import React, { useState, useEffect, useRef } from 'react';
import { X, AlertCircle, CheckCircle, Clock, Play } from 'lucide-react';
import { PreprocessProgress } from '@/types';
import { apiClient } from '@/utils/api';
import ProgressBar from './ProgressBar';

interface ProgressModalProps {
  visible: boolean;
  onClose: () => void;
  dataIds: number[];
  title?: string;
}

const ProgressModal: React.FC<ProgressModalProps> = ({
  visible,
  onClose,
  dataIds,
  title = '批量预处理进度'
}) => {
  const [progressList, setProgressList] = useState<PreprocessProgress[]>([]);
  const [loading, setLoading] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [simulatedProgress, setSimulatedProgress] = useState<{[key: number]: number}>({});
  const startTimeRef = useRef<{[key: number]: number}>({});

  // 计算模拟进度（60秒内从0%增长到99%）
  const calculateSimulatedProgress = (dataId: number, actualStatus: string, actualFeatureStatus: string) => {
    // 如果真正完成了，返回100%
    if (actualStatus === 'completed' && actualFeatureStatus === 'completed') {
      return 100;
    }
    
    // 如果失败了，返回实际进度
    if (actualStatus === 'failed' || actualFeatureStatus === 'failed') {
      return 0;
    }
    
    // 如果还是pending，返回0
    if (actualStatus === 'pending') {
      return 0;
    }
    
    // 如果正在处理中，计算模拟进度
    if (actualStatus === 'processing' || actualFeatureStatus === 'processing') {
      // 记录开始时间
      if (!startTimeRef.current[dataId]) {
        startTimeRef.current[dataId] = Date.now();
      }
      
      const elapsed = (Date.now() - startTimeRef.current[dataId]) / 1000; // 转换为秒
      const maxTime = 60; // 60秒
      const maxProgress = 99; // 最大99%
      
      // 使用指数增长模拟，前期快，后期慢
      const progress = Math.min(maxProgress, maxProgress * (1 - Math.exp(-elapsed / (maxTime / 3))));
      
      return Math.round(progress);
    }
    
    return 0;
  };

  const fetchProgress = async () => {
    if (dataIds.length === 0) return;
    
    try {
      setLoading(true);
      const response = await apiClient.getBatchProgress(dataIds);
      
      // 为每个数据计算模拟进度
      const updatedSimulatedProgress = { ...simulatedProgress };
      const updatedProgressList = response.map((item: PreprocessProgress) => {
        const simulated = calculateSimulatedProgress(
          item.data_id, 
          item.processing_status, 
          item.feature_status
        );
        updatedSimulatedProgress[item.data_id] = simulated;
        
        return {
          ...item,
          progress_percentage: simulated
        };
      });
      
      setSimulatedProgress(updatedSimulatedProgress);
      setProgressList(updatedProgressList);
      
      // 计算总体进度
      const totalProgress = updatedProgressList.reduce((sum: number, item: any) => sum + item.progress_percentage, 0);
      const avgProgress = Math.round(totalProgress / updatedProgressList.length);
      setOverallProgress(avgProgress);
      
      // 检查是否全部完成
      const allCompleted = response.every((item: PreprocessProgress) => 
        item.processing_status === 'completed' && item.feature_status === 'completed'
      );
      setIsCompleted(allCompleted);
      
    } catch (error) {
      console.error('获取进度失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible && dataIds.length > 0) {
      // 重置开始时间
      startTimeRef.current = {};
      setSimulatedProgress({});
      
      fetchProgress();
      
      // 如果没有全部完成，每1秒刷新一次进度（更频繁以显示模拟进度）
      const interval = setInterval(() => {
        if (!isCompleted) {
          fetchProgress();
        }
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [visible, dataIds, isCompleted]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'processing':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <Play className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (processingStatus: string, featureStatus: string) => {
    if (processingStatus === 'completed' && featureStatus === 'completed') {
      return '预处理和特征提取已完成';
    } else if (processingStatus === 'completed' && featureStatus === 'processing') {
      return '预处理完成，特征提取中';
    } else if (processingStatus === 'processing') {
      return '数据预处理中';
    } else if (processingStatus === 'failed' || featureStatus === 'failed') {
      return '处理失败';
    } else {
      return '等待处理';
    }
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* 总体进度 */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">总体进度</span>
            <span className="text-sm text-gray-500">{progressList.length} 个数据</span>
          </div>
          <ProgressBar
            progress={overallProgress}
            status={isCompleted ? 'completed' : 'processing'}
            size="large"
            showIcon={false}
          />
        </div>

        {/* 详细进度列表 */}
        <div className="max-h-96 overflow-y-auto">
          {loading && progressList.length === 0 ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-500 mt-2">加载进度信息...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {progressList.map((item) => (
                <div key={item.data_id} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(item.processing_status === 'failed' || item.feature_status === 'failed' ? 'failed' : 
                                   item.processing_status === 'completed' && item.feature_status === 'completed' ? 'completed' : 'processing')}
                      <span className="font-medium text-gray-900">{item.personnel_name}</span>
                      <span className="text-sm text-gray-500">ID: {item.data_id}</span>
                    </div>
                    <span className={`text-sm ${getStatusColor(item.processing_status)}`}>
                      {getStatusText(item.processing_status, item.feature_status)}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <ProgressBar
                      progress={item.progress_percentage}
                      status={item.processing_status === 'failed' || item.feature_status === 'failed' ? 'failed' : 
                             item.processing_status === 'completed' && item.feature_status === 'completed' ? 'completed' : 'processing'}
                      title="预处理进度"
                      size="small"
                    />
                    
                    {item.message && (
                      <p className="text-xs text-gray-600 mt-1">{item.message}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex justify-end mt-6 space-x-3">
          <button
            onClick={fetchProgress}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 disabled:opacity-50"
          >
            {loading ? '刷新中...' : '刷新进度'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {isCompleted ? '完成' : '最小化'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProgressModal; 