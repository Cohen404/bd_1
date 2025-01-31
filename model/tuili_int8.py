import os
import mne
import tensorflow as tf
import numpy as np
import pickle as pkl
import traceback
import warnings
from PyQt5.QtCore import pyqtSignal, QThread
from util.db_util import SessionClass
from sql_model.tb_model import Model
import logging

# 过滤sklearn的版本警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='Trying to unpickle estimator StandardScaler')

# 配置GPU内存增长
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # 设置GPU显存用量按需使用
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        # 指定使用第一块GPU
        tf.config.experimental.set_visible_devices(gpus[0], 'GPU')
        logging.info(f"成功配置GPU: {gpus[0].name}")
    except RuntimeError as e:
        logging.error(f"GPU配置错误: {str(e)}")

class EegModelInt8(QThread):
    """
    支持INT8量化模型的脑电模型推理类
    继承自QThread以支持异步处理
    """
    _rule = pyqtSignal(float)
    finished = pyqtSignal()
    
    # 静态变量用于存储预加载的模型
    _interpreter = None
    _input_details = None
    _output_details = None
    _gpu_initialized = False
    
    @staticmethod
    def _init_gpu():
        """
        初始化GPU配置
        """
        if not EegModelInt8._gpu_initialized:
            try:
                # 检查GPU可用性
                gpus = tf.config.experimental.list_physical_devices('GPU')
                if gpus:
                    logging.info(f"检测到可用GPU: {[gpu.name for gpu in gpus]}")
                    # 设置GPU显存按需增长
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    # 指定使用第一块GPU
                    tf.config.experimental.set_visible_devices(gpus[0], 'GPU')
                    logging.info(f"已配置GPU: {gpus[0].name}")
                    EegModelInt8._gpu_initialized = True
                else:
                    logging.warning("未检测到可用GPU，将使用CPU进行推理")
            except RuntimeError as e:
                logging.error(f"GPU配置错误: {str(e)}")
    
    @staticmethod
    def load_static_model():
        """
        静态方法，用于加载INT8量化后的普通应激模型（model_type=0）
        Returns:
            bool: 加载是否成功
        """
        try:
            # 如果模型已经加载，直接返回True
            if EegModelInt8._interpreter is not None:
                logging.info("模型已经加载，无需重复加载")
                return True
                
            logging.info("开始加载INT8量化模型...")
            
            # 初始化GPU
            EegModelInt8._init_gpu()
            
            # 从数据库获取普通应激模型路径
            session = SessionClass()
            model_info = session.query(Model).filter(Model.model_type == 0).first()
            session.close()
            
            if not model_info:
                logging.error("数据库中未找到普通应激模型(model_type=0)")
                return False
            
            if not os.path.exists(model_info.model_path):
                logging.error(f"模型文件不存在: {model_info.model_path}")
                return False
                
            logging.info(f"开始加载模型文件: {model_info.model_path}")
            
            try:
                # 在GPU上下文中加载模型
                with tf.device('/GPU:0'):
                    # 直接加载量化模型
                    EegModelInt8._interpreter = tf.lite.Interpreter(
                        model_path=model_info.model_path,
                        num_threads=4
                    )
                    
                    # 分配张量
                    EegModelInt8._interpreter.allocate_tensors()
                    
                    # 获取输入输出细节
                    input_details = EegModelInt8._interpreter.get_input_details()
                    output_details = EegModelInt8._interpreter.get_output_details()
                    
                    # 验证模型输入输出
                    if not input_details or not output_details:
                        logging.error("模型输入输出信息获取失败")
                        return False
                    
                    # 记录模型信息
                    input_shape = input_details[0]['shape']
                    input_type = input_details[0]['dtype']
                    output_shape = output_details[0]['shape']
                    output_type = output_details[0]['dtype']
                    
                    logging.info(f"模型输入shape: {input_shape}, 类型: {input_type}")
                    logging.info(f"模型输出shape: {output_shape}, 类型: {output_type}")
                    
                    # 保存输入输出信息
                    EegModelInt8._input_details = input_details
                    EegModelInt8._output_details = output_details
                    
                    logging.info("模型加载成功并已放置在GPU上")
                    return True
                
            except Exception as e:
                logging.error(f"模型加载失败: {str(e)}")
                logging.error(traceback.format_exc())
                return False
            
        except Exception as e:
            logging.error(f"模型加载过程中发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return False

    def __init__(self, data_path, model_path):
        """
        初始化EegModelInt8类
        Args:
            data_path: 数据路径
            model_path: 模型路径
        """
        super(EegModelInt8, self).__init__()
        self.data_path = data_path
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
        """
        获取并预处理数据
        Returns:
            np.ndarray: 预处理后的数据
        """
        try:
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
                    return 4

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
                dir_path = os.path.join(model_dir, standarder)
                
                for j in range(N_ch):
                    save_path = os.path.join(dir_path, f'std_{j}.pkl')
                    with open(save_path, 'rb') as f:
                        scaler = pkl.load(f)
                    data[:, 0, j, :] = scaler.transform(data[:, 0, j, :])

                return data

        except Exception as e:
            logging.error(f"Error in get_data: {str(e)}")
            logging.error(traceback.format_exc())
            return None

    def predict(self):
        """
        使用INT8量化模型进行预测
        Returns:
            float: 预测结果
        """
        try:
            if EegModelInt8._interpreter is None:
                raise Exception("Model not loaded. Please call load_static_model() first.")
            
            X_test = self.get_data()
            if X_test is None:
                raise Exception("Failed to get test data")
            
            # 获取输入输出细节
            input_details = EegModelInt8._input_details
            output_details = EegModelInt8._output_details
            
            # 准备输入数据
            input_scale = input_details[0]['quantization'][0]
            input_zero_point = input_details[0]['quantization'][1]
            
            # 在GPU上进行数据处理
            with tf.device('/GPU:0'):
                # 量化输入数据
                X_test_quantized = X_test / input_scale + input_zero_point
                X_test_quantized = X_test_quantized.astype(np.int8)
                
                # 获取批次大小
                batch_size = X_test_quantized.shape[0]
                all_predictions = []
                
                # 逐个样本进行预测
                for i in range(batch_size):
                    # 提取单个样本
                    single_sample = X_test_quantized[i:i+1]  # 保持维度为(1, 1, 59, 1000)
                    
                    # 设置输入张量
                    EegModelInt8._interpreter.set_tensor(input_details[0]['index'], single_sample)
                    
                    # 运行推理
                    EegModelInt8._interpreter.invoke()
                    
                    # 获取输出
                    output_data = EegModelInt8._interpreter.get_tensor(output_details[0]['index'])
                    
                    # 反量化输出数据
                    output_scale = output_details[0]['quantization'][0]
                    output_zero_point = output_details[0]['quantization'][1]
                    pred = (output_data.astype(np.float32) - output_zero_point) * output_scale
                    all_predictions.append(pred)
                
                # 合并所有预测结果
                y_pred = np.vstack(all_predictions)
            
            # 计算结果
            num = float(y_pred.argmax(axis=-1).sum()) / len(y_pred.argmax(axis=-1))
            logging.info(f'Prediction result: {num}')
            return num
            
        except Exception as e:
            logging.error(f"Error during prediction: {str(e)}")
            logging.error(traceback.format_exc())
            return 0.0

    def run(self):
        """
        QThread的运行方法
        """
        try:
            result = self.predict()
            self._rule.emit(result)
        except Exception as e:
            logging.error(f"Error in run: {str(e)}")
            logging.error(traceback.format_exc())
        finally:
            self.finished.emit()

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试代码
    data_path = '../data/3_wangwu'
    model_list=['yingji','yiyu','jiaolv']
    
    # 只测试普通应激模型
    model_path = f'../model/{model_list[0]}/subject-1_quantized.tflite'
    predictor = EegModelInt8(data_path, model_path)
    
    # 加载静态模型
    if EegModelInt8.load_static_model():
        result = predictor.predict()
        print(f"预测结果: {result}")
    else:
        print("模型加载失败") 