import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import Layout from '@/components/Layout/Layout';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import AdminDashboardPage from '@/pages/AdminDashboardPage';
import UserManagePage from '@/pages/UserManagePage';
import RoleManagePage from '@/pages/RoleManagePage';
import DataManagePage from '@/pages/DataManagePage';
import HealthEvaluatePage from '@/pages/HealthEvaluatePage';
import ResultManagePage from '@/pages/ResultManagePage';
import ModelManagePage from '@/pages/ModelManagePage';
import ParameterManagePage from '@/pages/ParameterManagePage';
import LogManagePage from '@/pages/LogManagePage';
import Loading from '@/components/Common/Loading';

// 受保护的路由组件
const ProtectedRoute: React.FC<{ 
  children: React.ReactNode; 
  requireAdmin?: boolean 
}> = ({ children, requireAdmin = false }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <Loading />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && user.user_type !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <Loading />;
  }

  return (
    <Routes>
      {/* 登录页面 */}
      <Route 
        path="/login" 
        element={
          user ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <LoginPage />
          )
        } 
      />

      {/* 受保护的路由 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* 默认重定向 */}
        <Route 
          index 
          element={
            <Navigate 
              to="/dashboard" 
              replace 
            />
          } 
        />

        {/* 普通用户路由 */}
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="health-evaluate" element={<HealthEvaluatePage />} />
        <Route path="data-manage" element={<DataManagePage />} />
        <Route path="result-manage" element={<ResultManagePage />} />

        {/* 管理员路由 */}
        <Route 
          path="admin" 
          element={
            <ProtectedRoute requireAdmin>
              <AdminDashboardPage />
            </ProtectedRoute>
          } 
        />
        
        {/* 管理员子功能路由 */}
        <Route 
          path="admin/user-manage" 
          element={
            <ProtectedRoute requireAdmin>
              <UserManagePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="admin/role-manage" 
          element={
            <ProtectedRoute requireAdmin>
              <RoleManagePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="admin/model-manage" 
          element={
            <ProtectedRoute requireAdmin>
              <ModelManagePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="admin/parameter-manage" 
          element={
            <ProtectedRoute requireAdmin>
              <ParameterManagePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="admin/log-manage" 
          element={
            <ProtectedRoute requireAdmin>
              <LogManagePage />
            </ProtectedRoute>
          } 
        />
      </Route>

      {/* 404页面 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App; 