import React, { useState, useEffect } from 'react';
import { 
  FileBarChart, 
  Download, 
  Filter, 
  RefreshCw, 
  FileText,
  CheckSquare,
  Square,
  Trash2
} from 'lucide-react';
// ===== 纯前端演示模式 - 特殊标记 =====
// 注释掉后端API相关导入，使用localStorage存储
// import { apiClient } from '@/utils/api';
import { Result, User as UserType } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, initializeDemoData, ResultItem } from '@/utils/localStorage';
import { ReportGenerator, ReportData } from '@/utils/reportGenerator';
import { ChartGenerator } from '@/utils/chartGenerator';
import { ExcelExporter } from '@/utils/excelExporter';
import toast from 'react-hot-toast';
// ============================================


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


const ResultManagePage: React.FC = () => {
  const [filteredResults, setFilteredResults] = useState<Result[]>([]);
  const [users, setUsers] = useState<UserType[]>([]);
  const [selectedResults, setSelectedResults] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
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
        recommendations: item.recommendations,
        personnel_id: item.personnel_id,
        personnel_name: item.personnel_name
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
      
      setFilteredResults(filtered);
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
      const userItems = LocalStorageManager.get<any[]>(STORAGE_KEYS.USERS, []);
      
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


  useEffect(() => {
    fetchResults();
    fetchUsers();
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
  const handleExport = async (format: 'excel' | 'pdf') => {
    if (selectedResults.size === 0) {
      toast.error('请先选择要导出的结果');
      return;
    }

    try {
      setExporting(true);
      
      if (format === 'pdf') {
        // 批量生成报告
        toast('正在批量生成报告...');
        
        const resultItems = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
        const userItems = LocalStorageManager.get<any[]>(STORAGE_KEYS.USERS, []);
        
        for (const resultId of selectedResults) {
          const resultItem = resultItems.find(item => item.id === resultId);
          if (!resultItem) continue;
          
          const userItem = userItems.find(user => user.id === resultItem.user_id);
          if (!userItem) continue;
          
          // 生成图表（包括新增的EEG相关图表和时频域图表）
          const [eegChart, timeDomainChart, frequencyBandChart, diffEntropyChart, timeFreqChart, serumChart] = await Promise.all([
            ChartGenerator.generateEEGChart(resultItem),
            ChartGenerator.generateTimeDomainChart(resultItem),
            ChartGenerator.generateFrequencyBandChart(resultItem),
            ChartGenerator.generateDiffEntropyChart(resultItem),
            ChartGenerator.generateTimeFreqChart(resultItem),
            ChartGenerator.generateSerumChart(resultItem)
          ]);
          
          // 准备报告数据
          const reportData: ReportData = {
            result: resultItem,
            user: {
              username: userItem.username,
              user_type: userItem.role
            },
            charts: {
              eeg: eegChart,
              timeDomain: timeDomainChart,
              frequencyBand: frequencyBandChart,
              diffEntropy: diffEntropyChart,
              timeFreq: timeFreqChart,
              serum: serumChart
            }
          };
          
          // 生成HTML内容
          const htmlContent = ReportGenerator.createReportHTML(reportData);
          
          // 生成PDF文件名
          const filename = `心理健康评估报告_${resultItem.personnel_name || '未知'}_${new Date(resultItem.result_time).toLocaleDateString('zh-CN')}.pdf`;
          
          // 生成并下载PDF
          await ReportGenerator.generatePDF(htmlContent, filename);
        }
        
        toast.success(`成功生成 ${selectedResults.size} 份报告！`);
      } else {
        // Excel导出
        toast('正在导出Excel...');
        
        // 获取选中的结果数据
        const selectedResultsData = filteredResults.filter(result => 
          selectedResults.has(result.id)
        );
        
        // 调用Excel导出工具
        ExcelExporter.exportResults(selectedResultsData, '心理健康评估结果');
        
        toast.success(`成功导出 ${selectedResults.size} 条记录到Excel！`);
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
  // 生成并下载报告
  const handleGenerateReport = async (resultId: number) => {
    try {
      setGeneratingReport(true);
      
      // 获取结果数据
      const resultItems = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      const resultItem = resultItems.find(item => item.id === resultId);
      
      if (!resultItem) {
        toast.error('未找到评估结果');
        return;
      }
      
      // 获取用户数据
      const userItems = LocalStorageManager.get<any[]>(STORAGE_KEYS.USERS, []);
      const userItem = userItems.find(user => user.id === resultItem.user_id);
      
      if (!userItem) {
        toast.error('未找到用户信息');
        return;
      }
      
      toast('正在生成图表...');
      
      // 生成图表（包括新增的EEG相关图表和时频域图表）
      const [eegChart, timeDomainChart, frequencyBandChart, diffEntropyChart, timeFreqChart, serumChart] = await Promise.all([
        ChartGenerator.generateEEGChart(resultItem),
        ChartGenerator.generateTimeDomainChart(resultItem),
        ChartGenerator.generateFrequencyBandChart(resultItem),
        ChartGenerator.generateDiffEntropyChart(resultItem),
        ChartGenerator.generateTimeFreqChart(resultItem),
        ChartGenerator.generateSerumChart(resultItem)
      ]);
      
      toast('正在生成报告...');
      
      // 准备报告数据
      const reportData: ReportData = {
        result: resultItem,
        user: {
          username: userItem.username,
          user_type: userItem.role
        },
        charts: {
          eeg: eegChart,
          timeDomain: timeDomainChart,
          frequencyBand: frequencyBandChart,
          diffEntropy: diffEntropyChart,
          timeFreq: timeFreqChart,
          serum: serumChart
        }
      };
      
      // 生成HTML内容
      const htmlContent = ReportGenerator.createReportHTML(reportData);
      
      // 生成PDF文件名
      const filename = `心理健康评估报告_${resultItem.personnel_name || '未知'}_${new Date(resultItem.result_time).toLocaleDateString('zh-CN')}.pdf`;
      
      // 生成并下载PDF
      await ReportGenerator.generatePDF(htmlContent, filename);
      
      toast.success('报告生成成功！');
      
    } catch (error) {
      console.error('生成报告失败:', error);
      toast.error('生成报告失败');
    } finally {
      setGeneratingReport(false);
    }
  };
  // ============================================

  // 删除结果记录
  const handleDeleteResult = async (resultId: number) => {
    if (!window.confirm('确定要删除这条评估结果吗？此操作不可撤销。')) {
      return;
    }

    try {
      // 从localStorage中删除结果
      const existingResults = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      const updatedResults = existingResults.filter(result => result.id !== resultId);
      
      // 如果删除后没有结果了，清空结果数据
      if (updatedResults.length === 0) {
        LocalStorageManager.clearSpecificData('results');
      } else {
        LocalStorageManager.set(STORAGE_KEYS.RESULTS, updatedResults);
      }
      
      // 重新获取数据
      await fetchResults();
      
      // 从选中列表中移除
      const newSelected = new Set(selectedResults);
      newSelected.delete(resultId);
      setSelectedResults(newSelected);
      
      toast.success('评估结果删除成功');
    } catch (error) {
      console.error('删除评估结果失败:', error);
      toast.error('删除评估结果失败');
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
            onClick={() => handleExport('pdf')}
            disabled={selectedResults.size === 0 || exporting}
            className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
          >
            <FileText className="h-4 w-4" />
            <span>生成报告包</span>
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
                    人员信息
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
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {result.personnel_name || '未知人员'}
                          </div>
                          <div className="text-sm text-gray-500">
                            ID: {result.personnel_id || 'unknown'}
                          </div>
                        </div>
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
                          onClick={() => handleGenerateReport(result.id)}
                          disabled={generatingReport}
                          className="text-purple-600 hover:text-purple-700 disabled:opacity-50"
                          title="生成报告"
                        >
                          <FileText className="h-4 w-4" />
                        </button>
                          <button
                            onClick={() => handleDeleteResult(result.id)}
                            className="text-red-600 hover:text-red-700"
                            title="删除记录"
                          >
                            <Trash2 className="h-4 w-4" />
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
    </div>
  );
};

export default ResultManagePage; 