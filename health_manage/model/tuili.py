import os

import mne
import tensorflow as tf
import numpy as np
import pickle as pkl
import h5py
from PyQt5.QtCore import pyqtSignal,QThread


class EegModel(QThread):
    _rule = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, data_path, model_path):
        self.data_path = data_path + '/fif.fif'
        super(EegModel, self).__init__()
        self.model_path = model_path
        self.n_channels = 59
        self.in_samples = 1000
        self.n_classes = 2
        self.classes_labels = ['Control', 'EXP']
        self.dataset_conf = {
            'name': 'eegdata',
            'n_classes': self.n_classes,
            'cl_labels': self.classes_labels,
            'n_sub': 1,
            'n_channels': self.n_channels,
            'in_samples': self.in_samples,
            'data_path': self.data_path,
            'isStandard': True,
            'LOSO': True
        }
    def get_data(self):
        num_of_data = 108

        raw = mne.read_epochs(self.data_path)
        raw.load_data()
        exp_data = raw.get_data()
        data = exp_data[-(num_of_data)::, ::, ::]
        N_tr, N_ch, T = data.shape
        data = data.reshape(N_tr, 1, N_ch, T)

        # Standardization
        dir_path = '../standarder'
        for j in range(N_ch):
            save_path = os.path.join(dir_path,f'std_{j}.pkl')
            with open(save_path,'rb') as f:
                scaler = pkl.load(f)
            data[:, 0, j, :] = scaler.transform(data[:, 0, j, :])

        return data

    def load_model(self):
        return tf.keras.models.load_model(self.model_path,safe_mode=False)

    def predict(self):
        X_test = self.get_data()
        model = self.load_model()
        y_pred = model.predict(X_test)
        num = y_pred.argmax(axis=-1).sum()

        if num > 54:
            return 1
        else:
            return 0

    def run(self):
        result = self.predict()
        self._rule.emit(result)
        self.finished.emit()
        self.predict()
        self.finished.emit()


if __name__ == "__main__":

    data_path = '../data/3_wangwu/preprocessing-yiyu-2.fif'
    model_path = 'subject-1.keras'
    predictor = (EegModel(data_path, model_path))
    result = predictor.predict()
    print(result)
