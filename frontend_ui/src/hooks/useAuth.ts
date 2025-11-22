import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, LoginRequest } from '@/types';
// ===== 纯前端演示模式 - 特殊标记 =====
// 注释掉后端API相关导入，使用localStorage存储
// import { apiClient } from '@/utils/api';
import {
  getCurrentUser,
  setCurrentUser,
  removeToken,
  removeCurrentUser,
} from '@/utils/auth';
import { LocalStorageManager, STORAGE_KEYS, DataOperations, initializeDemoData, User as LocalUser } from '@/utils/localStorage';
import toast from 'react-hot-toast';
// ============================================

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
      
      // ===== 纯前端演示模式 - 特殊标记 =====
      // 检查本地是否有用户信息，不需要后端验证
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
      // ============================================
      
      /* 原有的API验证代码（已注释 - 纯前端演示模式）
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
      
      // ===== 纯前端演示模式 - 特殊标记 =====
      // 使用localStorage进行用户认证
      const { username, password } = credentials;
      
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 从localStorage获取用户数据
      const users = LocalStorageManager.get<LocalUser[]>(STORAGE_KEYS.USERS, []);
      const account = users.find(
        user => user.username === username && user.password === password
      );
      
      if (account) {
        // 更新最后登录时间
        DataOperations.updateUserLastLogin(account.username);
        
        // 添加登录日志
        DataOperations.addLog('USER_LOGIN', 'AUTH_MODULE', `用户 ${account.username} 登录成功`, account.username, account.id.toString());
        
        // 构建用户信息（转换为前端User类型）
        const userData: User = {
          user_id: account.id.toString(),
          username: account.username,
          user_type: account.role as 'admin' | 'user',
          created_at: account.created_at,
        };
        
        // 保存用户信息
        setUser(userData);
        setCurrentUser(userData);
        
        toast.success(`${account.role === 'admin' ? '管理员' : '用户'}登录成功`);
        
        // 根据用户类型跳转到不同页面
        setTimeout(() => {
          // 所有用户都跳转到 dashboard
          navigate('/dashboard', { replace: true });
        }, 100);
        
        return true;
      } else {
        // 添加登录失败日志
        DataOperations.addLog('LOGIN_FAILED', 'AUTH_MODULE', `用户 ${username} 登录失败`, 'system', '0');
        toast.error('用户名或密码错误');
        return false;
      }
      // ============================================
      
      /* 原有的API调用代码（已注释 - 纯前端演示模式）
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
    // 添加登出日志
    if (user) {
      DataOperations.addLog('USER_LOGOUT', 'AUTH_MODULE', `用户 ${user.username} 登出`, user.username, user.user_id);
    }
    
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
      // 直接进行认证检查，不要预先设置用户状态
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