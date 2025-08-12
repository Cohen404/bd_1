import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Brain, 
  CheckSquare, 
  Square, 
  Play, 
  Eye, 
  ChevronLeft, 
  ChevronRight,
  RefreshCw
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Data, Result } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';

interface HealthStatus {
  stress: number;
  depression: number;
  anxiety: number;
  social_isolation: number;
}

const HealthEvaluatePage: React.FC = () => {
  const [dataList, setDataList] = useState<Data[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<HealthStatus>({
    stress: 0,
    depression: 0,
    anxiety: 0,
    social_isolation: 0
  });
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showVisualization, setShowVisualization] = useState(false);

  // 获取数据列表
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getData();
      setDataList(Array.isArray(response) ? response : response?.items || []);
    } catch (error) {
      console.error('获取数据列表失败:', error);
      toast.error('获取数据列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取最新结果
  const fetchLatestResults = async () => {
    try {
      const response = await apiClient.getResults({ size: 1 });
      const results = Array.isArray(response) ? response : response?.items || [];
      if (results.length > 0) {
        const latest = results[0];
        setCurrentStatus({
          stress: latest.stress_score || 0,
          depression: latest.depression_score || 0,
          anxiety: latest.anxiety_score || 0,
          social_isolation: latest.social_isolation_score || 0
        });
      }
    } catch (error) {
      console.error('获取最新结果失败:', error);
    }
  };

  useEffect(() => {
    fetchData();
    fetchLatestResults();
  }, []);

  // 选择/取消选择项目
  const toggleSelection = (dataId: number) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(dataId)) {
      newSelected.delete(dataId);
    } else {
      newSelected.add(dataId);
    }
    setSelectedItems(newSelected);
  };

  // 选择前200条
  const selectTop200 = () => {
    const top200 = dataList.slice(0, 200).map(item => item.id);
    setSelectedItems(new Set(top200));
    toast.success(`已选择前${Math.min(200, dataList.length)}条数据`);
  };

  // 批量评估
  const handleBatchEvaluate = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要评估的数据');
      return;
    }

    try {
      setEvaluating(true);
      const selectedIds = Array.from(selectedItems);
      
      // 显示进度提示
      toast.loading('正在进行批量评估，请稍候...', { duration: 3000 });
      
      await apiClient.batchEvaluateHealth({ data_ids: selectedIds });
      toast.success(`已完成${selectedIds.length}条数据的健康评估`);
      
      // 更新最新结果
      await fetchLatestResults();
      setSelectedItems(new Set());
    } catch (error) {
      console.error('批量评估失败:', error);
      toast.error('批量评估失败');
    } finally {
      setEvaluating(false);
    }
  };

  // 获取状态颜色和标签
  const getStatusInfo = (score: number, type: string) => {
    let level = '正常';
    let color = 'bg-green-500';
    let textColor = 'text-green-600';
    
    if (score >= 0.7) {
      level = '高风险';
      color = 'bg-red-500';
      textColor = 'text-red-600';
    } else if (score >= 0.4) {
      level = '中等风险';
      color = 'bg-yellow-500';
      textColor = 'text-yellow-600';
    }
    
    return { level, color, textColor, percentage: (score * 100).toFixed(1) };
  };

  // 获取整体状态
  const getOverallStatus = () => {
    const maxScore = Math.max(
      currentStatus.stress,
      currentStatus.depression,
      currentStatus.anxiety,
      currentStatus.social_isolation
    );
    
    if (maxScore >= 0.7) return { text: '需要关注', color: 'text-red-600', bgColor: 'bg-red-50' };
    if (maxScore >= 0.4) return { text: '轻度异常', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { text: '状态良好', color: 'text-green-600', bgColor: 'bg-green-50' };
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">健康评估</h1>
        <p className="text-gray-600 mt-1">进行应激、抑郁、焦虑和社交孤立的健康状态分析</p>
      </div>

      {/* 当前状态显示 */}
      <div className={`card p-6 ${overallStatus.bgColor}`}>
        <div className="text-center">
          <h2 className={`text-3xl font-bold ${overallStatus.color} mb-2`}>
            {overallStatus.text}
          </h2>
          <p className="text-gray-600">整体健康状态评估结果</p>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* 数据选择表格 */}
        <div className="xl:col-span-2">
          <div className="card">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">数据选择</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={selectTop200}
                    className="btn btn-secondary flex items-center space-x-2"
                  >
                    <CheckSquare className="h-4 w-4" />
                    <span>选择前200条</span>
                  </button>
                  <button
                    onClick={handleBatchEvaluate}
                    disabled={selectedItems.size === 0 || evaluating}
                    className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
                  >
                    {evaluating ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                    <span>{evaluating ? '评估中...' : '批量评估'}</span>
                  </button>
                </div>
              </div>
              
              {/* 选择计数 */}
              {selectedItems.size > 0 && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <span className="text-blue-700 font-medium">
                    已选择: {selectedItems.size}/{Math.min(200, dataList.length)} 条数据
                  </span>
                  <button
                    onClick={() => setSelectedItems(new Set())}
                    className="ml-4 text-blue-600 hover:text-blue-700 text-sm"
                  >
                    清除选择
                  </button>
                </div>
              )}
            </div>

            {/* 数据表格 */}
            <div className="overflow-x-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
                  <span className="ml-2 text-gray-500">加载中...</span>
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        选择
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        人员ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        数据路径
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        上传用户
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {dataList.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <button
                            onClick={() => toggleSelection(item.id)}
                            className="text-primary-600 hover:text-primary-700"
                          >
                            {selectedItems.has(item.id) ? 
                              <CheckSquare className="h-4 w-4" /> : 
                              <Square className="h-4 w-4" />
                            }
                          </button>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.personnel_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 max-w-xs truncate" title={item.data_path}>
                            {item.data_path}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          用户{item.upload_user}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={async () => {
                              try {
                                await apiClient.evaluateHealth({ data_id: item.id });
                                toast.success('单个评估完成');
                                await fetchLatestResults();
                              } catch (error) {
                                toast.error('评估失败');
                              }
                            }}
                            className="text-primary-600 hover:text-primary-700"
                          >
                            评估
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>

        {/* 健康状态指示器和可视化 */}
        <div className="xl:col-span-1 space-y-6">
          {/* 健康状态指示器 */}
          <div className="card p-6 bg-primary-50">
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-6">健康状态指标</h3>
            
            <div className="space-y-4">
              {/* 普通应激 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.stress, 'stress').color}`}
                  />
                  <span className="text-sm font-medium">普通应激</span>
                </div>
                <span className={`text-sm font-bold ${getStatusInfo(currentStatus.stress, 'stress').textColor}`}>
                  {getStatusInfo(currentStatus.stress, 'stress').percentage}%
                </span>
              </div>

              {/* 抑郁 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.depression, 'depression').color}`}
                  />
                  <span className="text-sm font-medium">抑郁</span>
                </div>
                <span className={`text-sm font-bold ${getStatusInfo(currentStatus.depression, 'depression').textColor}`}>
                  {getStatusInfo(currentStatus.depression, 'depression').percentage}%
                </span>
              </div>

              {/* 焦虑 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.anxiety, 'anxiety').color}`}
                  />
                  <span className="text-sm font-medium">焦虑</span>
                </div>
                <span className={`text-sm font-bold ${getStatusInfo(currentStatus.anxiety, 'anxiety').textColor}`}>
                  {getStatusInfo(currentStatus.anxiety, 'anxiety').percentage}%
                </span>
              </div>

              {/* 社交孤立 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className={`w-6 h-6 rounded-full border-2 border-white ${getStatusInfo(currentStatus.social_isolation, 'social').color}`}
                  />
                  <span className="text-sm font-medium">社交孤立</span>
                </div>
                <span className={`text-sm font-bold ${getStatusInfo(currentStatus.social_isolation, 'social').textColor}`}>
                  {getStatusInfo(currentStatus.social_isolation, 'social').percentage}%
                </span>
              </div>
            </div>
          </div>

          {/* 数据可视化 */}
          <div className="card p-6 bg-primary-50">
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-4">数据可视化</h3>
            
            {/* 可视化图表区域 */}
            <div className="bg-white rounded-lg p-4 min-h-[200px] flex items-center justify-center border-2 border-dashed border-gray-300 mb-4">
              {showVisualization ? (
                <div className="text-center">
                  <Brain className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">EEG特征可视化</p>
                  <p className="text-xs text-gray-400 mt-1">图像 {currentImageIndex + 1} / 5</p>
                </div>
              ) : (
                <div className="text-center">
                  <Activity className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">请先进行评估</p>
                </div>
              )}
            </div>

            {/* 图像切换按钮 */}
            <div className="flex items-center justify-center space-x-2 mb-4">
              <button
                onClick={() => setCurrentImageIndex(Math.max(0, currentImageIndex - 1))}
                disabled={currentImageIndex === 0}
                className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-sm text-gray-600">上一张</span>
              
              <span className="text-sm text-gray-600 mx-4">下一张</span>
              
              <button
                onClick={() => setCurrentImageIndex(Math.min(4, currentImageIndex + 1))}
                disabled={currentImageIndex === 4}
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
      </div>
    </div>
  );
};

export default HealthEvaluatePage; 