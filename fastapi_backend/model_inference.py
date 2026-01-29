import os
import tensorflow as tf
import numpy as np
import pickle as pkl
import logging
import traceback
from sqlalchemy.orm import Session
import models as db_models
import asyncio
from concurrent.futures import ThreadPoolExecutor
import mne
import uuid
from datetime import datetime

# 创建一个线程池，用于处理计算密集型任务
executor = ThreadPoolExecutor(max_workers=3)  # 设置最大工作线程数

class EegModel:
    """
    EEG模型推理类，用于加载模型和进行预测
    """
    # 静态变量用于存储预加载的模型
    _models = {}
    
    @staticmethod
    async def load_static_model(model_type, db):
        """
        静态方法，用于加载模型
        Args:
            model_type: 模型类型 (0=应激, 1=抑郁, 2=焦虑)
            db: 数据库会话
        Returns:
            bool: 加载是否成功
        """
        try:
            # 避免重复加载
            if model_type in EegModel._models:
                return True
                
            # 从数据库获取模型路径
            model_info = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
            
            if not model_info:
                logging.error(f"错误：数据库中未找到类型为{model_type}的模型")
                return False
                
            # 异步加载模型
            loop = asyncio.get_event_loop()
            model = await loop.run_in_executor(
                executor,
                lambda: tf.keras.models.load_model(model_info.model_path, safe_mode=False)
            )
            
            # 存储到静态变量
            EegModel._models[model_type] = model
            logging.info(f"成功加载模型类型: {model_type}, 路径: {model_info.model_path}")
            return True
        except Exception as e:
            logging.error(f"模型加载错误: {str(e)}")
            logging.error(traceback.format_exc())
            return False

    def __init__(self, data_path, model_path):
        """
        初始化EegModel类
        Args:
            data_path: 数据路径
            model_path: 模型路径
        """
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
        self.model = None

    def get_data(self):
        """
        获取数据并进行预处理
        Returns:
            numpy.ndarray: 预处理后的数据
        """
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
            logging.info(f"model_dir: {model_dir}")
            dir_path = os.path.join(model_dir, standarder)
            logging.info(f"dir_path: {dir_path}")
            
            for j in range(N_ch):
                save_path = os.path.join(dir_path, f'std_{j}.pkl')
                logging.info(f"save_path: {save_path}")
                with open(save_path, 'rb') as f:
                    scaler = pkl.load(f)
                data[:, 0, j, :] = scaler.transform(data[:, 0, j, :])

            return data

    async def load_model(self):
        """
        加载模型并保存到实例变量中
        """
        try:
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                executor,
                lambda: tf.keras.models.load_model(self.model_path, safe_mode=False)
            )
            return True
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            logging.error(traceback.format_exc())
            return False

    async def predict(self, model_type):
        """
        使用预加载的模型进行预测
        Args:
            model_type: 模型类型 (0=应激, 1=抑郁, 2=焦虑)
        Returns:
            float: 预测结果
        """
        try:
            if model_type not in EegModel._models:
                raise Exception(f"Model type {model_type} not loaded. Please call load_static_model() first.")
            
            # 获取数据
            loop = asyncio.get_event_loop()
            X_test = await loop.run_in_executor(executor, self.get_data)
            
            # 预测
            model = EegModel._models[model_type]
            y_pred = await loop.run_in_executor(executor, lambda: model.predict(X_test))
            
            logging.info(f'pred_argmax: {y_pred.argmax(axis=-1)}')
            logging.info(f'a: {float(y_pred.argmax(axis=-1).sum())}')
            logging.info(f'b: {len(y_pred.argmax(axis=-1))}')
            
            num = float(y_pred.argmax(axis=-1).sum()) / len(y_pred.argmax(axis=-1))
            logging.info(f'numorig: {num}')
            
            return num
        except Exception as e:
            logging.error(f"预测错误: {str(e)}")
            logging.error(traceback.format_exc())
            return 0.0

