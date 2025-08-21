#!/usr/bin/env python3
"""
数据库更新脚本 - 添加预处理和特征提取状态字段
该脚本为tb_data表添加processing_status和feature_status字段
"""

import sys
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加当前目录到路径，以便导入config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_database.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_database_connection():
    """创建数据库连接"""
    try:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        logger.error(f"创建数据库连接失败: {e}")
        raise

def check_column_exists(engine, table_name, column_name):
    """检查列是否已存在"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = '{column_name}'
            """))
            return result.scalar() > 0
    except Exception as e:
        logger.error(f"检查列 {column_name} 是否存在时出错: {e}")
        return False

def add_status_columns(engine):
    """为tb_data表添加状态字段"""
    try:
        with engine.connect() as connection:
            # 开始事务
            trans = connection.begin()
            
            try:
                # 检查并添加processing_status字段
                if not check_column_exists(engine, 'tb_data', 'processing_status'):
                    logger.info("添加processing_status字段...")
                    connection.execute(text("""
                        ALTER TABLE tb_data 
                        ADD COLUMN processing_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                    """))
                    
                    # 添加字段注释
                    connection.execute(text("""
                        COMMENT ON COLUMN tb_data.processing_status 
                        IS '预处理状态: pending/processing/completed/failed'
                    """))
                    logger.info("processing_status字段添加成功")
                else:
                    logger.info("processing_status字段已存在，跳过")
                
                # 检查并添加feature_status字段
                if not check_column_exists(engine, 'tb_data', 'feature_status'):
                    logger.info("添加feature_status字段...")
                    connection.execute(text("""
                        ALTER TABLE tb_data 
                        ADD COLUMN feature_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                    """))
                    
                    # 添加字段注释
                    connection.execute(text("""
                        COMMENT ON COLUMN tb_data.feature_status 
                        IS '特征提取状态: pending/processing/completed/failed'
                    """))
                    logger.info("feature_status字段添加成功")
                else:
                    logger.info("feature_status字段已存在，跳过")
                
                # 提交事务
                trans.commit()
                logger.info("数据库更新完成")
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                logger.error(f"添加字段时出错，已回滚: {e}")
                raise
                
    except SQLAlchemyError as e:
        logger.error(f"数据库操作失败: {e}")
        raise
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise

def update_existing_data_status(engine):
    """更新现有数据的状态 - 根据是否存在特征图片来判断"""
    try:
        with engine.connect() as connection:
            logger.info("开始更新现有数据的状态...")
            
            # 获取所有数据记录
            result = connection.execute(text("SELECT id, data_path FROM tb_data"))
            data_records = result.fetchall()
            
            updated_count = 0
            for record in data_records:
                data_id = record[0]
                data_path = record[1]
                
                if not data_path or not os.path.exists(data_path):
                    continue
                
                # 检查是否存在特征图片
                required_images = [
                    'time_过零率.png', 'time_方差.png', 'time_能量.png', 'time_差分.png',
                    'frequency_band_1.png', 'frequency_band_2.png', 'frequency_band_3.png',
                    'frequency_band_4.png', 'frequency_band_5.png',
                    'frequency_wavelet.png', 'differential_entropy.png',
                    'Theta.png', 'Alpha.png', 'Beta.png', 'Gamma.png'
                ]
                
                # 检查当前目录或子目录中是否有所有图片
                has_all_images = False
                
                # 先检查当前目录
                if all(os.path.exists(os.path.join(data_path, img)) for img in required_images):
                    has_all_images = True
                else:
                    # 检查子目录
                    try:
                        for item in os.listdir(data_path):
                            item_path = os.path.join(data_path, item)
                            if os.path.isdir(item_path):
                                if all(os.path.exists(os.path.join(item_path, img)) for img in required_images):
                                    has_all_images = True
                                    break
                    except (OSError, PermissionError):
                        pass
                
                # 更新状态
                if has_all_images:
                    # 如果有所有图片，说明预处理和特征提取都已完成
                    connection.execute(text("""
                        UPDATE tb_data 
                        SET processing_status = 'completed', feature_status = 'completed'
                        WHERE id = :data_id
                    """), {"data_id": data_id})
                    updated_count += 1
                    logger.info(f"数据ID {data_id} 状态已更新为已完成")
                else:
                    # 如果没有图片，保持默认的pending状态
                    logger.info(f"数据ID {data_id} 保持待处理状态")
            
            connection.commit()
            logger.info(f"状态更新完成，共更新了 {updated_count} 条记录")
            
    except Exception as e:
        logger.error(f"更新现有数据状态时出错: {e}")
        raise

def main():
    """主函数"""
    logger.info("开始数据库更新...")
    
    try:
        # 创建数据库连接
        engine = create_database_connection()
        logger.info("数据库连接成功")
        
        # 添加状态字段
        add_status_columns(engine)
        
        # 更新现有数据的状态
        update_existing_data_status(engine)
        
        logger.info("数据库更新全部完成")
        
    except Exception as e:
        logger.error(f"数据库更新失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
 