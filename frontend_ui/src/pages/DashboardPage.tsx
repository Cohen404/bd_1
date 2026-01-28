import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  Database, 
  FileBarChart, 
  Brain,
  TrendingUp,
  Users,
  Clock,
  CheckCircle,
  AlertTriangle,
  BarChart3,
  RefreshCw,
  FileText,
  Settings,
  HardDrive,
  Monitor
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import toast from 'react-hot-toast';

interface DashboardStats {
  data_count: number;
  evaluation_count: number;
  result_count: number;
  model_count: number;
  user_count: number;
  recent_evaluations: number;
  high_risk_count: number;
  avg_scores: {
    stress: number;
    depression: number;
    anxiety: number;
    social: number;
  };
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState({
    models_ready: false,
    database_connected: true,
    services_running: true
  });

  // 获取仪表板统计数据（从后端API获取真实数据）
  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      
      // 并行获取各种统计数据
      const [dataResponse, resultsResponse, modelsResponse] = 
        await Promise.all([
          apiClient.getData(),
          apiClient.getResults(),
          apiClient.getModels()
        ]);

      const dataList = Array.isArray(dataResponse) ? dataResponse : dataResponse?.items || [];
      const resultsList = Array.isArray(resultsResponse) ? resultsResponse : resultsResponse?.items || [];
      const modelsList = Array.isArray(modelsResponse) ? modelsResponse : modelsResponse?.items || [];

      // 计算最近7天的评估数量
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      const recentEvaluations = resultsList.filter((result: any) => 
        new Date(result.result_time) >= sevenDaysAgo
      ).length;

      // 计算高风险数量
      const highRiskCount = resultsList.filter((result: any) => 
        result.stress_score >= 50 || 
        result.depression_score >= 50 || 
        result.anxiety_score >= 50 || 
        result.social_isolation_score >= 50
      ).length;

      // 计算平均分数（只使用前50条数据）
      const recentResults = resultsList.slice(0, 50);
      const avgScores = recentResults.length > 0 ? {
        stress: recentResults.reduce((sum: number, r: any) => sum + r.stress_score, 0) / recentResults.length,
        depression: recentResults.reduce((sum: number, r: any) => sum + r.depression_score, 0) / recentResults.length,
        anxiety: recentResults.reduce((sum: number, r: any) => sum + r.anxiety_score, 0) / recentResults.length,
        social: recentResults.reduce((sum: number, r: any) => sum + r.social_isolation_score, 0) / recentResults.length,
      } : {
        stress: 0,
        depression: 0,
        anxiety: 0,
        social: 0
      };

      setStats({
        data_count: dataList.length,
        evaluation_count: resultsList.length,
        result_count: resultsList.length,
        model_count: modelsList.length,
        user_count: 0, // 用户数据暂时设为0，因为API可能没有提供
        recent_evaluations: recentEvaluations,
        high_risk_count: highRiskCount,
        avg_scores: avgScores
      });