class BatchInferenceModel:
    """批量推理模型类"""
    
    def __init__(self):
        """初始化批量推理模型"""
        self.models = {}  # 存储模型的字典
        
    async def load_models(self, db: Session):
        """
        加载所有类型的模型
        Args:
            db: 数据库会话
        Returns:
            bool: 是否成功加载所有模型
        """
        try:
            # 获取所有模型
            model_types = [0, 1, 2]  # 应激、抑郁、焦虑
            
            for model_type in model_types:
                # 从数据库获取模型信息
                model_info = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
                
                if not model_info:
                    logging.warning(f"未找到类型为{model_type}的模型")
                    continue
                
                # 加载模型
                await EegModel.load_static_model(model_type, db)
            
            return True
        except Exception as e:
            logging.error(f"加载模型时出错: {str(e)}")
            logging.error(traceback.format_exc())
            return False
    
    async def batch_predict(self, data_paths, db: Session):
        """
        对多个数据进行批量预测
        Args:
            data_paths: 数据路径列表 [(data_id, data_path), ...]
            db: 数据库会话
        Returns:
            list: 预测结果列表 [(data_id, stress_score, depression_score, anxiety_score), ...]
        """
        results = []
        
        try:
            # 确保模型已加载
            await self.load_models(db)
            
            # 对每个数据路径进行预测
            for data_id, data_path in data_paths:
                try:
                    logging.info(f"正在处理数据ID: {data_id}, 路径: {data_path}")
                    
                    # 获取每个模型的结果
                    model_paths = {}
                    for model_type in [0, 1, 2]:  # 应激、抑郁、焦虑
                        model_info = db.query(db_models.Model).filter(db_models.Model.model_type == model_type).first()
                        if model_info:
                            model_paths[model_type] = model_info.model_path
                    
                    # 存储各模型的预测结果
                    scores = {
                        "stress": 0.0,
                        "depression": 0.0,
                        "anxiety": 0.0
                    }
                    
                    # 并行运行所有模型预测
                    tasks = []
                    for model_type, model_path in model_paths.items():
                        model = EegModel(data_path, model_path)
                        tasks.append(model.predict(model_type))
                    
                    # 等待所有任务完成
                    scores_list = await asyncio.gather(*tasks)
                    
                    # 将结果赋值给相应的分数
                    for i, model_type in enumerate(model_paths.keys()):
                        if model_type == 0:
                            scores["stress"] = scores_list[i] * 100
                        elif model_type == 1:
                            scores["depression"] = scores_list[i] * 100
                        elif model_type == 2:
                            scores["anxiety"] = scores_list[i] * 100
                    
                    # 将结果添加到列表中
                    results.append((
                        data_id,
                        scores["stress"],
                        scores["depression"],
                        scores["anxiety"]
                    ))
                    
                    # 将结果保存到数据库
                    user_id = db.query(db_models.Data).filter(db_models.Data.id == data_id).first().user_id
                    
                    result = db_models.Result(
                        result_time=datetime.now(),
                        stress_score=scores["stress"],
                        depression_score=scores["depression"],
                        anxiety_score=scores["anxiety"],
                        user_id=user_id,
                        data_id=data_id
                    )
                    
                    db.add(result)
                    db.commit()
                    
                    logging.info(f"数据ID: {data_id} 的预测结果: {scores}")
                
                except Exception as e:
                    logging.error(f"处理数据ID: {data_id} 时出错: {str(e)}")
                    logging.error(traceback.format_exc())
                    # 继续处理下一个数据
                    continue
            
            return results
        
        except Exception as e:
            logging.error(f"批量预测时出错: {str(e)}")
            logging.error(traceback.format_exc())
            return results

