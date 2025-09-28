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
  FileText,
  CheckSquare,
  Square,
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  Clock,
  Activity,
  AlertTriangle,
  ExternalLink,
  Printer,
  FileImage,
  X
} from 'lucide-react';
// ===== 纯前端演示模式 - 特殊标记 =====
// 注释掉后端API相关导入，使用localStorage存储
// import { apiClient } from '@/utils/api';
import { Result, User as UserType } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, DataOperations, initializeDemoData, ResultItem } from '@/utils/localStorage';
import toast from 'react-hot-toast';
// ============================================

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
  minStressScore: string;
  maxStressScore: string;
  minDepressionScore: string;
  maxDepressionScore: string;
}

interface Statistics {
  total_count: number;
  avg_stress_score: number;
  avg_depression_score: number;
  avg_anxiety_score: number;
  avg_social_isolation_score: number;
  high_risk_count: number;
  high_risk_percentage: number;
  recent_count: number;
}

const ResultManagePage: React.FC = () => {
  const [results, setResults] = useState<Result[]>([]);
  const [filteredResults, setFilteredResults] = useState<Result[]>([]);
  const [users, setUsers] = useState<UserType[]>([]);
  const [selectedResults, setSelectedResults] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<HealthStatus>({
    stress: 0,
    depression: 0,
    anxiety: 0,
    social_isolation: 0
  });
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showVisualization, setShowVisualization] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showStatistics, setShowStatistics] = useState(false);
  const [pdfViewerVisible, setPdfViewerVisible] = useState(false);
  const [currentPdfUrl, setCurrentPdfUrl] = useState<string>('');
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    userType: 'all',
    userId: 'all',
    dateStart: '',
    dateEnd: '',
    minStressScore: '',
    maxStressScore: '',
    minDepressionScore: '',
    maxDepressionScore: ''
  });

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取结果列表（从localStorage读取）
  const fetchResults = async () => {
    try {
      setLoading(true);
      
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 从localStorage获取结果数据
      const resultItems = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      
      // 转换为前端Result类型
      const convertedResults: Result[] = resultItems.map(item => ({
        id: item.id,
        user_id: item.user_id.toString(),
        username: item.username,
        result_time: item.result_time,
        stress_score: item.stress_score,
        depression_score: item.depression_score,
        anxiety_score: item.anxiety_score,
        social_isolation_score: item.social_isolation_score,
        overall_risk_level: item.overall_risk_level,
        recommendations: item.recommendations
      }));
      
      // 应用筛选条件
      let filtered = convertedResults;
      
      if (filters.userId !== 'all') {
        filtered = filtered.filter(result => result.user_id === filters.userId);
      }
      
      if (filters.dateStart) {
        filtered = filtered.filter(result => new Date(result.result_time) >= new Date(filters.dateStart));
      }
      
      if (filters.dateEnd) {
        filtered = filtered.filter(result => new Date(result.result_time) <= new Date(filters.dateEnd));
      }
      
      if (filters.minStressScore) {
        filtered = filtered.filter(result => result.stress_score >= parseFloat(filters.minStressScore));
      }
      
      if (filters.maxStressScore) {
        filtered = filtered.filter(result => result.stress_score <= parseFloat(filters.maxStressScore));
      }
      
      if (filters.minDepressionScore) {
        filtered = filtered.filter(result => result.depression_score >= parseFloat(filters.minDepressionScore));
      }
      
      if (filters.maxDepressionScore) {
        filtered = filtered.filter(result => result.depression_score <= parseFloat(filters.maxDepressionScore));
      }
      
      setResults(convertedResults);
      setFilteredResults(filtered);
      
      // 获取最新结果作为当前状态
      if (filtered.length > 0) {
        const latest = filtered[0];
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
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取用户列表（从localStorage读取）
  const fetchUsers = async () => {
    try {
      // 从localStorage获取用户数据
      const userItems = LocalStorageManager.get(STORAGE_KEYS.USERS, []);
      
      // 转换为前端User类型
      const convertedUsers: UserType[] = userItems.map(user => ({
        user_id: user.id.toString(),
        username: user.username,
        user_type: user.role,
        created_at: user.created_at
      }));
      
      setUsers(convertedUsers);
    } catch (error) {
      console.error('获取用户列表失败:', error);
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取统计信息（从localStorage计算）
  const fetchStatistics = async () => {
    try {
      // 从localStorage获取结果数据
      const resultItems = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      
      // 应用日期筛选
      let filteredResults = resultItems;
      if (filters.dateStart) {
        filteredResults = filteredResults.filter(result => new Date(result.result_time) >= new Date(filters.dateStart));
      }
      if (filters.dateEnd) {
        filteredResults = filteredResults.filter(result => new Date(result.result_time) <= new Date(filters.dateEnd));
      }
      
      // 计算统计信息
      const totalCount = filteredResults.length;
      const avgStressScore = totalCount > 0 ? filteredResults.reduce((sum, r) => sum + r.stress_score, 0) / totalCount : 0;
      const avgDepressionScore = totalCount > 0 ? filteredResults.reduce((sum, r) => sum + r.depression_score, 0) / totalCount : 0;
      const avgAnxietyScore = totalCount > 0 ? filteredResults.reduce((sum, r) => sum + r.anxiety_score, 0) / totalCount : 0;
      const avgSocialIsolationScore = totalCount > 0 ? filteredResults.reduce((sum, r) => sum + r.social_isolation_score, 0) / totalCount : 0;
      
      // 计算高风险数量（任一指标 >= 50）
      const highRiskCount = filteredResults.filter(result => 
        result.stress_score >= 50 || 
        result.depression_score >= 50 || 
        result.anxiety_score >= 50 || 
        result.social_isolation_score >= 50
      ).length;
      
      // 计算最近7天的数量
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      const recentCount = filteredResults.filter(result => 
        new Date(result.result_time) >= sevenDaysAgo
      ).length;
      
      const stats: Statistics = {
        total_count: totalCount,
        avg_stress_score: Math.round(avgStressScore * 100) / 100,
        avg_depression_score: Math.round(avgDepressionScore * 100) / 100,
        avg_anxiety_score: Math.round(avgAnxietyScore * 100) / 100,
        avg_social_isolation_score: Math.round(avgSocialIsolationScore * 100) / 100,
        high_risk_count: highRiskCount,
        high_risk_percentage: totalCount > 0 ? Math.round((highRiskCount / totalCount) * 100) : 0,
        recent_count: recentCount
      };
      
      setStatistics(stats);
    } catch (error) {
      console.error('获取统计信息失败:', error);
    }
  };
  // ============================================

  useEffect(() => {
    fetchResults();
    fetchUsers();
    fetchStatistics();
  }, [filters]);

  // 选择/取消选择结果
  const toggleResultSelection = (resultId: number) => {
    const newSelected = new Set(selectedResults);
    if (newSelected.has(resultId)) {
      newSelected.delete(resultId);
    } else {
      newSelected.add(resultId);
    }
    setSelectedResults(newSelected);
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedResults.size === filteredResults.length) {
      setSelectedResults(new Set());
    } else {
      setSelectedResults(new Set(filteredResults.map(result => result.id)));
    }
  };

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 导出结果（纯前端导出）
  const handleExport = async (format: 'excel' | 'csv' | 'pdf') => {
    if (selectedResults.size === 0) {
      toast.error('请先选择要导出的结果');
      return;
    }

    try {
      setExporting(true);
      
      // 获取选中的结果数据
      const selectedResultsData = filteredResults.filter(result => selectedResults.has(result.id));
      
      if (format === 'csv') {
        // 生成CSV内容
        const headers = ['ID', '用户名', '评估时间', '应激分数', '抑郁分数', '焦虑分数', '社交孤立分数', '风险等级', '建议'];
        const csvContent = [
          headers.join(','),
          ...selectedResultsData.map(result => [
            result.id,
            result.username,
            result.result_time,
            result.stress_score,
            result.depression_score,
            result.anxiety_score,
            result.social_isolation_score,
            result.overall_risk_level,
            `"${result.recommendations}"`
          ].join(','))
        ].join('\n');
        
        // 创建下载链接
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        link.download = `评估结果_${timestamp}.csv`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        toast.success('CSV 导出成功');
      } else {
        // 对于Excel和PDF，显示提示信息
        toast('Excel和PDF导出功能在演示模式下暂不可用，请使用CSV格式');
      }
    } catch (error) {
      console.error('导出失败:', error);
      toast.error('导出失败');
    } finally {
      setExporting(false);
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 查看PDF报告（使用演示PDF）
  const handleViewReport = async (resultId: number) => {
    try {
      // 使用演示PDF URL
      const pdfUrl = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf';
      setCurrentPdfUrl(pdfUrl);
      setPdfViewerVisible(true);
    } catch (error) {
      console.error('查看报告失败:', error);
      toast.error('查看报告失败');
    }
  };
  // ============================================

  // 重新生成报告
  const handleRegenerateReport = async (resultId: number) => {
    try {
      // const response = await apiClient.post(`/results/regenerate-report/${resultId}`); // 注释掉API调用
      toast.success('报告重新生成成功');
    } catch (error) {
      console.error('重新生成报告失败:', error);
      toast.error('重新生成报告失败');
    }
  };

  // 重置筛选
  const resetFilters = () => {
    setFilters({
      userType: 'all',
      userId: 'all',
      dateStart: '',
      dateEnd: '',
      minStressScore: '',
      maxStressScore: '',
      minDepressionScore: '',
      maxDepressionScore: ''
    });
  };

  // 获取状态颜色和标签
  const getStatusInfo = (score: number) => {
    if (score >= 50) return { level: '高风险', color: 'text-red-600', bgColor: 'bg-red-50' };
    if (score >= 30) return { level: '中等风险', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { level: '正常', color: 'text-green-600', bgColor: 'bg-green-50' };
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">结果管理</h1>
        <p className="text-gray-600 mt-1">查看和管理健康评估结果，导出报告数据</p>
      </div>

      {/* 统计信息卡片 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">总评估数</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">{statistics.total_count}</p>
              </div>
              <div className="p-3 rounded-full bg-blue-50">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">高风险比例</p>
                <p className="text-2xl font-bold text-red-600 mt-2">{statistics.high_risk_percentage}%</p>
                <p className="text-sm text-gray-500 mt-1">{statistics.high_risk_count} 人</p>
              </div>
              <div className="p-3 rounded-full bg-red-50">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">平均应激分数</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">{statistics.avg_stress_score}</p>
              </div>
              <div className="p-3 rounded-full bg-purple-50">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">最近7天</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">{statistics.recent_count}</p>
                <p className="text-sm text-gray-500 mt-1">新增评估</p>
              </div>
              <div className="p-3 rounded-full bg-green-50">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 操作栏 */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* 搜索和筛选 */}
        <div className="flex items-center space-x-3">
            <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-secondary flex items-center space-x-2"
            >
            <Filter className="h-4 w-4" />
            <span>筛选</span>
            </button>
          <button 
            onClick={resetFilters}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>重置</span>
          </button>
      </div>

        {/* 导出操作 */}
        <div className="flex items-center space-x-2">
          {selectedResults.size > 0 && (
            <span className="text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
              已选择 {selectedResults.size} 项
            </span>
          )}
              <button
            onClick={() => handleExport('excel')}
            disabled={selectedResults.size === 0 || exporting}
            className="btn btn-secondary flex items-center space-x-2 disabled:opacity-50"
              >
            <Download className="h-4 w-4" />
            <span>导出Excel</span>
              </button>
              <button
            onClick={() => handleExport('csv')}
            disabled={selectedResults.size === 0 || exporting}
            className="btn btn-secondary flex items-center space-x-2 disabled:opacity-50"
              >
                <Download className="h-4 w-4" />
            <span>导出CSV</span>
          </button>
          <button
            onClick={() => handleExport('pdf')}
            disabled={selectedResults.size === 0 || exporting}
            className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
          >
            <FileText className="h-4 w-4" />
            <span>导出PDF包</span>
              </button>
            </div>
          </div>

      {/* 高级筛选面板 */}
      {showFilters && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">高级筛选</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* 用户筛选 */}
              <div>
              <label className="label">用户筛选</label>
                <select
                  className="input"
                  value={filters.userId}
                  onChange={(e) => setFilters({ ...filters, userId: e.target.value })}
                >
                  <option value="all">全部用户</option>
                  {users.map(user => (
                    <option key={user.user_id} value={user.user_id}>
                    {user.username} ({user.user_type})
                    </option>
                  ))}
                </select>
              </div>

            {/* 日期范围 */}
              <div>
              <label className="label">开始日期</label>
                <input
                  type="date"
                  className="input"
                  value={filters.dateStart}
                  onChange={(e) => setFilters({ ...filters, dateStart: e.target.value })}
                />
              </div>
              <div>
              <label className="label">结束日期</label>
                <input
                  type="date"
                  className="input"
                  value={filters.dateEnd}
                  onChange={(e) => setFilters({ ...filters, dateEnd: e.target.value })}
                />
              </div>

            {/* 分数范围 */}
            <div>
              <label className="label">应激分数范围</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  placeholder="最小值"
                  className="input"
                  value={filters.minStressScore}
                  onChange={(e) => setFilters({ ...filters, minStressScore: e.target.value })}
                />
                <input
                  type="number"
                  placeholder="最大值"
                  className="input"
                  value={filters.maxStressScore}
                  onChange={(e) => setFilters({ ...filters, maxStressScore: e.target.value })}
                />
            </div>
            </div>
          </div>
        </div>
      )}

      {/* 结果列表 */}
      <div className="card overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
              <span className="ml-2 text-gray-500">加载中...</span>
            </div>
          ) : filteredResults.length === 0 ? (
            <div className="text-center py-8">
              <FileBarChart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">暂无评估结果</p>
            </div>
          ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={toggleSelectAll}
                      className="flex items-center space-x-2 hover:text-gray-700"
                    >
                      {selectedResults.size === filteredResults.length && filteredResults.length > 0 ? 
                        <CheckSquare className="h-4 w-4" /> : 
                        <Square className="h-4 w-4" />
                      }
                      <span>选择</span>
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    评估分数
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    状态
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    评估时间
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredResults.map((result) => (
                    <tr key={result.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => toggleResultSelection(result.id)}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        {selectedResults.has(result.id) ? 
                          <CheckSquare className="h-4 w-4" /> : 
                          <Square className="h-4 w-4" />
                        }
                      </button>
                    </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {result.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-xs space-y-1">
                        <div className="flex justify-between">
                          <span>应激:</span>
                          <span className={getStatusInfo(result.stress_score).color}>
                            {result.stress_score.toFixed(1)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>抑郁:</span>
                          <span className={getStatusInfo(result.depression_score).color}>
                            {result.depression_score.toFixed(1)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>焦虑:</span>
                          <span className={getStatusInfo(result.anxiety_score).color}>
                            {result.anxiety_score.toFixed(1)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>社交:</span>
                          <span className={getStatusInfo(result.social_isolation_score).color}>
                            {result.social_isolation_score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {(() => {
                        const maxScore = Math.max(
                          result.stress_score,
                          result.depression_score,
                          result.anxiety_score,
                          result.social_isolation_score
                        );
                        const status = getStatusInfo(maxScore);
                        return (
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${status.bgColor} ${status.color}`}>
                            {status.level}
                          </span>
                        );
                      })()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(result.result_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                          onClick={() => handleViewReport(result.id)}
                            className="text-blue-600 hover:text-blue-700"
                          title="查看报告"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                          onClick={() => handleRegenerateReport(result.id)}
                            className="text-green-600 hover:text-green-700"
                          title="重新生成报告"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleExport('pdf')}
                          className="text-purple-600 hover:text-purple-700"
                            title="下载报告"
                          >
                          <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* PDF查看器模态框 */}
      {pdfViewerVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-full max-w-6xl mx-4 h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">评估报告查看器</h2>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => window.open(currentPdfUrl, '_blank')}
                  className="btn btn-secondary flex items-center space-x-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>新窗口打开</span>
                </button>
                <button
                  onClick={() => setPdfViewerVisible(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="flex-1 p-4">
              <iframe
                src={currentPdfUrl}
                className="w-full h-full border border-gray-300 rounded-lg"
                title="PDF Report Viewer"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultManagePage; 