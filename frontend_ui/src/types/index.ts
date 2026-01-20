import React from 'react';

// 用户相关类型
export interface User {
  user_id: string;
  username: string;
  email?: string;
  phone?: string;
  user_type: 'admin' | 'user';
  last_login?: string;
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  username: string;
  password: string;
  email?: string;
  phone?: string;
  user_type?: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  phone?: string;
  password?: string;
  user_type?: string;
}

// 认证相关类型
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  user_type: string;
  username: string;
}

// 角色权限类型
export interface Role {
  role_id: number;
  role_name: string;
  description?: string;
  created_at: string;
}

export interface Permission {
  permission_id: number;
  permission_name: string;
  description?: string;
  resource: string;
  action: string;
}

// 数据相关类型
export interface Data {
  id: number;
  personnel_id: string;
  data_path: string;
  upload_user: number;
  personnel_name: string;
  user_id: string;
  upload_time: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  feature_status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface DataCreate {
  personnel_id: string;
  personnel_name: string;
  file: File;
}

// 预处理进度类型
export interface PreprocessProgress {
  data_id: number;
  personnel_name: string;
  processing_status: string;
  feature_status: string;
  progress_percentage: number;
  message: string;
}

// 批量预处理请求类型
export interface BatchPreprocessRequest {
  data_ids: number[];
}

// 健康评估结果类型
export interface Result {
  id: number;
  stress_score: number;
  depression_score: number;
  anxiety_score: number;
  social_isolation_score: number;
  user_id: string;
  username: string;
  data_id?: number;
  report_path?: string;
  result_time: string;
  overall_risk_level: string;
  recommendations: string;
  personnel_id?: string;
  personnel_name?: string;
  active_learned?: boolean;
}

export interface HealthEvaluateRequest {
  data_id: number;
}

export interface BatchHealthEvaluateRequest {
  data_ids: number[];
}

// AI模型类型
export interface Model {
  id: number;
  model_type: number;
  model_path: string;
  create_time: string;
}

// 参数类型
export interface Parameter {
  id: number;
  param_name: string;
  param_value: string;
  param_type: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface SystemParam {
  id: number;
  param_name: string;
  param_value: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

// API响应类型
export interface APIResponse<T = any> {
  success?: boolean;
  data?: T;
  message?: string;
  detail?: string;
  items?: T[];
  total?: number;
  page?: number;
  size?: number;
}

// 表格和分页类型
export interface PaginationParams {
  page?: number;
  size?: number;
  search?: string;
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  title: string;
  render?: (value: any, record: T) => React.ReactNode;
  width?: number;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
}

// 健康评估分数等级
export type ScoreLevel = 'low' | 'medium' | 'high';

export interface HealthScore {
  stress_score: number;
  depression_score: number;
  anxiety_score: number;
  social_isolation_score: number;
}

// 图表数据类型
export interface ChartData {
  name: string;
  value: number;
  level: ScoreLevel;
}

// 导航菜单类型
export interface MenuItem {
  key: string;
  label: string;
  icon: React.ComponentType<any>;
  path: string;
  permission?: string;
  children?: MenuItem[];
}

// 统计数据类型
export interface DashboardStats {
  totalUsers: number;
  totalData: number;
  totalResults: number;
  totalModels: number;
  recentEvaluations: number;
  activeUsers: number;
}

// 文件上传类型
export interface UploadFile {
  uid: string;
  name: string;
  status: 'uploading' | 'done' | 'error' | 'removed';
  percent?: number;
  response?: any;
  error?: any;
}

// 搜索和过滤类型
export interface SearchFilters {
  keyword?: string;
  dateRange?: [string, string];
  userType?: string;
  status?: string;
}

// 日志类型
export interface LogEntry {
  timestamp: string;
  level: string;
  username: string;
  message: string;
}

// 通用状态类型
export interface LoadingState {
  [key: string]: boolean;
}

export interface ErrorState {
  [key: string]: string | null;
} 