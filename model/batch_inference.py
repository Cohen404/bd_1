import os
import numpy as np
import tensorflow as tf
import logging
import traceback
import mne
import pickle as pkl
import warnings
from PyQt5.QtCore import QThread, pyqtSignal
from model.tuili_int8 import EegModelInt8
from model.result_processor import ResultProcessor

# 设置MNE日志级别为ERROR，只显示错误信息
mne.set_log_level('ERROR')

# 忽略特定的警告
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

# 过滤sklearn的版本警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='Trying to unpickle estimator StandardScaler')

class BatchInferenceModel(QThread):
    """
    批量推理模型类
    支持多个数据的批量推理，使用INT8量化模型
    """
    
    # 定义信号
    progress_updated = pyqtSignal(float)  # 进度更新信号
    batch_completed = pyqtSignal(list)    # 批次完成信号，发送结果列表
    error_occurred = pyqtSignal(str)      # 错误信号
    finished = pyqtSignal()               # 完成信号
    
    def __init__(self, data_paths, model_path, batch_size=40):
        """
        初始化批量推理模型
        
        Args:
            data_paths (list): 数据路径列表
            model_path (str): 模型路径
            batch_size (int): 批处理大小，默认为40
        """
        super(BatchInferenceModel, self).__init__()
        self.data_paths = data_paths
        self.model_path = model_path
        self.batch_size = batch_size
        self.n_channels = 59
        self.in_samples = 1000
        
    def preprocess_data(self, data_path):
        """
        预处理单个数据路径的数据
        
        Args:
            data_path (str): 数据路径
            
        Returns:
            np.ndarray: 预处理后的数据
        """
        try:
            num_of_data = 108
            files = os.listdir(data_path)
            
            # 定义文件排序键
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
                file_path = os.path.join(data_path, file)
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
            logging.error(f"数据预处理时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return None
    
    def run(self):
        """
        执行批量推理
        """
        try:
            # 确保模型已加载
            if not EegModelInt8._interpreter:
                if not EegModelInt8.load_static_model():
                    self.error_occurred.emit("模型加载失败")
                    return
            
            # 获取模型输入输出细节
            input_details = EegModelInt8._input_details
            output_details = EegModelInt8._output_details
            input_scale = input_details[0]['quantization'][0]
            input_zero_point = input_details[0]['quantization'][1]
            output_scale = output_details[0]['quantization'][0]
            output_zero_point = output_details[0]['quantization'][1]
            
            total_results = []
            total_paths = len(self.data_paths)
            
            # 批量处理数据
            for batch_start in range(0, total_paths, self.batch_size):
                batch_end = min(batch_start + self.batch_size, total_paths)
                batch_paths = self.data_paths[batch_start:batch_end]
                batch_results = []
                
                # 处理每个批次中的数据
                for data_path in batch_paths:
                    # 预处理数据
                    preprocessed_data = self.preprocess_data(data_path)
                    if preprocessed_data is None:
                        batch_results.append(0.0)
                        continue
                    
                    # 量化输入数据
                    data_quantized = preprocessed_data / input_scale + input_zero_point
                    data_quantized = data_quantized.astype(np.int8)
                    
                    # 获取样本数量
                    num_samples = data_quantized.shape[0] # 样本数量
                    predictions = []
                    
                    # 对每个样本进行推理
                    for i in range(num_samples):
                        single_sample = data_quantized[i:i+1]
                        EegModelInt8._interpreter.set_tensor(input_details[0]['index'], single_sample)
                        EegModelInt8._interpreter.invoke()
                        output_data = EegModelInt8._interpreter.get_tensor(output_details[0]['index'])
                        
                        # 反量化输出
                        pred = (output_data.astype(np.float32) - output_zero_point) * output_scale
                        predictions.append(pred)
                    
                    # 合并预测结果
                    y_pred = np.vstack(predictions)
                    
                    # 计算该数据的结果（1的占比）
                    result = float(y_pred.argmax(axis=-1).sum()) / len(y_pred.argmax(axis=-1))
                    
                    # 处理结果
                    final_result = ResultProcessor.process_result(0, result * 100, data_path)
                    batch_results.append(final_result)
                
                # 发送批次结果
                self.batch_completed.emit(batch_results)
                total_results.extend(batch_results)
                
                # 更新进度
                progress = (batch_end / total_paths) * 100
                self.progress_updated.emit(progress)
            
            # 发送完成信号
            self.finished.emit()
            
        except Exception as e:
            error_msg = f"批量推理过程中发生错误: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.error_occurred.emit(error_msg) 