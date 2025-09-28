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
// ===== 纯前端演示模式 - 特殊标记 =====
// 注释掉后端API相关导入，使用localStorage存储
// import { apiClient } from '@/utils/api';
import { Data, Result } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, DataOperations, initializeDemoData, DataItem, ResultItem } from '@/utils/localStorage';
import toast from 'react-hot-toast';
// ============================================

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

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取数据列表（从localStorage读取）
  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 从localStorage获取数据
      const dataItems = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      
      // 转换为前端Data类型
      const convertedData: Data[] = dataItems.map(item => ({
        user_id: '1', // 添加缺失的user_id字段
        id: item.id,
        personnel_id: item.name.split('_')[0] || 'unknown',
        personnel_name: item.name.split('_')[1]?.replace('.csv', '') || item.name,
        data_path: item.file_path,
        upload_time: item.upload_time,
        upload_user: item.uploader,
        processing_status: item.status === '已处理' ? 'completed' : 
                          item.status === '处理中' ? 'processing' : 'pending',
        feature_status: item.status === '已处理' ? 'completed' : 
                       item.status === '处理中' ? 'processing' : 'pending'
      }));
      
      setDataList(convertedData);
    } catch (error) {
      console.error('获取数据列表失败:', error);
      toast.error('获取数据列表失败');
    } finally {
      setLoading(false);
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取最新结果（从localStorage读取）
  const fetchLatestResults = async () => {
    try {
      // 从localStorage获取结果数据
      const resultItems = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      
      if (resultItems.length > 0) {
        // 获取最新的结果
        const latest = resultItems[resultItems.length - 1];
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
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取LED状态（使用演示数据）
  const fetchLEDStatus = async (resultId: number) => {
    try {
      // 从localStorage获取结果数据
      const resultItems = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      const result = resultItems.find(r => r.id === resultId);
      
      if (result) {
        // 生成LED状态数据
        const ledStatus: LEDStatus = {
          stress_led: result.stress_score >= 50 ? 'red' : result.stress_score >= 30 ? 'yellow' : 'green',
          depression_led: result.depression_score >= 50 ? 'red' : result.depression_score >= 30 ? 'yellow' : 'green',
          anxiety_led: result.anxiety_score >= 50 ? 'red' : result.anxiety_score >= 30 ? 'yellow' : 'green',
          social_led: result.social_isolation_score >= 50 ? 'red' : result.social_isolation_score >= 30 ? 'yellow' : 'green',
          stress_score: result.stress_score,
          depression_score: result.depression_score,
          anxiety_score: result.anxiety_score,
          social_isolation_score: result.social_isolation_score
        };
        setLedStatus(ledStatus);
      }
    } catch (error) {
      console.error('获取LED状态失败:', error);
    }
  };
  // ============================================

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
      // const response = await apiClient.getTop200Data(); // 注释掉API调用
      const top200Ids = [1, 2, 3, 4, 5]; // 模拟前5条数据
      setSelectedItems(new Set(top200Ids));
      toast.success(`已选择前${top200Ids.length}条数据`);
    } catch (error) {
      console.error('获取前200条数据失败:', error);
      toast.error('获取前200条数据失败');
    }
  };

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 单个评估（保存到localStorage）
  const handleSingleEvaluate = async (dataId: number) => {
    try {
      setEvaluating(true);
      
      // 模拟评估延迟
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 生成模拟评估结果
      const stressScore = Math.floor(Math.random() * 60) + 10; // 10-70
      const depressionScore = Math.floor(Math.random() * 60) + 10; // 10-70
      const anxietyScore = Math.floor(Math.random() * 60) + 10; // 10-70
      const socialScore = Math.floor(Math.random() * 60) + 10; // 10-70
      
      // 确定风险等级
      const maxScore = Math.max(stressScore, depressionScore, anxietyScore, socialScore);
      const riskLevel = maxScore >= 50 ? '高风险' : maxScore >= 30 ? '中等风险' : '低风险';
      
      // 生成建议
      const recommendations = maxScore >= 50 ? 
        '建议立即寻求专业心理咨询，注意休息和放松' :
        maxScore >= 30 ? 
        '建议适当调整生活方式，保持积极心态' :
        '保持良好的心理状态，继续当前的生活方式';
      
      // 获取现有结果数据
      const existingResults = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      
      // 创建新结果
      const newResult: ResultItem = {
        id: DataOperations.getNextId(existingResults),
        user_id: 2, // 当前用户ID
        username: 'user',
        result_time: new Date().toISOString(),
        stress_score: stressScore,
        depression_score: depressionScore,
        anxiety_score: anxietyScore,
        social_isolation_score: socialScore,
        overall_risk_level: riskLevel,
        recommendations: recommendations
      };
      
      // 保存到localStorage
      existingResults.push(newResult);
      LocalStorageManager.set(STORAGE_KEYS.RESULTS, existingResults);
      
      // 添加日志
      DataOperations.addLog('HEALTH_EVALUATION', 'HEALTH_ASSESSMENT', `用户完成健康评估，数据ID: ${dataId}`, 'user', '1');
      
      // 更新当前状态
      setCurrentStatus({
        stress: stressScore,
        depression: depressionScore,
        anxiety: anxietyScore,
        social_isolation: socialScore
      });
      setCurrentResultId(newResult.id);
      
      // 获取LED状态
      await fetchLEDStatus(newResult.id);
      
      toast.success('健康评估完成！');
      fetchData(); // 刷新数据列表
    } catch (error) {
      console.error('健康评估失败:', error);
      toast.error('健康评估失败');
    } finally {
      setEvaluating(false);
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 批量评估（保存到localStorage）
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

      // 获取现有结果数据
      const existingResults = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
      
      // 模拟批量评估过程
      for (let i = 0; i < selectedIds.length; i++) {
        const dataId = selectedIds[i];
        
        // 更新进度状态
        setEvaluationProgress(prev => ({
          ...prev,
          [dataId]: {
            status: 'processing',
            progress: 0,
            message: '正在评估...'
          }
        }));
        
        // 模拟评估延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 生成模拟评估结果
        const stressScore = Math.floor(Math.random() * 60) + 10;
        const depressionScore = Math.floor(Math.random() * 60) + 10;
        const anxietyScore = Math.floor(Math.random() * 60) + 10;
        const socialScore = Math.floor(Math.random() * 60) + 10;
        
        const maxScore = Math.max(stressScore, depressionScore, anxietyScore, socialScore);
        const riskLevel = maxScore >= 50 ? '高风险' : maxScore >= 30 ? '中等风险' : '低风险';
        
        const recommendations = maxScore >= 50 ? 
          '建议立即寻求专业心理咨询，注意休息和放松' :
          maxScore >= 30 ? 
          '建议适当调整生活方式，保持积极心态' :
          '保持良好的心理状态，继续当前的生活方式';
        
        // 创建新结果
        const newResult: ResultItem = {
          id: DataOperations.getNextId(existingResults),
          user_id: 2,
          username: 'user',
          result_time: new Date().toISOString(),
          stress_score: stressScore,
          depression_score: depressionScore,
          anxiety_score: anxietyScore,
          social_isolation_score: socialScore,
          overall_risk_level: riskLevel,
          recommendations: recommendations
        };
        
        existingResults.push(newResult);
        
        // 更新进度状态
        setEvaluationProgress(prev => ({
          ...prev,
          [dataId]: {
            status: 'completed',
            progress: 100,
            message: '评估完成',
            result_id: newResult.id
          }
        }));
      }
      
      // 保存到localStorage
      LocalStorageManager.set(STORAGE_KEYS.RESULTS, existingResults);
      
      // 添加日志
      DataOperations.addLog('BATCH_HEALTH_EVALUATION', 'HEALTH_ASSESSMENT', `用户完成批量健康评估，共${selectedIds.length}个数据`, 'user', '1');
      
      toast.success(`批量评估完成，共处理${selectedIds.length}个数据`);
      
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
      // const images = await apiClient.getDataImages(dataId); // 注释掉API调用
      const images: string[] = []; // 模拟空图片数组
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