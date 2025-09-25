import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, LoginRequest } from '@/types';
import { apiClient } from '@/utils/api';
import {
  getCurrentUser,
  setCurrentUser,
  setToken,
  removeToken,
  removeCurrentUser,
  isAuthenticated,
} from '@/utils/auth';
import toast from 'react-hot-toast';

export interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<boolean>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  checkAuth: () => Promise<boolean>;
}

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // 检查认证状态
  const checkAuth = async (): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // 检查本地是否有用户信息
      const currentUser = getCurrentUser();
      if (!currentUser) {
        setUser(null);
        // 如果当前不在登录页，则跳转到登录页
        if (window.location.pathname !== '/login') {
          navigate('/login', { replace: true });
        }
        return false;
      }

      // 直接使用本地存储的用户信息
      setUser(currentUser);
      return true;
      
      /* 原有的API验证代码（已注释）
      // 检查本地是否有认证信息
      if (!isAuthenticated()) {
        setUser(null);
        // 如果当前不在登录页，则跳转到登录页
        if (window.location.pathname !== '/login') {
          navigate('/login', { replace: true });
        }
        return false;
      }

      // 验证token有效性并获取用户信息
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      setCurrentUser(userData);
      return true;
      */
    } catch (error) {
      console.error('认证检查失败:', error);
      // 认证失败，清除本地数据
      removeToken();
      removeCurrentUser();
      setUser(null);
      
      // 如果当前不在登录页，则跳转到登录页
      if (window.location.pathname !== '/login') {
        navigate('/login', { replace: true });
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 登录
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // 硬编码的登录逻辑
      const { username, password } = credentials;
      
      // 检查管理员账号
      if (username === 'admin' && password === 'admin123') {
        // 构建管理员用户信息
        const userData: User = {
          user_id: 'admin-001',
          username: 'admin',
          user_type: 'admin',
          created_at: new Date().toISOString(),
        };
        
        // 保存用户信息（不需要真实的token）
        setUser(userData);
        setCurrentUser(userData);
        
        toast.success('管理员登录成功');
        
        // 跳转到管理员页面
        setTimeout(() => {
          navigate('/admin', { replace: true });
        }, 100);
        
        return true;
      }
      
      // 检查普通用户账号
      if (username === 'user' && password === 'user123') {
        // 构建普通用户信息
        const userData: User = {
          user_id: 'user-001',
          username: 'user',
          user_type: 'user',
          created_at: new Date().toISOString(),
        };
        
        // 保存用户信息（不需要真实的token）
        setUser(userData);
        setCurrentUser(userData);
        
        toast.success('用户登录成功');
        
        // 跳转到用户页面
        setTimeout(() => {
          navigate('/dashboard', { replace: true });
        }, 100);
        
        return true;
      }
      
      // 如果用户名密码不匹配，显示错误信息
      toast.error('用户名或密码错误');
      return false;
      
      /* 原有的API调用代码（已注释）
      const response = await apiClient.login(credentials);
      
      if (response.access_token) {
        // 保存token
        setToken(response.access_token);
        
        // 构建用户信息
        const userData: User = {
          user_id: response.user_id,
          username: response.username,
          user_type: response.user_type,
          created_at: new Date().toISOString(),
        };
        
        // 保存用户信息
        setUser(userData);
        setCurrentUser(userData);
        
        toast.success('登录成功');
        
        // 使用setTimeout确保状态更新完成后再跳转
        setTimeout(() => {
          // 根据用户类型跳转到不同页面
          if (response.user_type === 'admin') {
            navigate('/admin', { replace: true });
          } else {
            navigate('/dashboard', { replace: true });
          }
        }, 100);
        
        return true;
      }
      
      return false;
      */
    } catch (error: any) {
      console.error('登录失败:', error);
      toast.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 登出
  const logout = () => {
    removeToken();
    removeCurrentUser();
    setUser(null);
    toast.success('已安全退出');
    navigate('/login');
  };

  // 更新用户信息
  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      setCurrentUser(updatedUser);
    }
  };

  // 初始化时检查认证状态
  useEffect(() => {
    const initAuth = async () => {
      const currentUser = getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
      }
      
      // 验证认证状态
      await checkAuth();
    };
    
    initAuth();
  }, []);

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    updateUser,
    checkAuth,
  };
}; 