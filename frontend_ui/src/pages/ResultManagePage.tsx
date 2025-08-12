import React, { useState, useEffect } from 'react';
import { 
  FileBarChart, 
  Download, 
  Search, 
  Filter, 
  RefreshCw, 
  Calendar,
  User,
  Eye,
  ChevronLeft,
  ChevronRight,
  FileText
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Result, User as UserType } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';

interface HealthStatus {
  stress: number;
  depression: number;
  anxiety: number;
  social_isolation: number;
}

interface FilterState {
  userType: string;
  userId: string;
  dateStart: string;
  dateEnd: string;
}

const ResultManagePage: React.FC = () => {
  const [results, setResults] = useState<Result[]>([]);
  const [users, setUsers] = useState<UserType[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentStatus, setCurrentStatus] = useState<HealthStatus>({
    stress: 0,
    depression: 0,
    anxiety: 0,
    social_isolation: 0
  });
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showVisualization, setShowVisualization] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    userType: 'all',
    userId: 'all',
    dateStart: '',
    dateEnd: ''
  });

  // 获取结果列表
  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getResults();
      const resultList = Array.isArray(response) ? response : response?.items || [];
      setResults(resultList);
      
      // 获取最新结果作为当前状态
      if (resultList.length > 0) {
        const latest = resultList[0];
        setCurrentStatus({
          stress: latest.stress_score || 0,
          depression: latest.depression_score || 0,
          anxiety: latest.anxiety_score || 0,
          social_isolation: latest.social_isolation_score || 0
        });
      }
    } catch (error) {
      console.error('获取结果列表失败:', error);
      toast.error('获取结果列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取用户列表
  const fetchUsers = async () => {
    try {
      const response = await apiClient.getUsers();
      setUsers(Array.isArray(response) ? response : response?.items || []);
    } catch (error) {
      console.error('获取用户列表失败:', error);
    }
  };

  useEffect(() => {
    fetchResults();
    fetchUsers();
  }, []);

  // 应用筛选
  const applyFilters = () => {
    let filtered = [...results];
    
    // 用户类型筛选
    if (filters.userType !== 'all') {
      const targetUserType = filters.userType === 'admin' ? 'admin' : 'user';
      const userIdsOfType = users
        .filter(user => user.user_type === targetUserType)
        .map(user => user.user_id);
      filtered = filtered.filter(result => userIdsOfType.includes(result.user_id));
    }
    
    // 特定用户筛选
    if (filters.userId !== 'all') {
      filtered = filtered.filter(result => result.user_id === filters.userId);
    }
    
    // 日期范围筛选
    if (filters.dateStart) {
      filtered = filtered.filter(result => 
        new Date(result.result_time) >= new Date(filters.dateStart)
      );
    }
    
    if (filters.dateEnd) {
      const endDate = new Date(filters.dateEnd);
      endDate.setHours(23, 59, 59, 999); // 包含整天
      filtered = filtered.filter(result => 
        new Date(result.result_time) <= endDate
      );
    }
    
    return filtered;
  };

  // 重置筛选
  const resetFilters = () => {
    setFilters({
      userType: 'all',
      userId: 'all',
      dateStart: '',
      dateEnd: ''
    });
  };

  // 导出结果
  const exportResults = () => {
    const filteredResults = applyFilters();
    const csvContent = "data:text/csv;charset=utf-8," + 
      "ID,用户名,评估时间,普通应激,抑郁,焦虑,社交孤立\n" +
      filteredResults.map(result => {
        const user = users.find(u => u.user_id === result.user_id);
        return `"${result.id}","${user?.username || '未知用户'}","${formatDateTime(result.result_time)}","${(result.stress_score * 100).toFixed(1)}%","${(result.depression_score * 100).toFixed(1)}%","${(result.anxiety_score * 100).toFixed(1)}%","${(result.social_isolation_score * 100).toFixed(1)}%"`;
      }).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `评估结果_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('结果导出成功');
  };

  // 获取状态颜色和标签
  const getStatusInfo = (score: number) => {
    let color = 'bg-green-500';
    let textColor = 'text-green-600';
    
    if (score >= 0.7) {
      color = 'bg-red-500';
      textColor = 'text-red-600';
    } else if (score >= 0.4) {
      color = 'bg-yellow-500';
      textColor = 'text-yellow-600';
    }
    
    return { color, textColor, percentage: (score * 100).toFixed(1) };
  };

  const filteredResults = applyFilters();

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">结果管理</h1>
        <p className="text-gray-600 mt-1">查看和管理健康评估结果，导出评估报告</p>
      </div>

      {/* 顶部状态显示区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 当前评估结果 */}
        <div className="card p-6 bg-primary-50">
          <h2 className="text-lg font-semibold text-gray-900 text-center mb-6">当前评估结果</h2>
          
          <div className="space-y-4">
            {/* 普通应激 */}
            <div className="flex items-center justify-between p-3 bg-white rounded-lg">
              <div className="flex items-center space-x-3">
                <div 
                  className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.stress).color}`}
                />
                <span className="font-medium">普通应激</span>
              </div>
              <span className={`font-bold ${getStatusInfo(currentStatus.stress).textColor}`}>
                {getStatusInfo(currentStatus.stress).percentage}%
              </span>
            </div>

            {/* 抑郁状态 */}
            <div className="flex items-center justify-between p-3 bg-white rounded-lg">
              <div className="flex items-center space-x-3">
                <div 
                  className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.depression).color}`}
                />
                <span className="font-medium">抑郁状态</span>
              </div>
              <span className={`font-bold ${getStatusInfo(currentStatus.depression).textColor}`}>
                {getStatusInfo(currentStatus.depression).percentage}%
              </span>
            </div>

            {/* 焦虑状态 */}
            <div className="flex items-center justify-between p-3 bg-white rounded-lg">
              <div className="flex items-center space-x-3">
                <div 
                  className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.anxiety).color}`}
                />
                <span className="font-medium">焦虑状态</span>
              </div>
              <span className={`font-bold ${getStatusInfo(currentStatus.anxiety).textColor}`}>
                {getStatusInfo(currentStatus.anxiety).percentage}%
              </span>
            </div>

            {/* 社交孤立 */}
            <div className="flex items-center justify-between p-3 bg-white rounded-lg">
              <div className="flex items-center space-x-3">
                <div 
                  className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.social_isolation).color}`}
                />
                <span className="font-medium">社交孤立</span>
              </div>
              <span className={`font-bold ${getStatusInfo(currentStatus.social_isolation).textColor}`}>
                {getStatusInfo(currentStatus.social_isolation).percentage}%
              </span>
            </div>
          </div>
        </div>

        {/* 数据可视化 */}
        <div className="card p-6 bg-primary-50">
          <h2 className="text-lg font-semibold text-gray-900 text-center mb-4">数据可视化</h2>
          
          {/* EEG特征图显示区域 */}
          <div className="bg-white rounded-lg p-4 min-h-[200px] flex items-center justify-center border-2 border-dashed border-gray-300 mb-4">
            {showVisualization ? (
              <div className="text-center">
                <FileBarChart className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">EEG特征图显示</p>
                <p className="text-xs text-gray-400 mt-1">图像 {currentImageIndex + 1} / 5</p>
              </div>
            ) : (
              <div className="text-center">
                <FileBarChart className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">点击查看EEG特征图</p>
              </div>
            )}
          </div>

          {/* 图像切换按钮 */}
          <div className="flex items-center justify-center space-x-2 mb-4">
            <button
              onClick={() => setCurrentImageIndex(Math.max(0, currentImageIndex - 1))}
              disabled={currentImageIndex === 0 || !showVisualization}
              className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-sm text-gray-600">上一张</span>
            
            <span className="text-sm text-gray-600 mx-4">下一张</span>
            
            <button
              onClick={() => setCurrentImageIndex(Math.min(4, currentImageIndex + 1))}
              disabled={currentImageIndex === 4 || !showVisualization}
              className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>

          <button 
            className="btn btn-primary w-full flex items-center justify-center space-x-2"
            onClick={() => setShowVisualization(!showVisualization)}
          >
            <Eye className="h-4 w-4" />
            <span>图片查看</span>
          </button>
        </div>
      </div>

      {/* 历史评估结果 */}
      <div className="card">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">历史评估结果</h2>
            <div className="flex space-x-2">
              <button
                onClick={fetchResults}
                className="btn btn-secondary flex items-center space-x-2"
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span>刷新</span>
              </button>
              <button
                onClick={exportResults}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>导出结果</span>
              </button>
            </div>
          </div>

          {/* 筛选区域 */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              {/* 用户类型筛选 */}
              <div>
                <label className="label">用户类型:</label>
                <select
                  className="input"
                  value={filters.userType}
                  onChange={(e) => setFilters({ ...filters, userType: e.target.value })}
                >
                  <option value="all">全部</option>
                  <option value="admin">管理员</option>
                  <option value="user">普通用户</option>
                </select>
              </div>

              {/* 用户筛选 */}
              <div>
                <label className="label">用户:</label>
                <select
                  className="input"
                  value={filters.userId}
                  onChange={(e) => setFilters({ ...filters, userId: e.target.value })}
                >
                  <option value="all">全部用户</option>
                  {users.map(user => (
                    <option key={user.user_id} value={user.user_id}>
                      {user.username}
                    </option>
                  ))}
                </select>
              </div>

              {/* 开始日期 */}
              <div>
                <label className="label">开始日期:</label>
                <input
                  type="date"
                  className="input"
                  value={filters.dateStart}
                  onChange={(e) => setFilters({ ...filters, dateStart: e.target.value })}
                />
              </div>

              {/* 结束日期 */}
              <div>
                <label className="label">结束日期:</label>
                <input
                  type="date"
                  className="input"
                  value={filters.dateEnd}
                  onChange={(e) => setFilters({ ...filters, dateEnd: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <button
                onClick={resetFilters}
                className="btn btn-secondary"
              >
                重置
              </button>
              <button
                onClick={() => {/* 筛选已自动应用 */}}
                className="btn btn-primary"
              >
                应用筛选
              </button>
            </div>
          </div>
        </div>

        {/* 结果表格 */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
              <span className="ml-2 text-gray-500">加载中...</span>
            </div>
          ) : filteredResults.length === 0 ? (
            <div className="text-center py-8">
              <FileBarChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">暂无评估结果数据</p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    用户名
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    评估时间
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    普通应激
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    抑郁
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    焦虑
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    社交孤立
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredResults.map((result) => {
                  const user = users.find(u => u.user_id === result.user_id);
                  
                  return (
                    <tr key={result.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <User className="h-4 w-4 text-gray-400 mr-2" />
                          <span className="text-sm font-medium text-gray-900">
                            {user?.username || '未知用户'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(result.result_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          result.stress_score >= 0.7 ? 'bg-red-100 text-red-800' :
                          result.stress_score >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {(result.stress_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          result.depression_score >= 0.7 ? 'bg-red-100 text-red-800' :
                          result.depression_score >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {(result.depression_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          result.anxiety_score >= 0.7 ? 'bg-red-100 text-red-800' :
                          result.anxiety_score >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {(result.anxiety_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          result.social_isolation_score >= 0.7 ? 'bg-red-100 text-red-800' :
                          result.social_isolation_score >= 0.4 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {(result.social_isolation_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => toast('查看详情功能正在开发中', { icon: '👁️' })}
                            className="text-blue-600 hover:text-blue-700"
                            title="查看详情"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                await apiClient.getResultReport(result.id);
                                toast.success('报告下载成功');
                              } catch (error) {
                                toast.error('报告下载失败');
                              }
                            }}
                            className="text-green-600 hover:text-green-700"
                            title="下载报告"
                          >
                            <FileText className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* 显示筛选结果数量 */}
        {filteredResults.length !== results.length && (
          <div className="p-4 bg-blue-50 border-t border-blue-200">
            <p className="text-sm text-blue-700">
              筛选显示 {filteredResults.length} 条结果，共 {results.length} 条记录
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultManagePage; 