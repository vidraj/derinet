import os
import datetime

from unidecode import unidecode
from mlp_segmentation import mlp_postprocessor

os.environ.setdefault("KERAS_BACKEND", "torch")  # Use PyTorch backend unless specified otherwise
import keras
from keras.optimizers import Adam


class TorchTensorBoardCallback(keras.callbacks.Callback):
    def __init__(self, path):
        self._path = path
        self._writers = {}

    def writer(self, writer):
        if writer not in self._writers:
            import torch.utils.tensorboard
            self._writers[writer] = torch.utils.tensorboard.SummaryWriter(os.path.join(self._path, writer))
        return self._writers[writer]

    def add_logs(self, writer, logs, step):
        if logs:
            for key, value in logs.items():
                self.writer(writer).add_scalar(key, value, step)
            self.writer(writer).flush()

    def on_epoch_end(self, epoch, logs=None):
        if logs:
            if isinstance(getattr(self.model, "optimizer", None), keras.optimizers.Optimizer):
                logs = logs | {"learning_rate": keras.ops.convert_to_numpy(self.model.optimizer.learning_rate)}
            self.add_logs("train", {k: v for k, v in logs.items() if not k.startswith("val_")}, epoch + 1)
            self.add_logs("val", {k[4:]: v for k, v in logs.items() if k.startswith("val_")}, epoch + 1)


def train_and_predict(train_set, dev_set, test_set, limit, input_dim, embedd_dim=26):
    # Create logdir name
    logdir = os.path.join("logs", "{}-{}".format(
        datetime.datetime.now().strftime("%Y_%m_%d_%H-%M%S"),
        os.path.basename(globals().get("__file__", "notebook"))
    ))

    inputs = keras.Input(shape=[limit, input_dim])


    hidden1 = keras.layers.Conv1D(300, 2, padding="same")(inputs)
    hidden1 = keras.layers.BatchNormalization()(hidden1)
    hidden1 = keras.layers.ReLU()(hidden1)
    hidden2 = keras.layers.Conv1D(300, 3, padding="same")(inputs)
    hidden2 = keras.layers.BatchNormalization()(hidden2)
    hidden2 = keras.layers.ReLU()(hidden2)
    hidden3 = keras.layers.Conv1D(200, 4, padding="same")(inputs)
    hidden3 = keras.layers.BatchNormalization()(hidden3)
    hidden3 = keras.layers.ReLU()(hidden3)
    hidden4 = keras.layers.Conv1D(150, 5, padding="same")(inputs)
    hidden4 = keras.layers.BatchNormalization()(hidden4)
    hidden4 = keras.layers.ReLU()(hidden4)
    hidden5 = keras.layers.Conv1D(100, 6, padding="same")(inputs)
    hidden5 = keras.layers.BatchNormalization()(hidden5)
    hidden5 = keras.layers.ReLU()(hidden5)
    # Merge the outputs
    merged1 = keras.layers.concatenate([hidden1, hidden2, hidden3, hidden4, hidden5], axis=-1)

    hidden21 = keras.layers.Conv1D(300, 2, padding="same", activation="relu")(merged1)
    hidden21 = keras.layers.BatchNormalization()(hidden21)
    hidden21 = keras.layers.ReLU()(hidden21)
    hidden22 = keras.layers.Conv1D(300, 3, padding="same", activation="relu")(merged1)
    hidden22 = keras.layers.BatchNormalization()(hidden22)
    hidden22 = keras.layers.ReLU()(hidden22)
    hidden23 = keras.layers.Conv1D(200, 4, padding="same", activation="relu")(merged1)
    hidden23 = keras.layers.BatchNormalization()(hidden23)
    hidden23 = keras.layers.ReLU()(hidden23)
    merged2 = keras.layers.concatenate([hidden21, hidden22, hidden23], axis=-1)

    hidden3 = keras.layers.Conv1D(1000, 1, padding="same", activation="relu")(merged2)
    hidden3 = keras.layers.BatchNormalization()(hidden3)
    hidden3 = keras.layers.ReLU()(hidden3)
    hidden3 = keras.layers.Dropout(0.3)(hidden3)

    hidden4 = keras.layers.Conv1DTranspose(1000, 3, padding="same", activation="relu")(hidden3)
    hidden4 = keras.layers.BatchNormalization()(hidden4)
    hidden4 = keras.layers.ReLU()(hidden4)

    # added 1d convolution layer with relu and dropout -
    # TODO more training - 25 epochos
    hidden33 = keras.layers.Conv1D(1000, 1, padding="same", activation="relu")(hidden4)
    hidden33 = keras.layers.BatchNormalization()(hidden33)
    hidden33 = keras.layers.ReLU()(hidden33)
    hidden33 = keras.layers.Dropout(0.3)(hidden33)
    outputs = keras.layers.Conv1D(1, 1, padding="same", activation="sigmoid")(hidden33)

    lr_schedule = keras.optimizers.schedules.PolynomialDecay(
        initial_learning_rate=0.001,
        end_learning_rate=0.005,
        decay_steps=1000,
        power=1.0,
    )
    # Define the optimizer with the cosine decay learning rate schedule
    #optimizer = Adam(learning_rate=lr_schedule)
    optimizer = Adam()

    # Compile the model
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(loss=keras.losses.BinaryCrossentropy(label_smoothing=0.1), optimizer=optimizer,
                  metrics=[keras.metrics.BinaryAccuracy, keras.metrics.Precision(), keras.metrics.Recall()])
    model.summary(line_length=100)

    tb_callback = TorchTensorBoardCallback(logdir)
    model.fit(train_set[0], train_set[1], epochs=25, batch_size=64, validation_batch_size=64, validation_data=(dev_set[0], dev_set[1]) , verbose=1, callbacks=[tb_callback])

    # Predict on the test set
    train_pred = (model.predict(train_set[0], batch_size=64) > 0.5).astype(int)
    test_pred = (model.predict(test_set[0], batch_size=64) > 0.5).astype(int)
    train_pred = train_pred.squeeze(axis=-1)
    test_pred = test_pred.squeeze(axis=-1)


    mlp_postprocessor.evaluate_predicted(train_set, test_set, train_pred, test_pred,logdir)
    mlp_postprocessor.save_sigmorphon_predicted(test_set, test_pred)