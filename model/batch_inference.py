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
import sys
import pandas as pd

# 设置MNE日志级别为ERROR，只显示错误信息
mne.set_log_level('ERROR')

# 忽略特定的警告
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

# 过滤sklearn的版本警告
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='Trying to unpickle estimator StandardScaler')

sys.path.append('../')

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
    
    def __init__(self, data_paths, model_path):
        """
        初始化批量推理模型
        
        Args:
            data_paths: 数据路径列表
            model_path: 模型路径
        """
        super().__init__()
        self.data_paths = data_paths
        self.model_path = model_path
        self.results = []
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
    
    def calculate_scale_scores(self, data_path):
        """
        计算量表分数，只计算一次
        
        Args:
            data_path: 数据路径
            
        Returns:
            tuple: (焦虑量表分数, 抑郁量表分数) 如果无法计算则返回 (None, None)
        """
        try:
            # 读取量表数据
            lb_path = os.path.join(data_path, 'lb.csv')
            if not os.path.exists(lb_path):
                logging.info(f"量表文件不存在: {lb_path}")
                return None, None
                
            # 读取量表数据，没有header
            df = pd.read_csv(lb_path, header=None)
            if len(df) < 1:
                logging.info("量表数据为空")
                return None, None
            
            # 计算焦虑量表分数(前20列)
            anxiety_reverse_items = np.array([1, 2, 5, 8, 10, 11, 15, 16, 19, 20]) - 1
            first_20 = df.iloc[0, :20].values.astype(float)
            reverse_mask = np.zeros(20, dtype=bool)
            reverse_mask[anxiety_reverse_items] = True
            first_20[reverse_mask] = 5 - first_20[reverse_mask]
            anxiety_score = np.sum(first_20)
            
            # 计算抑郁量表分数(后20列)
            depression_reverse_items = np.array([2, 5, 6, 11, 12, 14, 16, 17, 18, 20]) - 1
            last_20 = df.iloc[0, 20:40].values.astype(float)
            reverse_mask = np.zeros(20, dtype=bool)
            reverse_mask[depression_reverse_items] = True
            last_20[reverse_mask] = 5 - last_20[reverse_mask]
            depression_score = np.sum(last_20) * 1.25
            
            logging.info(f"量表分数计算完成 - 焦虑量表: {anxiety_score:.2f}, 抑郁量表: {depression_score:.2f}")
            return anxiety_score, depression_score
            
        except Exception as e:
            logging.error(f"计算量表分数时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return None, None

    def calculate_final_score(self, model_score, scale_score, score_type):
        """
        根据模型分数和量表分数计算最终分数
        
        Args:
            model_score: 模型预测分数
            scale_score: 量表分数
            score_type: 分数类型 (1: 抑郁, 2: 焦虑)
            
        Returns:
            float: 计算后的最终分数
        """
        try:
            if scale_score is None:
                logging.info(f"量表分数不存在，使用模型分数的90%")
                return float(min(95, max(0, model_score)))
                
            if score_type == 1:  # 抑郁
                if scale_score < 53:
                    # 当量表分数<=53时，直接返回基于量表的计算结果
                    final_score = (scale_score / 53) * 50
                    logging.info(f"抑郁量表分数 < 53，使用量表计算结果: {final_score}")
                else:
                    # 当量表分数>53时，才结合模型分数
                    scale_factor = scale_score / 53.0 * 50
                    model_factor = model_score
                    final_score = (scale_factor + model_factor * 0.3)
                    logging.info(f"抑郁量表分数 >= 53，结合模型分数计算: {final_score}")
            else:  # 焦虑
                if scale_score < 48:
                    # 当量表分数<=48时，直接返回基于量表的计算结果
                    final_score = (scale_score / 48) * 50
                    logging.info(f"焦虑量表分数 < 48，使用量表计算结果: {final_score}")
                else:
                    # 当量表分数>48时，才结合模型分数
                    scale_factor = scale_score / 48.0 * 50
                    model_factor = model_score
                    final_score = (scale_factor + model_factor * 0.3)
                    logging.info(f"焦虑量表分数 >= 48，结合模型分数计算: {final_score}")
                    
            return float(min(95, max(0, final_score)))
            
        except Exception as e:
            logging.error(f"计算最终分数时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return model_score

    def run(self):
        """
        运行批量推理
        """
        try:
            # 确保模型已经加载
            if not EegModelInt8._interpreter:
                if not EegModelInt8.load_static_model():
                    self.error_occurred.emit("量化模型加载失败")
                    return

            total = len(self.data_paths)
            for i, data_path in enumerate(self.data_paths):
                try:
                    # 计算进度
                    progress = (i + 1) / total * 100
                    self.progress_updated.emit(progress)

                    # 计算量表分数
                    anxiety_score_lb, depression_score_lb = self.calculate_scale_scores(data_path)

                    # 使用模型进行推理
                    model = EegModelInt8(data_path, self.model_path)
                    model_result = model.predict() * 100
                    model_result = float(min(95, max(0, model_result)))

                    # 计算抑郁分数
                    depression_score = self.calculate_final_score(model_result, depression_score_lb, 1)
                    
                    # 计算焦虑分数
                    anxiety_score = self.calculate_final_score(model_result, anxiety_score_lb, 2)

                    # 将三个分数添加到结果列表
                    self.results.extend([model_result, depression_score, anxiety_score])

                except Exception as e:
                    logging.error(f"处理数据 {data_path} 时发生错误: {str(e)}")
                    logging.error(traceback.format_exc())
                    # 发生错误时，添加默认分数
                    self.results.extend([0, 0, 0])

            # 发送结果
            self.batch_completed.emit(self.results)
            self.finished.emit()

        except Exception as e:
            error_msg = f"批量推理过程中发生错误: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.error_occurred.emit(error_msg) 