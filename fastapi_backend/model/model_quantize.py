import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

import tensorflow as tf
import numpy as np
import logging
import traceback
from datetime import datetime
from util.db_util import SessionClass
from sql_model.tb_model import Model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(project_root, 'log', 'model_quantize.log')  # 添加日志文件路径
)

# 同时将日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

class ModelQuantizer:
    """
    模型量化器类，用于将模型进行INT8量化
    """
    def __init__(self):
        """
        初始化模型量化器
        """
        self.session = SessionClass()
        self.model = None
        self.model_path = None
        self.quantized_model = None
        
    def load_model(self):
        """
        从数据库加载model_type=0的模型
        Returns:
            bool: 加载是否成功
        """
        try:
            # 从数据库获取普通应激模型
            model_info = self.session.query(Model).filter(Model.model_type == 0).first()
            if not model_info:
                logging.error("未找到普通应激模型(model_type=0)")
                return False
                
            self.model_path = model_info.model_path
            if not os.path.exists(self.model_path):
                logging.error(f"模型文件不存在: {self.model_path}")
                return False
                
            # 加载模型
            self.model = tf.keras.models.load_model(self.model_path, safe_mode=False)
            logging.info(f"成功加载模型: {self.model_path}")
            return True
            
        except Exception as e:
            logging.error(f"加载模型时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return False
            
    def quantize_model(self):
        """
        对模型进行INT8量化
        Returns:
            bool: 量化是否成功
        """
        try:
            if self.model is None:
                logging.error("请先加载模型")
                return False
                
            logging.info("开始模型量化过程...")
            # 创建量化感知模型
            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            
            # 设置量化参数
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.int8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
            
            # 设置目标硬件加速
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
                tf.lite.OpsSet.TFLITE_BUILTINS,
                tf.lite.OpsSet.SELECT_TF_OPS
            ]
            
            # 设置代表性数据集用于量化校准
            def representative_dataset():
                logging.info("生成代表性数据集用于量化校准...")
                # 获取原始模型的输入shape
                input_shape = self.model.input_shape
                logging.info(f"原始模型输入shape: {input_shape}")
                
                for _ in range(100):
                    # 生成单个样本的数据
                    data = np.random.randn(1, 1, 59, 1000).astype(np.float32)
                    # 确保数据范围在合理区间内
                    data = np.clip(data, -10, 10)
                    yield [data]
                    
            converter.representative_dataset = representative_dataset
            
            # 执行量化
            logging.info("开始执行模型量化...")
            self.quantized_model = converter.convert()
            logging.info("模型量化完成")
            
            # 生成量化模型的保存路径
            model_dir = os.path.dirname(self.model_path)
            model_name = os.path.splitext(os.path.basename(self.model_path))[0]
            quantized_model_path = os.path.join(model_dir, f"{model_name}_quantized.tflite")
            
            # 保存量化后的模型
            with open(quantized_model_path, 'wb') as f:
                f.write(self.quantized_model)
                
            logging.info(f"量化模型已保存到: {quantized_model_path}")
            
            # 验证量化后的模型
            interpreter = tf.lite.Interpreter(model_path=quantized_model_path)
            interpreter.allocate_tensors()
            
            # 获取输入输出信息
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            logging.info(f"量化后模型输入信息: {input_details}")
            logging.info(f"量化后模型输出信息: {output_details}")
            
            # 更新数据库中的模型路径
            model = self.session.query(Model).filter(Model.model_type == 0).first()
            if model:
                old_path = model.model_path
                model.model_path = quantized_model_path
                self.session.commit()
                logging.info(f"数据库中的模型路径已更新: {old_path} -> {quantized_model_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"量化模型时发生错误: {str(e)}")
            logging.error(traceback.format_exc())
            return False
            
    def __del__(self):
        """
        析构函数，确保关闭数据库会话
        """
        if self.session:
            self.session.close()

def main():
    """
    主函数
    """
    try:
        quantizer = ModelQuantizer()
        
        # 加载模型
        if not quantizer.load_model():
            logging.error("加载模型失败")
            return
            
        # 量化模型
        if not quantizer.quantize_model():
            logging.error("量化模型失败")
            return
            
        logging.info("模型量化完成")
        
    except Exception as e:
        logging.error(f"执行过程中发生错误: {str(e)}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main() 