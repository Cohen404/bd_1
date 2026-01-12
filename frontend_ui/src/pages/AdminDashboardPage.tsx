import React, { useState, useEffect } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { 
  Users, 
  Shield, 
  Brain, 
  Settings, 
  FileText, 
  Activity,
  TrendingUp,
  CheckCircle,
  RefreshCw
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import toast from 'react-hot-toast';

interface AdminStats {
  totalUsers: number;
  totalRoles: number;
  totalModels: number;
  totalLogs: number;
  systemHealth: number;
  recentActivities: number;
}

const AdminDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAdminStats = async () => {
    try {
      setLoading(true);
      const adminStats = await apiClient.getAdminStats();
      setStats(adminStats);
    } catch (error) {
      console.error('获取管理员数据失败:', error);
      toast.error('获取管理员数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminStats();
  }, []);

  const adminMenuItems = [
    {
      title: '用户管理',
      icon: Users,
      description: '管理系统用户账户',
      path: '/admin/user-manage',
      color: 'bg-blue-50 text-blue-600',
      iconColor: 'text-blue-600'
    },
    {
      title: '角色管理',
      icon: Shield,
      description: '配置用户角色权限',
      path: '/admin/role-manage',
      color: 'bg-green-50 text-green-600',
      iconColor: 'text-green-600'
    },
    {
      title: '模型管理',
      icon: Brain,
      description: '管理AI评估模型',
      path: '/admin/model-manage',
      color: 'bg-purple-50 text-purple-600',
      iconColor: 'text-purple-600'
    },
    {
      title: '参数管理',
      icon: Settings,
      description: '配置系统参数',
      path: '/admin/parameter-manage',
      color: 'bg-orange-50 text-orange-600',
      iconColor: 'text-orange-600'
    },
    {
      title: '日志管理',
      icon: FileText,
      description: '查看系统日志',
      path: '/admin/log-manage',
      color: 'bg-gray-50 text-gray-600',
      iconColor: 'text-gray-600'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-primary-600 border-t-transparent"></div>
        <span className="ml-3 text-gray-500">加载数据中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 欢迎信息 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">管理员控制台</h1>
          <p className="text-gray-600 mt-1">系统管理和监控中心</p>
        </div>
        <button
          onClick={fetchAdminStats}
          disabled={loading}
          className="btn btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>刷新数据</span>
        </button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">用户总数</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.totalUsers || 0}</p>
              <p className="text-sm text-gray-500 mt-1">注册用户</p>
            </div>
            <div className="p-3 rounded-full bg-blue-50">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">角色数量</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.totalRoles || 0}</p>
              <p className="text-sm text-gray-500 mt-1">权限角色</p>
            </div>
            <div className="p-3 rounded-full bg-green-50">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">AI模型</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.totalModels || 0}</p>
              <p className="text-sm text-gray-500 mt-1">可用模型</p>
            </div>
            <div className="p-3 rounded-full bg-purple-50">
              <Brain className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">系统日志</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.totalLogs || 0}</p>
              <p className="text-sm text-gray-500 mt-1">日志条目</p>
            </div>
            <div className="p-3 rounded-full bg-orange-50">
              <FileText className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* 系统状态 */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">系统状态</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">系统健康度</p>
              <p className="text-xs text-gray-500">{stats?.systemHealth || 0}% 正常运行</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Activity className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">最近活动</p>
              <p className="text-xs text-gray-500">{stats?.recentActivities || 0} 次操作</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <TrendingUp className="h-4 w-4 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">性能指标</p>
              <p className="text-xs text-gray-500">响应时间 &lt; 200ms</p>
            </div>
          </div>
        </div>
      </div>

      {/* 管理功能 */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">管理功能</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {adminMenuItems.map((item, index) => {
            const IconComponent = item.icon;
            return (
              <button
                key={index}
                onClick={() => navigate(item.path)}
                className={`p-4 rounded-lg border-2 border-dashed border-gray-200 hover:border-gray-300 transition-colors text-left ${item.color} hover:shadow-md`}
              >
                <div className="flex items-center space-x-3">
                  <IconComponent className={`h-6 w-6 ${item.iconColor}`} />
                  <div>
                    <h3 className="font-medium">{item.title}</h3>
                    <p className="text-sm opacity-75">{item.description}</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 快速操作 */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
        <div className="flex flex-wrap gap-3">
          <button 
            onClick={() => navigate('/admin/user-manage')}
            className="btn btn-primary"
          >
            <Users className="h-4 w-4 mr-2" />
            添加用户
          </button>
          <button 
            onClick={() => navigate('/admin/role-manage')}
            className="btn btn-secondary"
          >
            <Shield className="h-4 w-4 mr-2" />
            配置权限
          </button>
          <NavLink
            to="/admin/model-manage"
            className="btn btn-secondary"
            style={{ cursor: 'pointer', zIndex: 10 }}
          >
            <Brain className="h-4 w-4 mr-2" />
            更新模型
          </NavLink>
          <button 
            onClick={() => navigate('/admin/log-manage')}
            className="btn btn-secondary"
          >
            <FileText className="h-4 w-4 mr-2" />
            查看日志
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage; 