class ResultProcessor:
    """结果处理器类，用于处理评估结果并生成报告"""
    
    def __init__(self, result_id, db: Session):
        """
        初始化结果处理器
        Args:
            result_id: 结果ID
            db: 数据库会话
        """
        self.result_id = result_id
        self.db = db
        self.result = None
        self.data = None
        self.user = None
        
    async def load_result(self):
        """
        加载结果数据
        Returns:
            bool: 是否成功加载
        """
        try:
            # 查询结果
            self.result = self.db.query(db_models.Result).filter(db_models.Result.id == self.result_id).first()
            
            if not self.result:
                logging.error(f"未找到ID为{self.result_id}的结果")
                return False
            
            # 查询相关数据
            if self.result.data_id:
                self.data = self.db.query(db_models.Data).filter(db_models.Data.id == self.result.data_id).first()
            
            # 查询用户
            self.user = self.db.query(db_models.User).filter(db_models.User.user_id == self.result.user_id).first()
            
            return True
        except Exception as e:
            logging.error(f"加载结果数据时出错: {str(e)}")
            logging.error(traceback.format_exc())
            return False
    
    def get_template_path(self, score_type):
        """
        根据分数类型获取模板路径
        Args:
            score_type: 分数类型 (anxiety/depression/stress/normal)
        Returns:
            str: 模板文件路径
        """
        # 模板目录
        template_dir = "templates"
        
        # 根据分数类型选择模板
        if score_type == "anxiety":
            return os.path.join(template_dir, "anxiety.txt")
        elif score_type == "depression":
            return os.path.join(template_dir, "depression.txt")
        elif score_type == "stress":
            return os.path.join(template_dir, "stress.txt")
        else:
            return os.path.join(template_dir, "normal.txt")
    
    def determine_score_type(self):
        """
        根据分数确定类型
        Returns:
            str: 分数类型 (anxiety/depression/stress/normal)
        """
        if not self.result:
            return "normal"
        
        # 获取分数
        anxiety = self.result.anxiety_score
        depression = self.result.depression_score
        stress = self.result.stress_score
        
        # 设置阈值
        threshold = 50
        
        # 确定类型
        if anxiety > threshold and anxiety >= depression and anxiety >= stress:
            return "anxiety"
        elif depression > threshold and depression >= anxiety and depression >= stress:
            return "depression"
        elif stress > threshold and stress >= anxiety and stress >= depression:
            return "stress"
        else:
            return "normal"
    
    async def generate_report(self):
        """
        生成评估报告
        Returns:
            str: 报告文件路径
        """
        try:
            # 加载结果数据
            if not await self.load_result():
                return None
            
            # 确定分数类型
            score_type = self.determine_score_type()
            
            # 获取模板路径
            template_path = self.get_template_path(score_type)
            
            # 检查模板是否存在
            if not os.path.exists(template_path):
                logging.error(f"模板文件不存在: {template_path}")
                return None
            
            # 创建结果目录
            results_dir = "data/results"
            os.makedirs(results_dir, exist_ok=True)
            
            # 生成报告文件名
            report_filename = f"report_{self.result_id}_{uuid.uuid4().hex[:8]}.txt"
            report_path = os.path.join(results_dir, report_filename)
            
            # 读取模板
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 替换变量
            report_content = template_content.replace('{stress_score}', f"{self.result.stress_score:.1f}")
            report_content = report_content.replace('{depression_score}', f"{self.result.depression_score:.1f}")
            report_content = report_content.replace('{anxiety_score}', f"{self.result.anxiety_score:.1f}")
            
            # 用户信息
            if self.user:
                report_content = report_content.replace('{username}', self.user.username)
            else:
                report_content = report_content.replace('{username}', "未知用户")
            
            # 评估时间
            report_content = report_content.replace('{evaluation_time}', self.result.result_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 更新数据库中的报告路径
            self.result.report_path = report_path
            self.db.commit()
            
            return report_path
        
        except Exception as e:
            logging.error(f"生成报告时出错: {str(e)}")
            logging.error(traceback.format_exc())
            return None 