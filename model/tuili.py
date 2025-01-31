import os

import mne
import tensorflow as tf
import numpy as np
import pickle as pkl
import h5py
from PyQt5.QtCore import pyqtSignal, QThread
import traceback
from util.db_util import SessionClass
from sql_model.tb_model import Model


class EegModel(QThread):
    _rule = pyqtSignal(float)
    finished = pyqtSignal()
    
    # 静态变量用于存储预加载的模型
    _model = None
    
    @staticmethod
    def load_static_model():
        """
        静态方法，用于加载普通应激模型（model_type=0）
        Returns:
            bool: 加载是否成功
        """
        try:
            # 从数据库获取普通应激模型路径
            session = SessionClass()
            model_info = session.query(Model).filter(Model.model_type == 0).first()
            session.close()
            
            if not model_info:
                print("Error: No stress model found in database")
                return False
                
            # 加载模型
            EegModel._model = tf.keras.models.load_model(model_info.model_path, safe_mode=False)
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            traceback.print_exc()
            return False

    def __init__(self, data_path, model_path):
        """
        初始化EegModel类
        Args:
            data_path: 数据路径
            model_path: 模型路径
        """
        self.data_path = data_path
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
        # 添加模型实例变量
        self.model = None

    def get_data(self):
        num_of_data = 108
        files = os.listdir(self.data_path)

        # 定义一个函数，根据文件的扩展名返回一个排序键
        def sort_key(file_name):
            if file_name.endswith('.fif'):
                return 1
            elif file_name.endswith('.edf'):
                return 2
            elif file_name.endswith('.set'):
                return 3
            else:
                return 4  # 对于其他类型的文件，返回一个较大的值

        # 对文件列表进行排序
        files = sorted(files, key=sort_key)

        for file in files:
            file_path = os.path.join(self.data_path, file)
            file_name = os.path.basename(file_path)

            if file_name.endswith('.fif'):
                raw = mne.read_epochs(file_path)
                raw.load_data()
                exp_data = raw.get_data()
            elif file_name.endswith('.edf'):
                raw = mne.io.read_raw_edf(file_path)
                raw.load_data()
                exp_data = raw.get_data()
                segment_length = int(500 * 2)
                num_channels, num_samples = exp_data.shape
                segments = []

                for start in range(0, num_samples, segment_length):
                    end = start + segment_length
                    if end <= num_samples:
                        segment = exp_data[:, start:end]
                        segments.append(segment)

                exp_data = np.array(segments)
            elif file_name.endswith('.set'):
                raw = mne.io.read_epochs_eeglab(file_path)
                exp_data = raw.get_data()

            data = exp_data[-(num_of_data)::, ::, ::]
            N_tr, N_ch, T = data.shape
            data = data.reshape(N_tr, 1, N_ch, T)

            standarder = 'standarder'
            model_dir = os.path.dirname(self.model_path)
            print("model_dir", model_dir)
            dir_path = os.path.join(model_dir, standarder)
            print("dir_path" + dir_path)
            for j in range(N_ch):
                save_path = os.path.join(dir_path, f'std_{j}.pkl')
                print("save_path", save_path)
                with open(save_path, 'rb') as f:
                    scaler = pkl.load(f)
                data[:, 0, j, :] = scaler.transform(data[:, 0, j, :])

            return data

    def load_model(self):
        """
        加载模型并保存到实例变量中
        """
        try:
            self.model = tf.keras.models.load_model(self.model_path, safe_mode=False)
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def predict(self):
        """
        使用预加载的模型进行预测
        Returns:
            float: 预测结果
        """
        try:
            if EegModel._model is None:
                raise Exception("Model not loaded. Please call load_static_model() first.")
            
            X_test = self.get_data()
            y_pred = EegModel._model.predict(X_test)
            print('pred_argmax',y_pred.argmax(axis=-1))
            print('a',float(y_pred.argmax(axis=-1).sum()))
            print('b',len(y_pred.argmax(axis=-1)))
            num = float(y_pred.argmax(axis=-1).sum())/len(y_pred.argmax(axis=-1))
            print('numorig',num)
            return num
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            traceback.print_exc()
            return 0.0

    def run(self):
        result = self.predict()
        self._rule.emit(result)
        self.finished.emit()


if __name__ == "__main__":
    data_path = '../data/3_wangwu'
    model_list=['yingji','yiyu','jiaolv']
    for i in range(0,3):
        model_path = f'../model/{model_list[i]}/subject-1.keras'
        predictor = (EegModel(data_path, model_path))
        result = predictor.predict()
        print(result)
