import os
import datetime
import random

import torch
from torch.utils.data import Dataset, DataLoader
from unidecode import unidecode
from mlp_segmentation import mlp_postprocessor

os.environ.setdefault("KERAS_BACKEND", "torch")  # Use PyTorch backend unless specified otherwise
import numpy as np
import sklearn
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


def train_and_predict(train_set, val_set, test_set, limit, char_index_dict, embedd_dim=26, augment_chance=0.15):
    # Create logdir name
    logdir = os.path.join("logs", "{}-{}".format(
        os.path.basename(globals().get("__file__", "notebook")),
        datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    ))

    class TorchDataset(Dataset):
        def __init__(self, data, augmentation_fn=None):
            self.char_arrays = data[0]
            self.labels = data[1]
            # self.words = data[2]
            self.augmentation_fn = augmentation_fn

        def __len__(self):
            return len(self.char_arrays)

        def __getitem__(self, idx):
            char_array = self.char_arrays[idx]
            label = self.labels[idx]
            if self.augmentation_fn:
                char_array = self.augmentation_fn(char_array)
            return char_array, label

        def augmentation_fn(char_array):
            if True or random.random() < augment_chance:
                idx = random.randint(0, len(char_array) - 1)
                char_array[idx] = char_index_dict['#']
            return char_array

    # train_dataset = TorchDataset(train_set, augmentation_fn=TorchDataset.augmentation_fn)
    train_dataset = TorchDataset(train_set)
    test_dataset = TorchDataset(test_set)

    train_batches = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=False)
    test_batches = torch.utils.data.DataLoader(test_dataset, batch_size=64, shuffle=False)

    input_layer = keras.Input(shape=[limit])
    inputs = keras.layers.Embedding(input_dim=len(char_index_dict), output_dim=embedd_dim)(input_layer)

    hidden1 = keras.layers.Conv1D(300, 4, padding="same")(inputs)
    hidden1 = keras.layers.BatchNormalization()(hidden1)
    hidden1 = keras.layers.ReLU()(hidden1)
    hidden2 = keras.layers.Conv1D(300, 5, padding="same")(inputs)
    hidden2 = keras.layers.BatchNormalization()(hidden2)
    hidden2 = keras.layers.ReLU()(hidden2)
    hidden3 = keras.layers.Conv1D(200, 6, padding="same")(inputs)
    hidden3 = keras.layers.BatchNormalization()(hidden3)
    hidden3 = keras.layers.ReLU()(hidden3)
    hidden4 = keras.layers.Conv1D(150, 7, padding="same")(inputs)
    hidden4 = keras.layers.BatchNormalization()(hidden4)
    hidden4 = keras.layers.ReLU()(hidden4)
    hidden5 = keras.layers.Conv1D(50, 8, padding="same")(inputs)
    hidden5 = keras.layers.BatchNormalization()(hidden5)
    hidden5 = keras.layers.ReLU()(hidden5)
    # Merge the outputs
    merged = keras.layers.concatenate([hidden1, hidden2,hidden3,hidden4,hidden5], axis=-1)
    hidden21 = keras.layers.Conv1D(300, 2, padding="same", activation="relu")(merged)
    hidden21 = keras.layers.BatchNormalization()(hidden21)
    hidden22 = keras.layers.Conv1D(200, 3, padding="same", activation="relu")(merged)
    hidden22 = keras.layers.BatchNormalization()(hidden22)
    hidden23 = keras.layers.Conv1D(50, 4, padding="same", activation="relu")(merged)
    hidden23 = keras.layers.BatchNormalization()(hidden23)
    merged = keras.layers.concatenate([hidden21, hidden22, hidden23], axis=-1)
    hidden = keras.layers.Flatten()(merged)
    hidden1 = keras.layers.Dense(1500, activation="relu")(hidden)
    dropout1 = keras.layers.Dropout(0.5)(hidden1)
    hidden2 = keras.layers.Dense(1500, activation="relu")(dropout1)
    dropout2 = keras.layers.Dropout(0.3)(hidden2)
    outputs = keras.layers.Dense(limit, activation="sigmoid")(dropout2)


    # Compile the model
    model = keras.Model(inputs=input_layer, outputs=outputs)
    model.compile(loss=keras.losses.BinaryCrossentropy(label_smoothing=0.1), optimizer=Adam(),
                  metrics=[keras.metrics.BinaryAccuracy(), keras.metrics.Precision(), keras.metrics.Recall()])
    model.summary(line_length=100)
    tb_callback = TorchTensorBoardCallback(logdir)
    model.fit(train_batches, epochs=2, batch_size=64, validation_data=test_batches ,validation_batch_size=64, verbose=1, callbacks=[tb_callback])

    # Predict on the test set
    train_pred = (model.predict(train_batches, batch_size=64) > 0.5).astype(int)
    test_pred = (model.predict(test_batches, batch_size=64) > 0.5).astype(int)
    mlp_postprocessor.evaluate_predicted(train_set, test_set, train_pred, test_pred)