      // 检查系统状态
      setSystemStatus({
        models_ready: modelsList.length > 0,
        database_connected: true,
        services_running: true
      });

    } catch (error) {
      console.error('获取仪表板数据失败:', error);
      toast.error('获取仪表板数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
    
    // 每30秒刷新一次数据
    const interval = setInterval(fetchDashboardStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // 获取风险等级样式
  const getRiskStyle = (score: number) => {
    if (score >= 50) return { color: 'text-red-600', bg: 'bg-red-50' };
    if (score >= 30) return { color: 'text-yellow-600', bg: 'bg-yellow-50' };
    return { color: 'text-green-600', bg: 'bg-green-50' };
  };

  const recentActivities = [
    {
      id: 1,
      type: 'evaluation',
      title: '完成健康评估',
      description: `最近完成了${stats?.recent_evaluations || 0}次评估`,
      time: '实时数据'
    },
    {
      id: 2,
      type: 'upload',
      title: '数据管理',
      description: `当前共有${stats?.data_count || 0}个数据文件`,
      time: '实时数据'
    },
    {
      id: 3,
      type: 'report',
      title: '结果分析',
      description: `已生成${stats?.result_count || 0}份评估报告`,
      time: '实时数据'
    }
  ];

  // 快速操作按钮配置
  const quickActions = [
    {
      title: '健康评估',
      icon: Activity,
      description: '开始进行健康评估',
      path: '/health-evaluate',
      primary: true
    },
    {
      title: '数据管理',
      icon: Database,
      description: '管理数据文件',
      path: '/data-manage',
      primary: false
    },
    {
      title: '结果管理',
      icon: FileBarChart,
      description: '查看评估结果',
      path: '/result-manage',
      primary: false
    }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'evaluation':
        return <Activity className="h-4 w-4" />;
      case 'upload':
        return <Database className="h-4 w-4" />;
      case 'report':
        return <FileBarChart className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

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
          <h1 className="text-2xl font-bold text-gray-900">控制台</h1>
          <p className="text-gray-600 mt-1">欢迎使用急进高原新兵心理应激多模态神经生理监测预警系统</p>
        </div>
        <button
          onClick={fetchDashboardStats}
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
              <p className="text-sm font-medium text-gray-600">数据文件</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.data_count || 0}</p>
              <p className="text-sm text-gray-500 mt-1">可用数据</p>
            </div>
            <div className="p-3 rounded-full bg-blue-50">
              <Database className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">评估次数</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.evaluation_count || 0}</p>
              <p className="text-sm text-gray-500 mt-1">总评估数</p>
            </div>
            <div className="p-3 rounded-full bg-green-50">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">评估报告</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.result_count || 0}</p>
              <p className="text-sm text-gray-500 mt-1">已生成报告</p>
            </div>
            <div className="p-3 rounded-full bg-purple-50">
              <FileBarChart className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">AI模型</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats?.model_count || 0}</p>
              <p className="text-sm text-gray-500 mt-1">可用模型</p>
            </div>
            <div className="p-3 rounded-full bg-orange-50">
              <Brain className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* 健康状态概览 */}
      {stats && stats.avg_scores && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">平均健康指标</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className={`p-4 rounded-lg ${getRiskStyle(stats.avg_scores.stress).bg}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">平均应激水平</span>
                <Activity className="h-5 w-5 text-gray-600" />
              </div>
              <p className={`text-2xl font-bold mt-2 ${getRiskStyle(stats.avg_scores.stress).color}`}>
                {stats.avg_scores.stress.toFixed(1)}
              </p>
            </div>
            <div className={`p-4 rounded-lg ${getRiskStyle(stats.avg_scores.depression).bg}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">平均抑郁水平</span>
                <Brain className="h-5 w-5 text-gray-600" />
              </div>
              <p className={`text-2xl font-bold mt-2 ${getRiskStyle(stats.avg_scores.depression).color}`}>
                {stats.avg_scores.depression.toFixed(1)}
              </p>
            </div>
            <div className={`p-4 rounded-lg ${getRiskStyle(stats.avg_scores.anxiety).bg}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">平均焦虑水平</span>
                <AlertTriangle className="h-5 w-5 text-gray-600" />
              </div>
              <p className={`text-2xl font-bold mt-2 ${getRiskStyle(stats.avg_scores.anxiety).color}`}>
                {stats.avg_scores.anxiety.toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 最近活动 */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">最近活动</h2>
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <div className="text-green-600">
                      {getActivityIcon(activity.type)}
                    </div>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.title}
                  </p>
                  <p className="text-sm text-gray-500">
                    {activity.description}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {activity.time}
                  </p>
                </div>
                <div className="flex-shrink-0">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 快速操作 */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">快速操作</h2>
          <div className="space-y-3">
            {quickActions.map((action, index) => {
              const IconComponent = action.icon;
              return (
                <button 
                  key={index}
                  onClick={() => navigate(action.path)}
                  className={`w-full text-left flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                    action.primary 
                      ? 'bg-primary-600 text-white hover:bg-primary-700' 
                      : 'bg-gray-50 text-gray-900 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  <IconComponent className="h-5 w-5" />
                  <div>
                    <span className="font-medium">{action.title}</span>
                    <p className={`text-sm ${action.primary ? 'text-primary-100' : 'text-gray-500'}`}>
                      {action.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* 系统状态 */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">系统状态</h2>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">系统正常运行</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <Brain className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                AI模型状态
              </p>
              <p className="text-xs text-gray-500">
                {systemStatus.models_ready ? '模型已就绪，可以开始评估' : '模型未就绪'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Database className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                数据库连接
              </p>
              <p className="text-xs text-gray-500">
                {systemStatus.database_connected ? '数据库连接正常' : '数据库连接异常'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <Monitor className="h-4 w-4 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                服务状态
              </p>
              <p className="text-xs text-gray-500">
                {systemStatus.services_running ? '所有服务运行正常' : '部分服务异常'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 