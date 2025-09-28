import React, { useState } from 'react';
import { Brain, User, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useForm } from 'react-hook-form';
import { LoginRequest } from '@/types';
import toast from 'react-hot-toast';

// ===== 纯前端演示模式 - 特殊标记 =====
// 此文件已修改为纯前端演示模式，不需要后端API
// 支持两个固定账户：admin/admin123 和 user/user123
// ============================================

const LoginPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoading } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginRequest>();

  const onSubmit = async (data: LoginRequest) => {
    try {
      // ===== 纯前端演示模式 - 特殊标记 =====
      // 直接调用修改后的login函数，不需要后端API
      const success = await login(data);
      if (success) {
        // 登录成功，useAuth hook会处理跳转
        console.log('登录成功，等待跳转...');
      }
      // ============================================
    } catch (error) {
      console.error('登录失败:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-background to-blue-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo和标题 */}
        <div className="text-center">
          <div className="mx-auto w-20 h-20 bg-gradient-to-br from-primary-600 to-primary-700 rounded-full flex items-center justify-center shadow-lg">
            <Brain className="h-10 w-10 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            北京健康评估系统
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            基于EEG数据的心理健康评估平台
          </p>
        </div>

        {/* 登录表单 */}
        <div className="card rounded-xl p-8">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label htmlFor="username" className="label">
                用户名
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('username', {
                    required: '请输入用户名',
                    minLength: { value: 2, message: '用户名至少2个字符' }
                  })}
                  type="text"
                  className="input pl-10"
                  placeholder="请输入用户名"
                />
              </div>
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.username.message}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="label">
                密码
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('password', {
                    required: '请输入密码',
                    minLength: { value: 6, message: '密码至少6个字符' }
                  })}
                  type={showPassword ? 'text' : 'password'}
                  className="input pl-10 pr-10"
                  placeholder="请输入密码"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary w-full py-3 text-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                    <span>登录中...</span>
                  </div>
                ) : (
                  '登录'
                )}
              </button>
            </div>
          </form>

          {/* 默认账号提示 */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="text-sm font-medium text-blue-900 mb-2">默认登录账号：</h4>
            <div className="text-sm text-blue-800 space-y-1">
              <p><span className="font-medium">管理员：</span>admin / admin123</p>
              <p><span className="font-medium">普通用户：</span>user / user123</p>
            </div>
          </div>
        </div>

        {/* 版权信息 */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            © 2024 北京健康评估系统 v1.0.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 