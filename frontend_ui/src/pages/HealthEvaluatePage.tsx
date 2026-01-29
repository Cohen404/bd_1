import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  CheckSquare, 
  Square, 
  RefreshCw,
  ArrowLeft,
  ArrowRight,
  FileImage,
  AlertTriangle,
  Clock,
  Play
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Data } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';

interface PersonnelSubData {
  id: number;
  data_path: string;
  upload_time: string;
  period: string;
  has_result?: boolean;
  stress_score?: number;
  depression_score?: number;
  anxiety_score?: number;
  overall_risk_level?: string;
  recommendations?: string;
  blood_oxygen?: number;
  blood_pressure?: string;
  selected?: boolean;
}

interface PersonnelData extends Data {
  subData: PersonnelSubData[];
  expanded: boolean;
}


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
      overall_risk_level: string;
      recommendations: string;
    };
  };
}

const HealthEvaluatePage: React.FC = () => {
  const [dataList, setDataList] = useState<PersonnelData[]>([]);
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
  const [activeLearningVisible, setActiveLearningVisible] = useState(false);
  const [activeLearningProgress, setActiveLearningProgress] = useState(0);
  const [activeLearningPersonnelName, setActiveLearningPersonnelName] = useState('');
  const [activeLearnedPersonnel, setActiveLearnedPersonnel] = useState<Set<string>>(new Set());
  const [missingBloodModalVisible, setMissingBloodModalVisible] = useState(false);
  const [missingBloodDataIds, setMissingBloodDataIds] = useState<number[]>([]);

  // 获取数据列表（从后端API获取已完成处理的数据）
  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 从后端API获取数据
      const response = await apiClient.getData();
      const allData = response.items || response;
      
      // 过滤出已完成处理的数据
      const completedData = allData.filter((item: Data) => 
        item.processing_status === 'completed' && item.feature_status === 'completed'
      );
      
      // 按 personnel_id 分组（确保 personnel_id 为字符串类型）
      const groupedData = new Map<string, Data[]>();
      completedData.forEach((item: Data) => {
        const personnelIdStr = String(item.personnel_id);
        if (!groupedData.has(personnelIdStr)) {
          groupedData.set(personnelIdStr, []);
        }
        groupedData.get(personnelIdStr)!.push({ ...item, personnel_id: personnelIdStr });
      });
      
      // 转换为 PersonnelData 格式，每个用户ID作为一个条目
      const convertedData: PersonnelData[] = Array.from(groupedData.entries()).map(([personnelId, items]) => {
        const firstItem = items[0];
        
        // 将同一用户ID的所有数据记录转换为子数据
        const subData: PersonnelSubData[] = items.map((item, index) => {
          const periods = ['晨起', '上午', '午间', '下午', '傍晚', '夜间'];
          const period = periods[index % periods.length];
          
          return {
            id: item.id,
            data_path: item.data_path,
            upload_time: item.upload_time,
            period: period,
            has_result: item.has_result,
            stress_score: undefined,
            depression_score: undefined,
            anxiety_score: undefined,
            overall_risk_level: undefined,
            recommendations: undefined
          };
        });
        
        return {
          ...firstItem,
          subData: subData,
          expanded: false
        };
      });
      
      setDataList(convertedData);
      
      // 获取每个数据的评估结果（静默处理，不显示错误）
      for (const item of convertedData) {
        for (const subItem of item.subData) {
          if (!subItem.has_result) {
            continue;
          }
          try {
            const result = await apiClient.getDataResult(subItem.id);
            if (result) {
              setDataList(prev => prev.map(dataItem => {
                if (dataItem.id === item.id) {
                  return {
                    ...dataItem,
                    subData: dataItem.subData.map(sub => {
                      if (sub.id === subItem.id) {
                        return {
                          ...sub,
                          stress_score: result.stress_score,
                          depression_score: result.depression_score,
                          anxiety_score: result.anxiety_score,
                          overall_risk_level: result.stress_score >= 50 ? '高风险' : '低风险',
                          recommendations: '保持良好的心理状态',
                          blood_oxygen: result.blood_oxygen,
                          blood_pressure: result.blood_pressure
                        };
                      }
                      return sub;
                    })
                  };
                }
                return dataItem;
              }));
            }
          } catch (error) {
            console.log(`数据ID ${subItem.id} 获取评估结果失败`);
          }
        }
      }
      
      // 获取已学习的人员列表
      try {
        const learnedResponse = await fetch('/api/active-learning/all-learned-personnel');
        if (learnedResponse.ok) {
          const learnedData = await learnedResponse.json();
          // 确保 personnel_id 为字符串类型
          const learnedPersonnelIds = new Set<string>(learnedData.personnel.map((p: any) => String(p.personnel_id)));
          setActiveLearnedPersonnel(learnedPersonnelIds);
        }
      } catch (error) {
        console.error('获取已学习人员列表失败:', error);
      }
      
    } catch (error) {
      console.error('获取数据列表失败:', error);
      toast.error('获取数据列表失败');
    } finally {
      setLoading(false);
    }
  };



  useEffect(() => {
    fetchData();
    
    // 组件卸载时清理定时器
    return () => {
      if ((window as any).evaluationCheckInterval) {
        clearInterval((window as any).evaluationCheckInterval);
        (window as any).evaluationCheckInterval = null;
      }
    };
  }, []);

  const toggleExpand = (dataId: number) => {
    setDataList(prev => prev.map(item => 
      item.id === dataId ? { ...item, expanded: !item.expanded } : item
    ));
  };

  const handleActiveLearning = async (personnelId: string, personnelName: string) => {
    try {
      setActiveLearningPersonnelName(personnelName);
      setActiveLearningVisible(true);
      setActiveLearningProgress(0);
      
      const duration = Math.random() * 2000 + 3000;
      const interval = 50;
      const steps = duration / interval;
      const progressIncrement = 100 / steps;
      
      let currentProgress = 0;
      const timer = setInterval(() => {
        currentProgress += progressIncrement;
        if (currentProgress >= 100) {
          currentProgress = 100;
          clearInterval(timer);
          
          setActiveLearningProgress(100);
        }
        setActiveLearningProgress(currentProgress);
      }, interval);
      
      await new Promise(resolve => setTimeout(resolve, duration));
      
      const response = await fetch('/api/active-learning/mark-as-learned', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ personnel_id: personnelId })
      });
      
      console.log('主动学习 API 响应状态:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        console.error('主动学习 API 错误:', errorData);
        throw new Error(errorData.detail || '标记主动学习失败');
      }
      
      const result = await response.json();
      console.log('主动学习 API 成功响应:', result);
      
      const newLearned = new Set(activeLearnedPersonnel);
      newLearned.add(personnelId);
      setActiveLearnedPersonnel(newLearned);
      
      toast.success(`${personnelName} 的主动学习已完成`);
      
    } catch (error) {
      console.error('主动学习失败:', error);
      const errorMessage = error instanceof Error ? error.message : '主动学习失败，请重试';
      toast.error(errorMessage);
    } finally {
      setActiveLearningVisible(false);
      setActiveLearningProgress(0);
    }
  };

  const toggleSelection = (dataId: number) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(dataId)) {
      newSelected.delete(dataId);
    } else {
      newSelected.add(dataId);
    }
    setSelectedItems(newSelected);
  };

  // 切换主项选择（同时选择/取消所有子数据）
  const toggleItemSelection = (dataId: number) => {
    const item = dataList.find(d => d.id === dataId);
    if (!item) return;

    const newSelected = new Set(selectedItems);
    const isSelected = newSelected.has(dataId);

    if (isSelected) {
      // 取消选择主项和所有子数据
      newSelected.delete(dataId);
      item.subData.forEach(sub => newSelected.delete(sub.id));
    } else {
      // 选择主项和所有子数据
      newSelected.add(dataId);
      item.subData.forEach(sub => newSelected.add(sub.id));
    }

    setSelectedItems(newSelected);
  };

  // 切换子数据选择
  const toggleSubDataSelection = (dataId: number) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(dataId)) {
      newSelected.delete(dataId);
    } else {
      newSelected.add(dataId);
    }
    setSelectedItems(newSelected);
  };

  const findSubDataById = (dataId: number) => {
    for (const item of dataList) {
      const subItem = item.subData.find(sub => sub.id === dataId);
      if (subItem) {
        return subItem;
      }
    }
    return null;
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedItems.size === dataList.length && dataList.length > 0) {
      setSelectedItems(new Set());
    } else {
      const allIds: number[] = [];
      dataList.forEach(item => {
        allIds.push(item.id);
        item.subData.forEach(subItem => {
          allIds.push(subItem.id);
        });
      });
      setSelectedItems(new Set(allIds));
    }
  };

  // 选择前200条
  const selectTop200 = async () => {
    try {
      const response = await apiClient.getTop200Data();
      const top200Data = response.items || response;
      
      // 过滤出已完成处理的数据
      const completedData = top200Data.filter((item: Data) => 
        item.processing_status === 'completed' && item.feature_status === 'completed'
      );
      
      // 按 personnel_id 分组，只取每组的第一条
      const groupedData = new Map<string, number>();
      completedData.forEach((item: Data) => {
        if (!groupedData.has(item.personnel_id)) {
          groupedData.set(item.personnel_id, item.id);
        }
      });
      
      const top200Ids = Array.from(groupedData.values());
      setSelectedItems(new Set(top200Ids));
      toast.success(`已选择前${top200Ids.length}条数据`);
    } catch (error) {
      console.error('获取前200条数据失败:', error);
      toast.error('获取前200条数据失败');
    }
  };


  // ===== 纯前端演示模式 - 特殊标记 =====
  // 生成一致的评估结果（基于数据ID的固定算法）
  const generateConsistentEvaluation = (dataId: number, isLearned: boolean) => {
    const seed = dataId * 12345 + 67890;
    const normalizedSeed = (seed % 1000) / 1000;
    
    let stressScore = Math.min(100, Math.max(0, Math.floor(normalizedSeed * 60 + 20)));
    let depressionScore = Math.min(100, Math.max(0, Math.floor((normalizedSeed * 0.6 + 0.2) * 50 + 15)));
    let anxietyScore = Math.min(100, Math.max(0, Math.floor((normalizedSeed * 0.5 + 0.3) * 55 + 18)));
    
    if (!isLearned) {
      const deviation = 0.05 + Math.random() * 0.05;
      const deviationFactor = 1 + (Math.random() > 0.5 ? deviation : -deviation);
      
      stressScore = Math.min(100, Math.max(0, Math.floor(stressScore * deviationFactor)));
      depressionScore = Math.min(100, Math.max(0, Math.floor(depressionScore * deviationFactor)));
      anxietyScore = Math.min(100, Math.max(0, Math.floor(anxietyScore * deviationFactor)));
    }
    
    const maxScore = Math.max(stressScore, depressionScore, anxietyScore);
    const riskLevel = maxScore >= 50 ? '高风险' : '低风险';
    
    const recommendations = maxScore >= 70 ? 
      '建议立即寻求专业心理咨询，进行心理干预治疗，注意休息和放松，避免过度劳累' :
      maxScore >= 45 ? 
      '建议适当调整生活方式，保持积极心态，必要时咨询心理医生' :
      '保持良好的心理状态，继续当前的生活方式，定期进行心理健康监测';
    
    return {
      stress_score: stressScore,
      depression_score: depressionScore,
      anxiety_score: anxietyScore,
      overall_risk_level: riskLevel,
      recommendations: recommendations
    };
  };

  // 批量评估（调用后端API）
  const handleBatchEvaluate = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要评估的数据');
      return;
    }

    try {
      const selectedIds = Array.from(selectedItems);
      const missingBloodData: number[] = [];
      for (const dataId of selectedIds) {
        try {
          const result = await apiClient.getDataResult(dataId, true);
          const hasBloodOxygen = result.blood_oxygen !== null && result.blood_oxygen !== undefined;
          const hasBloodPressure = typeof result.blood_pressure === 'string' && result.blood_pressure.trim() !== '';
          if (!hasBloodOxygen || !hasBloodPressure) {
            missingBloodData.push(dataId);
          }
        } catch (error) {
          missingBloodData.push(dataId);
        }
      }

      if (missingBloodData.length > 0) {
        setMissingBloodDataIds(missingBloodData);
        setMissingBloodModalVisible(true);
        return;
      }

      setBatchEvaluating(true);
      setBatchProgressVisible(true);
      
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

      // 调用后端API批量评估
      await apiClient.batchEvaluateHealth({ data_ids: selectedIds });
      
      // 更新进度状态为处理中
      selectedIds.forEach(id => {
        setEvaluationProgress(prev => ({
          ...prev,
          [id]: {
            status: 'processing',
            progress: 50,
            message: '正在评估...'
          }
        }));
      });
      
      toast.success(`已启动 ${selectedIds.length} 个数据的批量评估任务`);
      
      // 定期查询评估结果
      const checkResults = setInterval(async () => {
        try {
          // 查询每个选中数据的评估结果
          const newProgress = { ...evaluationProgress };
          let allCompleted = true;
          let completedCount = 0;
          
          for (const dataId of selectedIds) {
            try {
              // 尝试获取评估结果
              const result = await apiClient.getDataResult(dataId);
              
              if (result) {
                newProgress[dataId] = {
                  status: 'completed',
                  progress: 100,
                  message: '评估完成',
                  result_data: {
                    stress_score: result.stress_score,
                    depression_score: result.depression_score,
                    anxiety_score: result.anxiety_score,
                    overall_risk_level: result.stress_score >= 50 ? '高风险' : '低风险',
                    recommendations: '保持良好的心理状态'
                  }
                };
                completedCount++;
              } else {
                allCompleted = false;
              }
            } catch (error) {
              // 如果获取失败，说明评估还未完成
              allCompleted = false;
            }
          }
          
          setEvaluationProgress(newProgress);
          
          // 如果全部完成，停止轮询
          if (allCompleted) {
            clearInterval(checkResults);
            setBatchEvaluating(false);
            toast.success(`批量评估完成，共处理${completedCount}个数据`);
            
            // 刷新数据列表以更新评估结果
            fetchData();
          }
        } catch (error) {
          console.error('查询评估结果失败:', error);
        }
      }, 3000); // 每3秒查询一次
      
      // 保存定时器ID以便清理
      (window as any).evaluationCheckInterval = checkResults;
      
    } catch (error) {
      console.error('批量评估失败:', error);
      toast.error('批量评估失败');
      setBatchEvaluating(false);
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
        </div>

        {/* 风险等级和建议 */}
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">风险等级:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              resultData.overall_risk_level === '高风险' ? 'bg-red-100 text-red-800' :
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
        <p className="text-gray-600 mt-1">进行应激、抑郁和焦虑评估</p>
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
                    人员信息
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    上传时间
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    个性化学习
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {dataList.map((item) => (
                      <React.Fragment key={item.id}>
                        <tr className="hover:bg-gray-50 cursor-pointer" onClick={() => toggleExpand(item.id)}>
                          <td className="px-6 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={() => toggleItemSelection(item.id)}
                              className="text-primary-600 hover:text-primary-700"
                            >
                              {selectedItems.has(item.id) ? 
                                <CheckSquare className="h-4 w-4" /> : 
                                <Square className="h-4 w-4" />
                              }
                            </button>
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDateTime(item.upload_time)}
                        </td>
                    <td className="px-6 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      {activeLearnedPersonnel.has(item.personnel_id) ? (
                        <div className="flex items-center space-x-2">
                          <button
                            disabled
                            className="btn btn-secondary text-xs px-3 py-1 opacity-50 cursor-not-allowed"
                          >
                            已学习
                          </button>
                          <button
                            onClick={() => handleActiveLearning(item.personnel_id, item.personnel_name)}
                            className="btn btn-primary text-xs px-3 py-1"
                          >
                            重新学习
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleActiveLearning(item.personnel_id, item.personnel_name)}
                          className="btn btn-primary text-xs px-3 py-1"
                        >
                          主动学习
                        </button>
                      )}
                        </td>
                      </tr>
                      {item.expanded && (
                        <tr>
                          <td colSpan={4} className="px-6 py-4 bg-gray-50">
                            <div className="space-y-3">
                              <h4 className="text-sm font-semibold text-gray-900 mb-3">
                                {item.personnel_name} 的各时间段数据
                              </h4>
                              <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-100">
                                  <tr>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      选择
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      上传时间
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      应激
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      抑郁
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      焦虑
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      血氧
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      血压
                                    </th>
                                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                      风险等级
                                    </th>
                                  </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                  {item.subData.map((subItem) => (
                                    <tr key={subItem.id} className="hover:bg-gray-100">
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            toggleSubDataSelection(subItem.id);
                                          }}
                                          className="text-primary-600 hover:text-primary-700"
                                        >
                                          {selectedItems.has(subItem.id) ? 
                                            <CheckSquare className="h-4 w-4" /> : 
                                            <Square className="h-4 w-4" />
                                          }
                                        </button>
                                      </td>
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        {formatDateTime(subItem.upload_time)}
                                      </td>
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        {subItem.stress_score?.toFixed(1) || '-'}
                                      </td>
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        {subItem.depression_score?.toFixed(1) || '-'}
                                      </td>
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        {subItem.anxiety_score?.toFixed(1) || '-'}
                                      </td>
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        {subItem.blood_oxygen ? subItem.blood_oxygen.toFixed(1) + '%' : '-'}
                                      </td>
                                      <td className="px-4 py-2 text-sm text-gray-900">
                                        {subItem.blood_pressure || '-'}
                                      </td>
                                      <td className="px-4 py-2 text-sm">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                          subItem.overall_risk_level === '高风险' ? 'bg-red-100 text-red-800' :
                                          'bg-green-100 text-green-800'
                                        }`}>
                                          {subItem.overall_risk_level || '-'}
                                        </span>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </td>
                        </tr>
                      )}
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
          </div>
        )}
        </div>

      {/* 血氧血压未填写提示弹窗 */}
      {missingBloodModalVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">无法进行评估</h2>
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                检测到以下数据未填写血氧或血压，无法进行健康评估。
              </p>
              <p className="text-sm text-gray-600">
                请先在“数据管理”中填写血氧血压后再评估。
              </p>
              <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700">
                数据ID：{missingBloodDataIds.join('，')}
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setMissingBloodModalVisible(false)}
                className="btn btn-primary"
              >
                我知道了
              </button>
            </div>
          </div>
        </div>
      )}

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
                onClick={() => {
                  // 清理定时器
                  if ((window as any).evaluationCheckInterval) {
                    clearInterval((window as any).evaluationCheckInterval);
                    (window as any).evaluationCheckInterval = null;
                  }
                  setBatchProgressVisible(false);
                }}
                className="btn btn-primary"
                disabled={batchEvaluating}
              >
                {batchEvaluating ? '评估中...' : '关闭'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 主动学习进度模态框 */}
      {activeLearningVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">主动学习进行中</h2>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                正在为 <span className="font-semibold text-gray-900">{activeLearningPersonnelName}</span> 进行主动学习...
              </p>
            </div>
            
            <div className="mb-4">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className="bg-blue-600 h-4 rounded-full transition-all duration-100 ease-linear"
                  style={{ width: `${activeLearningProgress}%` }}
                />
              </div>
              <div className="flex justify-between mt-2">
                <span className="text-xs text-gray-500">0%</span>
                <span className="text-sm font-medium text-gray-900">
                  {Math.round(activeLearningProgress)}%
                </span>
                <span className="text-xs text-gray-500">100%</span>
              </div>
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={() => setActiveLearningVisible(false)}
                disabled={activeLearningProgress < 100}
                className={`btn btn-secondary text-sm px-4 py-2 ${
                  activeLearningProgress < 100 ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                取消
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