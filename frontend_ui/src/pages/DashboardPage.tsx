import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  Database, 
  FileBarChart, 
  Brain,
  TrendingUp,
  Users,
  Clock,
  CheckCircle
} from 'lucide-react';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const stats = [
    {
      title: '我的数据',
      value: '12',
      icon: Database,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      trend: '+2 本月'
    },
    {
      title: '评估次数',
      value: '8',
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      trend: '+3 本月'
    },
    {
      title: '完成报告',
      value: '6',
      icon: FileBarChart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      trend: '+1 本月'
    },
    {
      title: '最新评分',
      value: '82',
      icon: Brain,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      trend: '健康状态'
    }
  ];

  const recentActivities = [
    {
      id: 1,
      type: 'evaluation',
      title: '完成健康评估',
      description: '对数据集 subject_001.csv 进行了应激评估',
      time: '2小时前'
    },
    {
      id: 2,
      type: 'upload',
      title: '数据上传成功',
      description: '上传了新的数据文件 subject_002.csv',
      time: '4小时前'
    },
    {
      id: 3,
      type: 'report',
      title: '报告生成完成',
      description: '健康评估报告已生成并可下载',
      time: '1天前'
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

  return (
    <div className="space-y-6">
      {/* 欢迎信息 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">控制台</h1>
        <p className="text-gray-600 mt-1">欢迎使用北京健康评估系统</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const IconComponent = stat.icon;
          return (
            <div key={index} className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  <p className="text-sm text-gray-500 mt-1">{stat.trend}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <IconComponent className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

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

      {/* 系统提示 */}
      <div className="card p-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center">
            <Brain className="h-4 w-4 text-blue-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">
              系统运行正常
            </p>
            <p className="text-xs text-gray-500">
              所有健康评估模型已就绪，可以开始评估
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 