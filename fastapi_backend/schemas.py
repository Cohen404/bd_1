from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# 用户相关模型
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    user_type: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    user_type: Optional[str] = None

class UserInDB(UserBase):
    user_id: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

# 角色相关模型
class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None

class Role(RoleBase):
    role_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# 权限相关模型
class PermissionBase(BaseModel):
    permission_name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None

class Permission(PermissionBase):
    permission_id: int

    class Config:
        orm_mode = True

# 用户角色关联模型
class UserRoleBase(BaseModel):
    user_id: str
    role_id: int

class UserRoleCreate(UserRoleBase):
    pass

class UserRole(UserRoleBase):
    id: int

    class Config:
        orm_mode = True

# 角色权限关联模型
class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermission(RolePermissionBase):
    id: int

    class Config:
        orm_mode = True

# 数据相关模型
class DataBase(BaseModel):
    personnel_id: str
    data_path: str
    upload_user: int
    personnel_name: str
    user_id: str
    md5: Optional[str] = None

class DataCreate(DataBase):
    pass

class DataUpdate(BaseModel):
    personnel_id: Optional[str] = None
    data_path: Optional[str] = None
    upload_user: Optional[int] = None
    personnel_name: Optional[str] = None
    md5: Optional[str] = None

class Data(DataBase):
    id: int
    upload_time: datetime
    processing_status: str
    feature_status: str

    class Config:
        from_attributes = True

# 结果相关模型
class ResultBase(BaseModel):
    stress_score: float
    depression_score: float
    anxiety_score: float
    user_id: str
    data_id: Optional[int] = None
    report_path: Optional[str] = None
    personnel_id: Optional[str] = None
    personnel_name: Optional[str] = None
    active_learned: bool = False
    blood_oxygen: Optional[float] = None
    blood_pressure: Optional[str] = None
    md5: Optional[str] = None

class ResultCreate(ResultBase):
    pass

class ResultUpdate(BaseModel):
    stress_score: Optional[float] = None
    depression_score: Optional[float] = None
    anxiety_score: Optional[float] = None
    report_path: Optional[str] = None
    blood_oxygen: Optional[float] = None
    blood_pressure: Optional[str] = None
    md5: Optional[str] = None

class Result(ResultBase):
    id: int
    result_time: datetime

    class Config:
        orm_mode = True

# 模型相关模型
class ModelBase(BaseModel):
    model_type: int
    model_path: str

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    model_type: Optional[int] = None
    model_path: Optional[str] = None

class Model(ModelBase):
    id: int
    create_time: datetime

    class Config:
        orm_mode = True

# 参数相关模型
class ParameterBase(BaseModel):
    param_name: str
    param_value: str
    param_type: str
    description: Optional[str] = None

class ParameterCreate(ParameterBase):
    pass

class ParameterUpdate(BaseModel):
    param_name: Optional[str] = None
    param_value: Optional[str] = None
    param_type: Optional[str] = None
    description: Optional[str] = None

class Parameter(ParameterBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 系统参数相关模型
class SystemParamBase(BaseModel):
    param_name: str
    param_value: str
    description: Optional[str] = None

class SystemParamCreate(SystemParamBase):
    pass

class SystemParamUpdate(BaseModel):
    param_name: Optional[str] = None
    param_value: Optional[str] = None
    description: Optional[str] = None

class SystemParam(SystemParamBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# 登录请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

# 健康评估请求模型
class HealthEvaluateRequest(BaseModel):
    data_id: int

# 批量健康评估请求模型
class BatchHealthEvaluateRequest(BaseModel):
    data_ids: List[int] 

# 批量预处理请求模型
class BatchPreprocessRequest(BaseModel):
    data_ids: List[int]

# 预处理进度响应模型
class PreprocessProgress(BaseModel):
    data_id: int
    personnel_name: str
    processing_status: str
    feature_status: str
    progress_percentage: int
    message: str

# 预处理状态更新模型
class StatusUpdate(BaseModel):
    data_id: int
    processing_status: Optional[str] = None
    feature_status: Optional[str] = None

# 批量删除请求模型
class BatchDeleteRequest(BaseModel):
    data_ids: List[int]

# 批量上传响应模型
class BatchUploadResponse(BaseModel):
    success_count: int
    failed_count: int
    uploaded_data: List[Data]
    errors: List[str]

# 图像信息模型
class ImageInfo(BaseModel):
    image_type: str
    image_name: str
    image_path: str
    description: Optional[str] = None

# 图像查看请求模型
class ImageViewRequest(BaseModel):
    data_id: int
    image_type: str

# 结果导出请求模型
class ResultExportRequest(BaseModel):
    result_ids: List[int]
    export_format: str = "excel"  # excel, csv, pdf

# LED状态模型
class LEDStatus(BaseModel):
    stress_led: str  # "red", "gray"
    depression_led: str
    anxiety_led: str
    stress_score: float
    depression_score: float
    anxiety_score: float

# 评估状态模型
class EvaluationStatus(BaseModel):
    data_id: int
    status: str  # "pending", "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    message: Optional[str] = None
    result_id: Optional[int] = None

# 管理员统计模型
class AdminStats(BaseModel):
    totalUsers: int
    totalRoles: int
    totalModels: int
    totalLogs: int
    systemHealth: int
    recentActivities: int 