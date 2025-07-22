from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib

import models
from database import get_db
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 定义Token模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_type: str
    username: str

# 定义TokenData模型
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    user_type: Optional[str] = None

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# 验证密码
def verify_password(plain_password, hashed_password):
    # 使用SHA256哈希算法
    hashed_input = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_input == hashed_password

# 获取用户
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 获取用户权限
def get_user_permissions(db: Session, user_id: str):
    # 通过用户ID查询用户角色
    user_roles = db.query(models.UserRole).filter(models.UserRole.user_id == user_id).all()
    
    # 获取角色ID列表
    role_ids = [ur.role_id for ur in user_roles]
    
    # 通过角色ID查询角色权限
    role_permissions = db.query(models.RolePermission).filter(
        models.RolePermission.role_id.in_(role_ids)
    ).all()
    
    # 获取权限ID列表
    permission_ids = [rp.permission_id for rp in role_permissions]
    
    # 通过权限ID查询权限
    permissions = db.query(models.Permission).filter(
        models.Permission.permission_id.in_(permission_ids)
    ).all()
    
    return permissions

# 验证用户
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        user_type: str = payload.get("user_type")
        if username is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, user_id=user_id, user_type=user_type)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    return user

# 获取当前活跃用户
async def get_current_active_user(current_user = Depends(get_current_user)):
    return current_user

# 检查是否为管理员
async def check_admin_permission(current_user = Depends(get_current_user)):
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

# 检查用户是否有特定权限
def has_permission(user_id: str, resource: str, action: str, db: Session):
    permissions = get_user_permissions(db, user_id)
    for permission in permissions:
        if permission.resource == resource and permission.action == action:
            return True
    return False

# 检查特定权限的依赖项
def check_permission(resource: str, action: str):
    async def check_permission_dependency(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.user_type == "admin":
            return current_user
            
        if has_permission(current_user.user_id, resource, action, db):
            return current_user
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要 {resource}:{action} 权限"
        )
    return check_permission_dependency 