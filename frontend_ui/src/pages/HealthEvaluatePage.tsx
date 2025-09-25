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
  RefreshCw,
  Image,
  ArrowLeft,
  ArrowRight,
  ZoomIn,
  FileImage,
  AlertTriangle,
  Clock,
  Download,
  BarChart3
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

interface LEDStatus {
  stress_led: string;
  depression_led: string;
  anxiety_led: string;
  social_led: string;
  stress_score: number;
  depression_score: number;
  anxiety_score: number;
  social_isolation_score: number;
}

interface EvaluationProgress {
  [key: number]: {
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress: number;
    message: string;
    result_id?: number;
  };
}

const HealthEvaluatePage: React.FC = () => {
  const [dataList, setDataList] = useState<Data[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [batchEvaluating, setBatchEvaluating] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<HealthStatus>({
    stress: 0,
    depression: 0,
    anxiety: 0,
    social_isolation: 0
  });
  const [ledStatus, setLedStatus] = useState<LEDStatus | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showVisualization, setShowVisualization] = useState(false);
  const [imageViewerVisible, setImageViewerVisible] = useState(false);
  const [batchProgressVisible, setBatchProgressVisible] = useState(false);
  const [evaluationProgress, setEvaluationProgress] = useState<EvaluationProgress>({});
  const [currentImageData, setCurrentImageData] = useState<{
    dataId: number;
    images: any[];
    currentIndex: number;
  } | null>(null);
  const [currentResultId, setCurrentResultId] = useState<number | null>(null);

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
        setCurrentResultId(latest.id);
        
        // 获取LED状态
        await fetchLEDStatus(latest.id);
      }
    } catch (error) {
      console.error('获取最新结果失败:', error);
    }
  };

  // 获取LED状态
  const fetchLEDStatus = async (resultId: number) => {
    try {
      const response = await apiClient.get(`/health/led-status/${resultId}`);
      setLedStatus(response);
    } catch (error) {
      console.error('获取LED状态失败:', error);
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

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedItems.size === dataList.length && dataList.length > 0) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(dataList.map(item => item.id)));
    }
  };

  // 选择前200条
  const selectTop200 = async () => {
    try {
      const response = await apiClient.getTop200Data();
      const top200Ids = response.map((item: Data) => item.id);
      setSelectedItems(new Set(top200Ids));
      toast.success(`已选择前${top200Ids.length}条数据`);
    } catch (error) {
      console.error('获取前200条数据失败:', error);
      toast.error('获取前200条数据失败');
    }
  };

  // 单个评估
  const handleSingleEvaluate = async (dataId: number) => {
    try {
      setEvaluating(true);
      const result = await apiClient.post('/health/evaluate', { data_id: dataId });
      
      // 更新当前状态
      setCurrentStatus({
        stress: result.stress_score || 0,
        depression: result.depression_score || 0,
        anxiety: result.anxiety_score || 0,
        social_isolation: result.social_isolation_score || 0
      });
      setCurrentResultId(result.id);
      
      // 获取LED状态
      await fetchLEDStatus(result.id);
      
      toast.success('健康评估完成！');
      fetchData(); // 刷新数据列表
    } catch (error) {
      console.error('健康评估失败:', error);
      toast.error('健康评估失败');
    } finally {
      setEvaluating(false);
    }
  };

  // 批量评估
  const handleBatchEvaluate = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要评估的数据');
      return;
    }

    try {
      setBatchEvaluating(true);
      setBatchProgressVisible(true);
      
      const selectedIds = Array.from(selectedItems);
      
      // 初始化进度状态
      const initialProgress: EvaluationProgress = {};
      selectedIds.forEach(id => {
        initialProgress[id] = {
          status: 'pending',
          progress: 0,
          message: '等待评估...'
        };
      });
      setEvaluationProgress(initialProgress);

      // 启动批量评估
      const response = await apiClient.post('/health/batch-evaluate', { 
        data_ids: selectedIds 
      });
      
      toast.success(response.message || '批量评估已启动');
      
      // 模拟进度更新（实际应用中可以通过WebSocket获取实时进度）
      setTimeout(() => {
        const updatedProgress = { ...initialProgress };
        selectedIds.forEach(id => {
          updatedProgress[id] = {
            status: 'completed',
            progress: 100,
            message: '评估完成',
            result_id: Math.floor(Math.random() * 1000) // 模拟result_id
          };
        });
        setEvaluationProgress(updatedProgress);
        setBatchEvaluating(false);
        fetchLatestResults(); // 刷新最新结果
      }, 3000);
      
    } catch (error) {
      console.error('批量评估失败:', error);
      toast.error('批量评估失败');
      setBatchEvaluating(false);
    }
  };

  // 查看数据图像
  const handleViewImages = async (dataId: number) => {
    try {
      const images = await apiClient.getDataImages(dataId);
      setCurrentImageData({
        dataId,
        images,
        currentIndex: 0
      });
      setImageViewerVisible(true);
    } catch (error) {
      console.error('获取图像列表失败:', error);
      toast.error('获取图像列表失败');
    }
  };

  // 切换图像
  const navigateImage = (direction: 'prev' | 'next') => {
    if (!currentImageData) return;
    
    const { images, currentIndex } = currentImageData;
    let newIndex = currentIndex;
    
    if (direction === 'prev') {
      newIndex = currentIndex > 0 ? currentIndex - 1 : images.length - 1;
    } else {
      newIndex = currentIndex < images.length - 1 ? currentIndex + 1 : 0;
    }
    
    setCurrentImageData({
      ...currentImageData,
      currentIndex: newIndex
    });
  };

  // LED指示器组件
  const LEDIndicator = ({ status, score, label }: { status: string; score: number; label: string }) => (
    <div className="flex items-center space-x-3">
      <div 
        className={`w-8 h-8 rounded-full border-2 border-white shadow-lg ${
          status === 'red' ? 'bg-red-500' : 'bg-gray-400'
        }`}
        title={`${label}: ${score.toFixed(1)}`}
      />
      <div>
        <div className="text-sm font-medium text-gray-900">{label}</div>
        <div className="text-xs text-gray-500">{score.toFixed(1)}</div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">健康评估</h1>
        <p className="text-gray-600 mt-1">进行应激、抑郁、焦虑和社交孤立评估</p>
      </div>

      {/* LED状态指示器 */}
      {ledStatus && (
        <div className="card p-6 bg-gradient-to-r from-blue-50 to-purple-50">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 text-center">健康状态指示器</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <LEDIndicator 
              status={ledStatus.stress_led} 
              score={ledStatus.stress_score} 
              label="普通应激" 
            />
            <LEDIndicator 
              status={ledStatus.depression_led} 
              score={ledStatus.depression_score} 
              label="抑郁" 
            />
            <LEDIndicator 
              status={ledStatus.anxiety_led} 
              score={ledStatus.anxiety_score} 
              label="焦虑" 
            />
            <LEDIndicator 
              status={ledStatus.social_led} 
              score={ledStatus.social_isolation_score} 
              label="社交孤立" 
            />
          </div>
          <div className="mt-4 text-center text-sm text-gray-600">
            <div className="flex items-center justify-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>高风险 (≥50)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                <span>正常 (&lt;50)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 操作栏 */}
      <div className="flex flex-wrap items-center gap-3">
                  <button
                    onClick={selectTop200}
                    className="btn btn-secondary flex items-center space-x-2"
                  >
                    <CheckSquare className="h-4 w-4" />
                    <span>选择前200条</span>
                  </button>
                  <button
                    onClick={handleBatchEvaluate}
          disabled={selectedItems.size === 0 || batchEvaluating}
                    className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
                  >
          {batchEvaluating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          <span>批量评估</span>
                  </button>
                  <button
          onClick={toggleSelectAll}
          className="btn btn-secondary flex items-center space-x-2"
        >
          {selectedItems.size === dataList.length && dataList.length > 0 ? 
            <CheckSquare className="h-4 w-4" /> : 
            <Square className="h-4 w-4" />
          }
          <span>全选</span>
                  </button>
        {selectedItems.size > 0 && (
          <span className="text-sm text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
            已选择 {selectedItems.size} 项
          </span>
              )}
            </div>

      {/* 数据列表 */}
      <div className="card overflow-hidden">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
                  <span className="ml-2 text-gray-500">加载中...</span>
                </div>
        ) : dataList.length === 0 ? (
          <div className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">暂无数据文件</p>
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
                      {selectedItems.size === dataList.length && dataList.length > 0 ? 
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
                    文件路径
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    上传时间
                      </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
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
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {item.personnel_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {item.personnel_id}
                        </div>
                      </div>
                        </td>
                    <td className="px-6 py-4">
                          <div className="text-sm text-gray-900 max-w-xs truncate" title={item.data_path}>
                            {item.data_path}
                          </div>
                        </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDateTime(item.upload_time)}
                        </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleViewImages(item.id)}
                          className="text-blue-600 hover:text-blue-700"
                          title="查看图像"
                        >
                          <Image className="h-4 w-4" />
                        </button>
                          <button
                          onClick={() => handleSingleEvaluate(item.id)}
                          disabled={evaluating}
                          className="text-green-600 hover:text-green-700 disabled:opacity-50"
                          title="开始评估"
                          >
                          {evaluating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
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

      {/* 批量评估进度模态框 */}
      {batchProgressVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">批量评估进度</h2>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {Object.entries(evaluationProgress).map(([dataId, progress]) => (
                <div key={dataId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">数据ID: {dataId}</span>
                  <div className="flex items-center space-x-2">
                    {progress.status === 'pending' && (
                      <Clock className="h-4 w-4 text-gray-500" />
                    )}
                    {progress.status === 'processing' && (
                      <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
                    )}
                    {progress.status === 'completed' && (
                      <CheckSquare className="h-4 w-4 text-green-500" />
                    )}
                    {progress.status === 'failed' && (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-xs text-gray-600">{progress.message}</span>
              </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setBatchProgressVisible(false)}
                className="btn btn-primary"
                disabled={batchEvaluating}
              >
                {batchEvaluating ? '评估中...' : '关闭'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 图像查看器模态框 */}
      {imageViewerVisible && currentImageData && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                数据ID: {currentImageData.dataId} - 特征图像查看器
              </h2>
              <button
                onClick={() => setImageViewerVisible(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {currentImageData.images.length > 0 ? (
              <div className="space-y-4">
                {/* 图像导航 */}
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    {currentImageData.currentIndex + 1} / {currentImageData.images.length}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => navigateImage('prev')}
                      className="btn btn-secondary flex items-center space-x-1"
                    >
                      <ArrowLeft className="h-4 w-4" />
                      <span>上一张</span>
                    </button>
            <button 
                      onClick={() => navigateImage('next')}
                      className="btn btn-secondary flex items-center space-x-1"
            >
                      <span>下一张</span>
                      <ArrowRight className="h-4 w-4" />
            </button>
                  </div>
                </div>
                
                {/* 当前图像信息 */}
                <div className="bg-gray-50 p-3 rounded-lg">
                  <h3 className="font-medium text-gray-900">
                    {currentImageData.images[currentImageData.currentIndex]?.description}
                  </h3>
                  <p className="text-sm text-gray-600">
                    文件名: {currentImageData.images[currentImageData.currentIndex]?.image_name}
                  </p>
                </div>
                
                {/* 图像显示区域 */}
                <div className="flex justify-center bg-gray-100 rounded-lg p-4">
                  <div 
                    className="relative group cursor-pointer"
                    onClick={() => {
                      console.log('健康评估页面图片点击事件触发');
                      const imageUrl = `/api/health/image/${currentImageData.dataId}/${currentImageData.images[currentImageData.currentIndex]?.image_type}`;
                      console.log('打开图片URL:', imageUrl);
                      const newWindow = window.open(imageUrl, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
                      if (!newWindow) {
                        alert('弹窗被浏览器阻止，请允许弹窗后重试');
                      }
                    }}
                  >
                    <img
                      src={`/api/health/image/${currentImageData.dataId}/${currentImageData.images[currentImageData.currentIndex]?.image_type}`}
                      alt={currentImageData.images[currentImageData.currentIndex]?.description}
                      className="max-w-full max-h-96 object-contain rounded-lg shadow-lg hover:shadow-xl transition-shadow"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7lm77lg4/kuI3lrZjlnKg8L3RleHQ+PC9zdmc+';
                      }}
                    />
                    {/* 悬停提示 */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black bg-opacity-30 rounded-lg pointer-events-none">
                      <div className="bg-white px-3 py-1 rounded text-sm font-medium shadow-lg">
                        点击在新窗口打开
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <FileImage className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">该数据暂无可用图像</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthEvaluatePage; 