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


def train_and_predict(train_set, dev_set, test_set, limit, input_dim, ft):
    # Create logdir name
    logdir = os.path.join("logs", "{}-{}".format(
        os.path.basename(globals().get("__file__", "notebook")),
        datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    ))
    print("limit",limit)
    # inputs = (keras.Input(shape=[limit, input_dim]), keras.Input(shape=[ft.get_dimension()]))
    input1 = keras.Input(shape=[limit, input_dim], name="in1")
    input_emb = keras.Input(shape=[ft.get_dimension()],  name="in2")

    hidden_emb = keras.layers.Dense(1200, activation="relu")(input_emb)
    dropout_emb = keras.layers.Dropout(0.5)(hidden_emb)
    hidden_emb2 = keras.layers.Dense(1200, activation="relu")(dropout_emb)
    dropout_emb2 = keras.layers.Dropout(0.5)(hidden_emb2)

    hidden1 = keras.layers.Conv1D(400, 3, padding="same", name="co1")(input1)
    hidden1 = keras.layers.BatchNormalization()(hidden1)
    hidden1 = keras.layers.ReLU()(hidden1)
    # hidden1 = keras.layers.Conv1D(300, 4, padding="same")(inputs)
    # hidden1 = keras.layers.BatchNormalization()(hidden1)
    # hidden1 = keras.layers.ReLU()(hidden1)
    hidden2 = keras.layers.Conv1D(300, 5, padding="same", name="co2")(input1)
    hidden2 = keras.layers.BatchNormalization()(hidden2)
    hidden2 = keras.layers.ReLU()(hidden2)
    # hidden3 = keras.layers.Conv1D(200, 6, padding="same")(inputs)
    # hidden3 = keras.layers.BatchNormalization()(hidden3)
    # hidden3 = keras.layers.ReLU()(hidden3)
    hidden4 = keras.layers.Conv1D(150, 7, padding="same", name="co4")(input1)
    hidden4 = keras.layers.BatchNormalization()(hidden4)
    hidden4 = keras.layers.ReLU()(hidden4)
    # hidden5 = keras.layers.Conv1D(50, 8, padding="same")(inputs)
    # hidden5 = keras.layers.BatchNormalization()(hidden5)
    # hidden5 = keras.layers.ReLU()(hidden5)
    # Merge the outputs
    # merged = keras.layers.concatenate([hidden1, hidden2,hidden3,hidden4,hidden5], axis=-1)
    merged = keras.layers.concatenate([hidden1, hidden2,hidden4], axis=-1)
    hidden21 = keras.layers.Conv1D(300, 1, padding="same", activation="relu")(merged)
    hidden21 = keras.layers.BatchNormalization()(hidden21)

    hidden22 = keras.layers.Conv1D(200, 2, padding="same", activation="relu")(merged)
    hidden22 = keras.layers.BatchNormalization()(hidden22)

    hidden23 = keras.layers.Conv1D(200, 3, padding="same", activation="relu")(merged)
    hidden23 = keras.layers.BatchNormalization()(hidden23)

    hidden24 = keras.layers.Conv1D(200, 4, padding="same", activation="relu")(merged)
    hidden24 = keras.layers.BatchNormalization()(hidden24)

    hidden25 = keras.layers.Conv1D(80, 5, padding="same", activation="relu")(merged)
    hidden25 = keras.layers.BatchNormalization()(hidden25)

    hidden26 = keras.layers.Conv1D(80, 6, padding="same", activation="relu")(merged)
    hidden26 = keras.layers.BatchNormalization()(hidden26)

    merged2 = keras.layers.concatenate([hidden21, hidden22, hidden23, hidden24,hidden25, hidden26], axis=-1)
    hidden31 = keras.layers.Conv1D(1, 1, padding="same", activation="relu")(merged)
    hidden31 = keras.layers.BatchNormalization()(hidden31)


    # merged_with_embeddings = keras.layers.concatenate([dropout1, dropout_emb], axis=-1)

    outputs = keras.layers.Dense(limit, activation="sigmoid")(hidden31)
    # Compile the model
    # lr_schedule = keras.optimizers.schedules.PolynomialDecay(
    #     initial_learning_rate=0.001,
    #     end_learning_rate=0.0002,
    #     decay_steps=1000,
    #     power=1.0,
    # )
    # Define the optimizer with the cosine decay learning rate schedule
    #optimizer = Adam(learning_rate=lr_schedule)
    optimizer = Adam()
    model = keras.Model(inputs=[input1, input_emb], outputs=outputs)
    model.compile(loss=keras.losses.BinaryCrossentropy(label_smoothing=0.1), optimizer=optimizer,
                  metrics=[keras.metrics.BinaryAccuracy(), keras.metrics.Precision(), keras.metrics.Recall()])
    model.summary(line_length=100)
    tb_callback = TorchTensorBoardCallback(logdir)
    model.fit([train_set[0], train_set[3]], train_set[1], epochs=20, batch_size=64, validation_batch_size=64,
              validation_data=([dev_set[0],dev_set[3]], dev_set[1]) , verbose=1, callbacks=[tb_callback])

    # Predict on the test set
    train_pred = (model.predict((train_set[0],train_set[3]), batch_size=64) > 0.5).astype(int)
    test_pred = (model.predict((test_set[0],test_set[3]), batch_size=64) > 0.5).astype(int)
    mlp_postprocessor.evaluate_predicted(train_set, test_set, train_pred, test_pred,logdir)
    mlp_postprocessor.save_sigmorphon_predicted(test_set, test_pred)