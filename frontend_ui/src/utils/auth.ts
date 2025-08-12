import Cookies from 'js-cookie';
import { User } from '@/types';

// Token管理
export const getToken = (): string | undefined => {
  return Cookies.get('access_token');
};

export const setToken = (token: string): void => {
  Cookies.set('access_token', token, { expires: 7 }); // 7天过期
};

export const removeToken = (): void => {
  Cookies.remove('access_token');
};

// 用户信息管理
export const getCurrentUser = (): User | null => {
  const userStr = Cookies.get('user_info');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error('解析用户信息失败:', error);
      return null;
    }
  }
  return null;
};

export const setCurrentUser = (user: User): void => {
  Cookies.set('user_info', JSON.stringify(user), { expires: 7 });
};

export const removeCurrentUser = (): void => {
  Cookies.remove('user_info');
};

// 权限检查
export const hasPermission = (permission: string): boolean => {
  const user = getCurrentUser();
  if (!user) return false;
  
  // 管理员拥有所有权限
  if (user.user_type === 'admin') return true;
  
  // TODO: 这里需要根据实际的权限系统进行实现
  // 可以从后端获取用户的具体权限列表进行检查
  return false;
};

export const isAdmin = (): boolean => {
  const user = getCurrentUser();
  return user?.user_type === 'admin';
};

export const isAuthenticated = (): boolean => {
  const token = getToken();
  const user = getCurrentUser();
  return !!(token && user);
};

// 登出
export const logout = (): void => {
  removeToken();
  removeCurrentUser();
  window.location.href = '/login';
};

// 检查token是否过期（简单实现）
export const isTokenExpired = (): boolean => {
  const token = getToken();
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // JWT exp是秒，需要转换为毫秒
    return Date.now() >= exp;
  } catch (error) {
    console.error('解析token失败:', error);
    return true;
  }
};

// 用户类型枚举
export enum UserType {
  ADMIN = 'admin',
  USER = 'user'
}

// 权限常量（与后端保持一致）
export const PERMISSIONS = {
  USER_MANAGE: 'PERM_USER_MANAGE',
  ROLE_MANAGE: 'PERM_ROLE_MANAGE',
  DATA_MANAGE: 'PERM_DATA_MANAGE',
  RESULT_MANAGE: 'PERM_RESULT_MANAGE',
  MODEL_MANAGE: 'PERM_MODEL_MANAGE',
  STRESS_ASSESSMENT: 'PERM_STRESS_ASSESSMENT',
  PARAM_MANAGE: 'PERM_PARAM_MANAGE',
  LOG_MANAGE: 'PERM_LOG_MANAGE',
} as const;

export type PermissionType = typeof PERMISSIONS[keyof typeof PERMISSIONS]; 