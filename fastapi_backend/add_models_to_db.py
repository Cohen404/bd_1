import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models import Model
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_models_to_database():
    """
    将模型添加到数据库中
    """
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 获取项目根目录路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 定义模型列表
        models_to_add = [
            {
                'model_type': 0,  # 普通应激模型
                'model_path': os.path.join(project_root, 'original_application', 'model', 'yingji', 'subject-1_yingji_quantized.tflite'),
                'description': '普通应激模型（INT8量化）'
            },
            {
                'model_type': 1,  # 抑郁评估模型
                'model_path': os.path.join(project_root, 'original_application', 'model', 'yiyu', 'subject-1 yiyu.keras'),
                'description': '抑郁评估模型'
            },
            {
                'model_type': 2,  # 焦虑评估模型
                'model_path': os.path.join(project_root, 'original_application', 'model', 'jiaolv', 'subject-1jiaolv.keras'),
                'description': '焦虑评估模型'
            }
        ]
        
        # 检查并添加模型
        for model_info in models_to_add:
            model_type = model_info['model_type']
            model_path = model_info['model_path']
            description = model_info['description']
            
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                logger.warning(f"模型文件不存在，跳过: {model_path}")
                continue
            
            # 检查数据库中是否已存在该类型的模型
            existing_model = db.query(Model).filter(Model.model_type == model_type).first()
            
            if existing_model:
                logger.info(f"模型类型 {model_type} 已存在，更新路径: {existing_model.model_path}")
                existing_model.model_path = model_path
                existing_model.create_time = datetime.now()
            else:
                # 创建新模型记录
                new_model = Model(
                    model_type=model_type,
                    model_path=model_path,
                    create_time=datetime.now()
                )
                db.add(new_model)
                logger.info(f"添加新模型: {description} -> {model_path}")
        
        # 提交更改
        db.commit()
        logger.info("模型添加/更新成功！")
        
        # 显示所有模型
        logger.info("\n当前数据库中的所有模型:")
        all_models = db.query(Model).all()
        for model in all_models:
            model_type_name = {
                0: '普通应激模型',
                1: '抑郁评估模型',
                2: '焦虑评估模型',
                3: '社交孤立评估模型'
            }.get(model.model_type, f'未知类型({model.model_type})')
            logger.info(f"  - {model_type_name}: {model.model_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"添加模型到数据库时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("开始添加模型到数据库...")
    success = add_models_to_database()
    if success:
        logger.info("操作完成！")
    else:
        logger.error("操作失败！")
        sys.exit(1)
