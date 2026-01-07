import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models as db_models
from auth import hash_password
import logging
from datetime import datetime
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_data():
    db = SessionLocal()
    try:
        # 创建默认角色
        admin_role = db.query(db_models.Role).filter(db_models.Role.role_name == "admin").first()
        if not admin_role:
            admin_role = db_models.Role(
                role_name="admin",
                description="系统管理员"
            )
            db.add(admin_role)
            logger.info("创建管理员角色")
        
        user_role = db.query(db_models.Role).filter(db_models.Role.role_name == "user").first()
        if not user_role:
            user_role = db_models.Role(
                role_name="user",
                description="普通用户"
            )
            db.add(user_role)
            logger.info("创建普通用户角色")
        
        db.commit()
        
        # 创建默认管理员用户
        admin_user = db.query(db_models.User).filter(db_models.User.username == "admin").first()
        if not admin_user:
            admin_user = db_models.User(
                user_id=str(uuid.uuid4()),
                username="admin",
                password=hash_password("admin123"),
                email="admin@bj-health.com",
                user_type="admin",
                created_at=datetime.now()
            )
            db.add(admin_user)
            db.commit()
            
            # 关联管理员角色
            user_role_rel = db_models.UserRole(
                user_id=admin_user.user_id,
                role_id=admin_role.role_id
            )
            db.add(user_role_rel)
            logger.info("创建默认管理员用户: admin/admin123")
        
        # 创建基本权限
        permissions = [
            ("user_read", "用户信息读取", "user", "read"),
            ("user_write", "用户信息修改", "user", "write"),
            ("data_read", "数据读取", "data", "read"),
            ("data_write", "数据修改", "data", "write"),
            ("model_read", "模型读取", "model", "read"),
            ("model_write", "模型修改", "model", "write"),
            ("result_read", "结果读取", "result", "read"),
            ("result_write", "结果修改", "result", "write"),
            ("admin_all", "系统管理", "system", "admin"),
        ]
        
        for perm_name, desc, resource, action in permissions:
            existing_perm = db.query(db_models.Permission).filter(
                db_models.Permission.permission_name == perm_name
            ).first()
            if not existing_perm:
                permission = db_models.Permission(
                    permission_name=perm_name,
                    description=desc,
                    resource=resource,
                    action=action
                )
                db.add(permission)
                logger.info(f"创建权限: {perm_name}")
        
        db.commit()
        
        # 为管理员角色分配所有权限
        all_permissions = db.query(db_models.Permission).all()
        existing_role_perms = db.query(db_models.RolePermission).filter(
            db_models.RolePermission.role_id == admin_role.role_id
        ).all()
        existing_perm_ids = {rp.permission_id for rp in existing_role_perms}
        
        for permission in all_permissions:
            if permission.permission_id not in existing_perm_ids:
                role_permission = db_models.RolePermission(
                    role_id=admin_role.role_id,
                    permission_id=permission.permission_id
                )
                db.add(role_permission)
        
        db.commit()
        logger.info("初始数据创建完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建初始数据失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()