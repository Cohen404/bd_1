import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  CheckSquare, 
  Square, 
  RefreshCw,
  Image,
  ArrowLeft,
  ArrowRight,
  FileImage,
  AlertTriangle,
  Clock,
  Play
} from 'lucide-react';
// ===== 纯前端演示模式 - 特殊标记 =====
// 注释掉后端API相关导入，使用localStorage存储
// import { apiClient } from '@/utils/api';
import { Data } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, DataOperations, initializeDemoData, DataItem, ResultItem } from '@/utils/localStorage';
import toast from 'react-hot-toast';
// ============================================


interface EvaluationProgress {
  [key: number]: {
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress: number;
    message: string;
    result_id?: number;
    result_data?: {
      stress_score: number;
      depression_score: number;
      anxiety_score: number;
      social_isolation_score: number;
      overall_risk_level: string;
      recommendations: string;
    };
  };
}

const HealthEvaluatePage: React.FC = () => {
  const [dataList, setDataList] = useState<Data[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [batchEvaluating, setBatchEvaluating] = useState(false);
  const [imageViewerVisible, setImageViewerVisible] = useState(false);
  const [batchProgressVisible, setBatchProgressVisible] = useState(false);
  const [evaluationProgress, setEvaluationProgress] = useState<EvaluationProgress>({});
  const [currentImageData, setCurrentImageData] = useState<{
    dataId: number;
    images: any[];
    currentIndex: number;
  } | null>(null);
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());

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
        upload_user: parseInt(item.uploader) || 1, // 转换为number类型
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



  useEffect(() => {
    fetchData();
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
  // 生成一致的评估结果（基于数据ID的固定算法）
  const generateConsistentEvaluation = (dataId: number) => {
    // 使用数据ID作为种子，确保同一数据ID总是生成相同结果
    const seed = dataId * 12345 + 67890;
    const normalizedSeed = (seed % 1000) / 1000; // 归一化到0-1
    
    // 基于种子生成固定范围的分数
    const stressScore = Math.floor(normalizedSeed * 40 + 15); // 15-55
    const depressionScore = Math.floor((normalizedSeed * 0.7 + 0.3) * 40 + 10); // 10-50
    const anxietyScore = Math.floor((normalizedSeed * 0.5 + 0.5) * 45 + 12); // 12-57
    const socialScore = Math.floor((normalizedSeed * 0.8 + 0.2) * 35 + 8); // 8-43
    
    const maxScore = Math.max(stressScore, depressionScore, anxietyScore, socialScore);
    const riskLevel = maxScore >= 50 ? '高风险' : maxScore >= 30 ? '中等风险' : '低风险';
    
    const recommendations = maxScore >= 50 ? 
      '建议立即寻求专业心理咨询，注意休息和放松' :
      maxScore >= 30 ? 
      '建议适当调整生活方式，保持积极心态' :
      '保持良好的心理状态，继续当前的生活方式';
    
    return {
      stress_score: stressScore,
      depression_score: depressionScore,
      anxiety_score: anxietyScore,
      social_isolation_score: socialScore,
      overall_risk_level: riskLevel,
      recommendations: recommendations
    };
  };

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
        
        // 生成一致的评估结果
        const evaluationResult = generateConsistentEvaluation(dataId);
        
        // 获取对应数据的人员信息
        const dataItem = dataList.find(item => item.id === dataId);
        
        // 创建结果记录（每次评估保存一条记录）
        const newResult: ResultItem = {
          id: DataOperations.getNextId(existingResults),
          user_id: 2,
          username: 'user',
          result_time: new Date().toISOString(),
          stress_score: evaluationResult.stress_score,
          depression_score: evaluationResult.depression_score,
          anxiety_score: evaluationResult.anxiety_score,
          social_isolation_score: evaluationResult.social_isolation_score,
          overall_risk_level: evaluationResult.overall_risk_level,
          recommendations: evaluationResult.recommendations,
          personnel_id: dataItem?.personnel_id || 'unknown',
          personnel_name: dataItem?.personnel_name || '未知人员'
        };
        
        existingResults.push(newResult);
        
        // 更新进度状态
        setEvaluationProgress(prev => ({
          ...prev,
          [dataId]: {
            status: 'completed',
            progress: 100,
            message: '评估完成',
            result_id: newResult.id,
            result_data: {
              stress_score: evaluationResult.stress_score,
              depression_score: evaluationResult.depression_score,
              anxiety_score: evaluationResult.anxiety_score,
              social_isolation_score: evaluationResult.social_isolation_score,
              overall_risk_level: evaluationResult.overall_risk_level,
              recommendations: evaluationResult.recommendations
            }
          }
        }));
      }
      
      // 保存到localStorage
      LocalStorageManager.set(STORAGE_KEYS.RESULTS, existingResults);
      
      // 添加日志
      DataOperations.addLog('BATCH_HEALTH_EVALUATION', 'HEALTH_ASSESSMENT', `用户完成批量健康评估，共${selectedIds.length}个数据`, 'user', '1');
      
      toast.success(`批量评估完成，共处理${selectedIds.length}个数据`);
      
      // 评估完成后，保持弹窗打开状态，只更新状态
      setBatchEvaluating(false);
      
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

  // 切换结果展开状态
  const toggleResultExpansion = (dataId: number) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(dataId)) {
      newExpanded.delete(dataId);
    } else {
      newExpanded.add(dataId);
    }
    setExpandedResults(newExpanded);
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

  // 评估结果展示组件
  const EvaluationResultDisplay = ({ resultData }: { resultData: EvaluationProgress[number]['result_data'] }) => {
    if (!resultData) return null;

    const getLEDStatus = (score: number) => {
      return score >= 50 ? 'red' : 'green';
    };

    return (
      <div className="mt-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">评估结果详情</h4>
        
        {/* 健康状态指示器 */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <LEDIndicator 
            status={getLEDStatus(resultData.stress_score)} 
            score={resultData.stress_score} 
            label="普通应激" 
          />
          <LEDIndicator 
            status={getLEDStatus(resultData.depression_score)} 
            score={resultData.depression_score} 
            label="抑郁" 
          />
          <LEDIndicator 
            status={getLEDStatus(resultData.anxiety_score)} 
            score={resultData.anxiety_score} 
            label="焦虑" 
          />
          <LEDIndicator 
            status={getLEDStatus(resultData.social_isolation_score)} 
            score={resultData.social_isolation_score} 
            label="社交孤立" 
          />
        </div>

        {/* 风险等级和建议 */}
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">风险等级:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              resultData.overall_risk_level === '高风险' ? 'bg-red-100 text-red-800' :
              resultData.overall_risk_level === '中等风险' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {resultData.overall_risk_level}
            </span>
          </div>
          <div>
            <span className="text-sm font-medium text-gray-700">建议:</span>
            <p className="text-sm text-gray-600 mt-1">{resultData.recommendations}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">健康评估</h1>
        <p className="text-gray-600 mt-1">进行应激、抑郁、焦虑和社交孤立评估</p>
      </div>


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
                <div key={dataId} className="bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between p-3">
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
                      
                      {/* 展开/收起按钮 - 仅评估完成时显示 */}
                      {progress.status === 'completed' && progress.result_data && (
                        <button
                          onClick={() => toggleResultExpansion(parseInt(dataId))}
                          className="ml-2 text-blue-600 hover:text-blue-700 text-xs font-medium"
                        >
                          {expandedResults.has(parseInt(dataId)) ? '收起' : '展开'}
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* 展开的评估结果 */}
                  {progress.status === 'completed' && progress.result_data && expandedResults.has(parseInt(dataId)) && (
                    <div className="px-3 pb-3">
                      <EvaluationResultDisplay resultData={progress.result_data} />
                    </div>
                  )}
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