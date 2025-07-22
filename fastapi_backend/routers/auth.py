from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from database import get_db
from auth import authenticate_user, create_access_token, Token
from config import ACCESS_TOKEN_EXPIRE_MINUTES
import schemas

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口，获取访问令牌
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logging.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.user_id, "user_type": user.user_type},
        expires_delta=access_token_expires
    )
    
    logging.info(f"User {user.username} logged in successfully")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_type": user.user_type,
        "username": user.username
    }

@router.post("/login", response_model=Token)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口，简化版
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        logging.warning(f"Failed login attempt for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.user_id, "user_type": user.user_type},
        expires_delta=access_token_expires
    )
    
    logging.info(f"User {user.username} logged in successfully")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_type": user.user_type,
        "username": user.username
    } 