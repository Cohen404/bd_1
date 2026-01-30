import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Upload, 
  Search, 
  Trash2, 
  Settings,
  Eye,
  BarChart3,
  CheckSquare,
  Square,
  RefreshCw,
  FileImage,
  ArrowLeft,
  ArrowRight,
  Play,
  CheckCircle,
  Clock,
  XCircle,
  Heart
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Data } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';
import ProgressBar from '@/components/Common/ProgressBar';
import ProgressModal from '@/components/Common/ProgressModal';
import ConfirmDialog from '@/components/Common/ConfirmDialog';
import EEGVisualization from '@/components/EEGVisualization';

const DataManagePage: React.FC = () => {
  const [dataList, setDataList] = useState<Data[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [batchUploadModalVisible, setBatchUploadModalVisible] = useState(false);
  const [imageViewerVisible, setImageViewerVisible] = useState(false);
  const [preprocessingModalVisible, setPreprocessingModalVisible] = useState(false);
  const [showVisualization, setShowVisualization] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [batchUploading, setBatchUploading] = useState(false);
  const [preprocessing, setPreprocessing] = useState(false);
  const [selectedDataId, setSelectedDataId] = useState<number | null>(null);
  const [currentImageData, setCurrentImageData] = useState<{
    dataId: number;
    images: any[];
    currentIndex: number;
  } | null>(null);
  const [formData, setFormData] = useState({
    personnel_id: '',
    personnel_name: '',
    file: null as File | null
  });
  const [batchFiles, setBatchFiles] = useState<FileList | null>(null);
  const [progressModalVisible, setProgressModalVisible] = useState(false);
  const [progressDataIds, setProgressDataIds] = useState<number[]>([]);
  const [processingStartTimes, setProcessingStartTimes] = useState<{[key: number]: number}>({});
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{id: number, name: string} | null>(null);
  const [batchDeleteConfirmVisible, setBatchDeleteConfirmVisible] = useState(false);
  const [bloodModalVisible, setBloodModalVisible] = useState(false);
  const [editingDataId, setEditingDataId] = useState<number | null>(null);
  const [bloodOxygen, setBloodOxygen] = useState('');
  const [bloodPressure, setBloodPressure] = useState('');

  // 图像类型选项
  const imageTypes = [
    { key: 'theta', label: 'Theta功率特征图' },
    { key: 'alpha', label: 'Alpha功率特征图' },
    { key: 'beta', label: 'Beta功率特征图' },
    { key: 'gamma', label: 'Gamma功率特征图' },
    { key: 'frequency_band_1', label: '均分频带1特征图' },
    { key: 'frequency_band_2', label: '均分频带2特征图' },
    { key: 'frequency_band_3', label: '均分频带3特征图' },
    { key: 'frequency_band_4', label: '均分频带4特征图' },
    { key: 'frequency_band_5', label: '均分频带5特征图' },
    { key: 'time_zero_crossing', label: '时域特征-过零率' },
    { key: 'time_variance', label: '时域特征-方差' },
    { key: 'time_energy', label: '时域特征-能量' },
    { key: 'time_difference', label: '时域特征-差分' },
    { key: 'frequency_wavelet', label: '时频域特征图' },
    { key: 'differential_entropy', label: '微分熵特征图' }
  ];

  // 获取数据列表（从后端API读取）
  const fetchData = async () => {
    try {
      setLoading(true);
      
      const response = await apiClient.getData();
      setDataList(response.items || response);
    } catch (error) {
      console.error('获取数据列表失败:', error);
      toast.error('获取数据列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取状态图标和颜色
  const getStatusIcon = (processingStatus: string, featureStatus: string) => {
    if (processingStatus === 'failed' || featureStatus === 'failed') {
      return <XCircle className="h-4 w-4 text-red-500" />;
    } else if (processingStatus === 'completed' && featureStatus === 'completed') {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    } else if (processingStatus === 'processing' || featureStatus === 'processing') {
      return <Play className="h-4 w-4 text-blue-500 animate-spin" />;
    } else {
      return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  // 获取状态文本
  const getStatusText = (processingStatus: string, featureStatus: string) => {
    if (processingStatus === 'failed' || featureStatus === 'failed') {
      return '处理失败';
    } else if (processingStatus === 'completed' && featureStatus === 'completed') {
      return '已完成';
    } else if (processingStatus === 'completed' && featureStatus === 'processing') {
      return '特征提取中';
    } else if (processingStatus === 'processing') {
      return '预处理中';
    } else {
      return '待处理';
    }
  };

  // 计算进度百分比（支持模拟进度）
  const getProgressPercentage = (dataId: number, processingStatus: string, featureStatus: string) => {
    // 如果真正完成了，返回100%
    if (processingStatus === 'completed' && featureStatus === 'completed') {
      return 100;
    }
    
    // 如果失败了，返回0
    if (processingStatus === 'failed' || featureStatus === 'failed') {
      return 0;
    }
    
    // 如果还是pending，返回0
    if (processingStatus === 'pending') {
      return 0;
    }
    
    // 如果正在处理中，计算模拟进度
    if (processingStatus === 'processing' || featureStatus === 'processing') {
      // 记录开始时间
      if (!processingStartTimes[dataId]) {
        const newStartTimes = { ...processingStartTimes };
        newStartTimes[dataId] = Date.now();
        setProcessingStartTimes(newStartTimes);
        return 0;
      }
      
      const elapsed = (Date.now() - processingStartTimes[dataId]) / 1000; // 转换为秒
      const maxTime = 4; // 4秒（3-5秒的中间值）
      const maxProgress = 99; // 最大99%
      
      // 使用指数增长模拟，前期快，后期慢，加入随机波动
      const baseProgress = maxProgress * (1 - Math.exp(-elapsed / (maxTime / 3)));
      // 添加±5%的随机波动
      const randomFactor = 1 + (Math.random() * 0.1 - 0.05);
      const progress = Math.min(maxProgress, baseProgress * randomFactor);
      
      const simulated = Math.round(progress);
      
      return simulated;
    }
    
    return 0;
  };

  useEffect(() => {
    fetchData();
  }, [searchTerm]);

  // 定期更新进度（用于显示模拟进度）
  useEffect(() => {
    const interval = setInterval(() => {
      // 检查是否有正在处理的数据
      const hasProcessing = dataList.some(item => 
        item.processing_status === 'processing' || item.feature_status === 'processing'
      );
      
      if (hasProcessing) {
        // 强制重新渲染以更新进度条
        setDataList(prev => [...prev]);
      }
    }, 1000); // 每秒更新一次
    
    return () => clearInterval(interval);
  }, [dataList]);

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

  // 选择前200条（从后端API读取）
  const selectTop200 = async () => {
    try {
      const response = await apiClient.getTop200Data();
      const top200Ids = response.items.map((item: Data) => item.id);
      setSelectedItems(new Set(top200Ids));
      toast.success(`已选择前${top200Ids.length}条数据`);
    } catch (error) {
      console.error('获取前200条数据失败:', error);
      toast.error('获取前200条数据失败');
    }
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedItems.size === filteredData.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredData.map(item => item.id)));
    }
  };

  // 上传文件（调用后端API）
  const handleUpload = async () => {
    if (!formData.file || !formData.personnel_id || !formData.personnel_name) {
      toast.error('请填写完整信息并选择文件');
      return;
    }

    try {
      setUploading(true);
      
      // 创建FormData
      const formDataToSend = new FormData();
      formDataToSend.append('file', formData.file);
      formDataToSend.append('personnel_id', formData.personnel_id);
      formDataToSend.append('personnel_name', formData.personnel_name);
      
      // 调用后端API上传
      await apiClient.uploadData(formDataToSend);
      
      toast.success('数据上传成功！');
      setUploadModalVisible(false);
      setFormData({ personnel_id: '', personnel_name: '', file: null });
      fetchData();
    } catch (error) {
      console.error('数据上传失败:', error);
      toast.error('数据上传失败');
    } finally {
      setUploading(false);
    }
  };

  // 批量上传文件（调用后端API）
  const handleBatchUpload = async () => {
    if (!batchFiles || batchFiles.length === 0) {
      toast.error('请选择要上传的文件');
      return;
    }

    try {
      setBatchUploading(true);
      
      // 创建FormData
      const formDataToSend = new FormData();
      Array.from(batchFiles).forEach((file) => {
        formDataToSend.append('files', file);
      });
      
      // 调用后端API批量上传
      const response = await apiClient.batchUploadData(formDataToSend);
      
      if (response.failed_count > 0) {
        // 如果有失败，显示错误信息
        if (response.errors && response.errors.length > 0) {
          response.errors.forEach((error: string) => {
            console.error('上传错误:', error);
            toast.error(error);
          });
        }
      }
      
      if (response.success_count > 0) {
        toast.success(`成功上传 ${response.success_count} 个文件`);
      }
      
      setBatchUploadModalVisible(false);
      setBatchFiles(null);
      fetchData();
    } catch (error) {
      console.error('批量上传失败:', error);
      toast.error('批量上传失败');
    } finally {
      setBatchUploading(false);
    }
  };

  // 批量预处理（调用后端API）
  const handleBatchPreprocess = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要预处理的数据');
      return;
    }

    try {
      setPreprocessing(true);
      
      const selectedIds = Array.from(selectedItems);

      // 检查血氧血压是否已填写
      const missingIds: number[] = [];
      for (const dataId of selectedIds) {
        try {
          const result = await apiClient.getDataResult(dataId, true);
          const hasBloodOxygen = result.blood_oxygen !== null && result.blood_oxygen !== undefined;
          const hasBloodPressure = typeof result.blood_pressure === 'string' && result.blood_pressure.trim() !== '';
          if (!hasBloodOxygen || !hasBloodPressure) {
            missingIds.push(dataId);
          }
        } catch (error) {
          missingIds.push(dataId);
        }
      }

      if (missingIds.length > 0) {
        toast.error(`以下数据未填写血氧血压，无法预处理：${missingIds.join('，')}`);
        return;
      }
      
      // 调用后端API批量预处理
      await apiClient.batchPreprocessData({ data_ids: selectedIds });
      
      toast.success(`已开始预处理 ${selectedIds.length} 条数据`);
      
      // 打开进度模态框
      setProgressDataIds(selectedIds);
      setProgressModalVisible(true);
      
      fetchData();
    } catch (error) {
      console.error('批量预处理失败:', error);
      toast.error('批量预处理失败');
    } finally {
      setPreprocessing(false);
    }
  };

  // 批量删除（调用后端API）
  const handleBatchDelete = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要删除的数据');
      return;
    }

    setBatchDeleteConfirmVisible(true);
  };

  const confirmBatchDelete = async () => {
    try {
      const selectedIds = Array.from(selectedItems);
      
      // 调用后端API批量删除
      await apiClient.batchDeleteData({ data_ids: selectedIds });
      
      toast.success(`已删除${selectedIds.length}条数据`);
      setSelectedItems(new Set());
      setBatchDeleteConfirmVisible(false);
      fetchData();
    } catch (error) {
      console.error('批量删除失败:', error);
      toast.error('批量删除失败');
    }
  };

  // 单个数据预处理（调用后端API）
  const handlePreprocessSingle = async (dataId: number, fileName: string) => {
    try {
      const result = await apiClient.getDataResult(dataId, true);
      const hasBloodOxygen = result.blood_oxygen !== null && result.blood_oxygen !== undefined;
      const hasBloodPressure = typeof result.blood_pressure === 'string' && result.blood_pressure.trim() !== '';
      if (!hasBloodOxygen || !hasBloodPressure) {
        toast.error('请先填写血氧血压后再进行预处理');
        return;
      }

      // 调用后端API预处理
      await apiClient.preprocessData(dataId);
      
      toast.success(`已开始预处理"${fileName}"`);
      
      // 打开进度模态框
      setProgressDataIds([dataId]);
      setProgressModalVisible(true);
      
      fetchData();
    } catch (error) {
      console.error('数据预处理失败:', error);
      toast.error('数据预处理失败');
    }
  };

  // 删除单个数据（调用后端API）
  const handleDeleteSingle = async (dataId: number, fileName: string) => {
    setDeleteTarget({ id: dataId, name: fileName });
    setDeleteConfirmVisible(true);
  };

  const confirmDeleteSingle = async () => {
    if (!deleteTarget) return;

    try {
      // 调用后端API删除
      await apiClient.deleteData(deleteTarget.id);
      
      toast.success('数据删除成功');
      setDeleteConfirmVisible(false);
      setDeleteTarget(null);
      fetchData();
    } catch (error) {
      console.error('删除数据失败:', error);
      toast.error('删除数据失败');
    }
  };

  // 打开血氧血压输入弹窗
  const handleOpenBloodModal = async (dataId: number) => {
    try {
      // 获取该数据对应的评估结果
      const result = await apiClient.getDataResult(dataId, true);
      
      setEditingDataId(dataId);
      setBloodOxygen(result.blood_oxygen ? result.blood_oxygen.toString() : '');
      setBloodPressure(result.blood_pressure || '');
      setBloodModalVisible(true);
    } catch (error) {
      console.error('获取评估结果失败:', error);
      toast.error('该数据尚未进行健康评估，无法输入血氧血压');
    }
  };

  // 保存血氧血压
  const handleSaveBloodData = async () => {
    if (!editingDataId) return;

    try {
      console.log('开始保存血氧血压，dataId:', editingDataId);
      
      // 获取该数据对应的评估结果
      const result = await apiClient.getDataResult(editingDataId, true);
      console.log('获取到的结果:', result);
      
      // 调用后端API更新结果
      await apiClient.updateResult(result.id, {
        blood_oxygen: bloodOxygen ? parseFloat(bloodOxygen) : null,
        blood_pressure: bloodPressure || null
      });
      console.log('更新成功');
      
      // 刷新数据列表
      await fetchData();
      
      // 关闭弹窗
      setBloodModalVisible(false);
      setEditingDataId(null);
      setBloodOxygen('');
      setBloodPressure('');
      
      toast.success('血氧血压保存成功');
    } catch (error) {
      console.error('保存血氧血压失败:', error);
      toast.error('保存血氧血压失败');
    }
  };

  // 查看数据图像（调用后端API）
  const handleViewImages = async (dataId: number) => {
    try {
      const response = await apiClient.getDataImages(dataId);
      
      setCurrentImageData({
        dataId,
        images: response.images || [],
        currentIndex: 0
      });
      setImageViewerVisible(true);
    } catch (error) {
      console.error('获取图像列表失败:', error);
      toast.error('获取图像列表失败');
    }
  };

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 处理可视化显示（使用EEG图表）
  const handleVisualizationDisplay = () => {
    if (!selectedDataId) {
      toast.error('请先选择数据');
      return;
    }
    
    const data = dataList.find(item => item.id === selectedDataId);
    if (!data) {
      toast.error('找不到选中的数据');
      return;
    }
    
    if (data.processing_status !== 'completed' || data.feature_status !== 'completed') {
      toast.error('该数据尚未完成预处理，无法查看可视化');
      return;
    }
    
    setShowVisualization(true);
    toast.success('正在显示脑电波形图...');
  };
  // ============================================

  // 选择数据用于可视化
  const handleSelectDataForVisualization = (dataId: number) => {
    const data = dataList.find(item => item.id === dataId);
    if (data && data.processing_status === 'completed' && data.feature_status === 'completed') {
      setSelectedDataId(dataId);
      setShowVisualization(false);
    } else {
      toast.error('该数据尚未完成预处理，无法查看可视化');
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

  // 过滤数据
  const filteredData = dataList.filter(item =>
    item.personnel_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.data_path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    String(item.upload_user).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">数据管理</h1>
        <p className="text-gray-600 mt-1">管理数据文件上传、预处理和可视化</p>
      </div>

      {/* 搜索和操作栏 */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* 搜索 */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="搜索姓名、文件路径或上传用户..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* 操作按钮组 */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setBatchUploadModalVisible(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>上传</span>
          </button>
          <button
            onClick={selectTop200}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <CheckSquare className="h-4 w-4" />
            <span>选择前200条</span>
          </button>
          <button
            onClick={handleBatchPreprocess}
            disabled={selectedItems.size === 0 || preprocessing}
            className="btn btn-secondary flex items-center space-x-2 disabled:opacity-50"
          >
            {preprocessing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Settings className="h-4 w-4" />}
            <span>批量预处理</span>
          </button>
          <button
            onClick={handleBatchDelete}
            disabled={selectedItems.size === 0}
            className="btn btn-secondary flex items-center space-x-2 disabled:opacity-50 text-orange-600 hover:text-orange-700"
          >
            <Trash2 className="h-4 w-4" />
            <span>批量删除</span>
          </button>
        </div>
      </div>

      {/* 选择计数 */}
      {selectedItems.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="text-blue-700 font-medium">
              已选择: {selectedItems.size}/{filteredData.length}
            </span>
            <button
              onClick={() => setSelectedItems(new Set())}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              清除选择
            </button>
          </div>
        </div>
      )}

      {/* 数据表格 */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
            <span className="ml-2 text-gray-500">加载中...</span>
          </div>
        ) : filteredData.length === 0 ? (
          <div className="text-center py-8">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm ? '未找到匹配的数据' : '暂无数据文件'}
            </p>
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
                      {selectedItems.size === filteredData.length ? 
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
                    上传信息
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    处理状态
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredData.map((item) => (
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
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm text-gray-900">用户{item.upload_user}</div>
                        <div className="text-sm text-gray-500">
                          {formatDateTime(item.upload_time)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(item.processing_status, item.feature_status)}
                          <span className="text-sm text-gray-700">
                            {getStatusText(item.processing_status, item.feature_status)}
                          </span>
                        </div>
                                                     <div className="w-24">
                           <ProgressBar
                             progress={getProgressPercentage(item.id, item.processing_status, item.feature_status)}
                             status={item.processing_status === 'failed' || item.feature_status === 'failed' ? 'failed' : 
                                    item.processing_status === 'completed' && item.feature_status === 'completed' ? 'completed' : 
                                    item.processing_status === 'processing' || item.feature_status === 'processing' ? 'processing' : 'pending'}
                             size="small"
                             showIcon={false}
                           />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handlePreprocessSingle(item.id, item.personnel_name)}
                          className="text-green-600 hover:text-green-700"
                          title="预处理"
                        >
                          <Settings className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleSelectDataForVisualization(item.id)}
                          className={item.processing_status === 'completed' && item.feature_status === 'completed' 
                            ? 'text-purple-600 hover:text-purple-700' 
                            : 'text-gray-400 cursor-not-allowed'}
                          title={item.processing_status === 'completed' && item.feature_status === 'completed' 
                            ? '选择用于可视化' 
                            : '需要先完成预处理'}
                          disabled={!(item.processing_status === 'completed' && item.feature_status === 'completed')}
                        >
                          <BarChart3 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleOpenBloodModal(item.id)}
                          className="text-red-500 hover:text-red-600"
                          title="血氧血压"
                        >
                          <Heart className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteSingle(item.id, item.personnel_name)}
                          className="text-red-600 hover:text-red-700"
                          title="删除"
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

      {/* 数据可视化 */}
      <div className="card p-6 bg-primary-50">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 text-center">数据可视化</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 数据选择和控制区域 */}
            <div className="lg:col-span-1 space-y-4">
              {/* 数据选择 */}
              <div>
                <label className="label">选择数据：</label>
                <select
                  className="input"
                  value={selectedDataId || ''}
                  onChange={(e) => {
                    const dataId = e.target.value ? Number(e.target.value) : null;
                    if (dataId) {
                      handleSelectDataForVisualization(dataId);
                    } else {
                      setSelectedDataId(null);
                      setShowVisualization(false);
                    }
                  }}
                >
                  <option value="">请选择数据</option>
                  {filteredData.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.personnel_name} (ID: {item.id})
                    </option>
                  ))}
                </select>
              </div>

              <button 
                className="btn btn-primary w-full flex items-center justify-center space-x-2"
                onClick={handleVisualizationDisplay}
                disabled={!selectedDataId}
              >
                <Eye className="h-4 w-4" />
                <span>显示脑电波形图</span>
              </button>
            </div>

            {/* 可视化图表区域 */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg p-4 min-h-[500px] border-2 border-dashed border-gray-300">
                {showVisualization && selectedDataId ? (
                  <div className="w-full h-full">
                    <EEGVisualization 
                      dataId={selectedDataId}
                    />
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <Database className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">
                        {selectedDataId ? '点击下方按钮查看脑电波形图' : '请先选择数据'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 上传模态框 */}
      {uploadModalVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">上传数据文件</h2>
            
            <div className="space-y-4">
              <div>
                <label className="label">人员ID *</label>
                <input
                  type="text"
                  className="input"
                  value={formData.personnel_id}
                  onChange={(e) => setFormData({ ...formData, personnel_id: e.target.value })}
                  placeholder="请输入人员ID"
                />
              </div>
              
              <div>
                <label className="label">人员姓名 *</label>
                <input
                  type="text"
                  className="input"
                  value={formData.personnel_name}
                  onChange={(e) => setFormData({ ...formData, personnel_name: e.target.value })}
                  placeholder="请输入人员姓名"
                />
              </div>
              
              <div>
                <label className="label">数据文件 *</label>
                <input
                  type="file"
                  accept=".zip"
                  className="input"
                  onChange={(e) => setFormData({ ...formData, file: e.target.files?.[0] || null })}
                />
                <p className="text-xs text-gray-500 mt-1">支持格式：ZIP压缩包（包含数据文件）</p>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setUploadModalVisible(false);
                  setFormData({ personnel_id: '', personnel_name: '', file: null });
                }}
                className="btn btn-secondary"
                disabled={uploading}
              >
                取消
              </button>
              <button
                onClick={handleUpload}
                className="btn btn-primary"
                disabled={uploading}
              >
                {uploading ? '上传中...' : '上传'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 批量上传模态框 */}
      {batchUploadModalVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">单个/批量上传数据文件</h2>
            
            <div className="space-y-4">
              <div>
                <label className="label">选择多个文件 *</label>
                <input
                  type="file"
                  multiple
                  accept=".zip"
                  className="input"
                  onChange={(e) => setBatchFiles(e.target.files)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  支持格式：ZIP压缩包，文件名格式：人员ID_姓名.zip
                </p>
                {batchFiles && (
                  <p className="text-sm text-blue-600 mt-2">
                    已选择 {batchFiles.length} 个文件
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setBatchUploadModalVisible(false);
                  setBatchFiles(null);
                }}
                className="btn btn-secondary"
                disabled={batchUploading}
              >
                取消
              </button>
              <button
                onClick={handleBatchUpload}
                className="btn btn-primary"
                disabled={batchUploading}
              >
                {batchUploading ? '上传中...' : '上传'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 预处理进度模态框 */}
      {preprocessingModalVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">批量预处理进度</h2>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {progressDataIds.map((dataId) => (
                <div key={dataId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">数据ID: {dataId}</span>
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
                    <span className="text-xs text-gray-600">处理中...</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setPreprocessingModalVisible(false)}
                className="btn btn-primary"
                disabled={preprocessing}
              >
                {preprocessing ? '处理中...' : '关闭'}
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
                数据ID: {currentImageData.dataId} - 图像查看器
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
                      console.log('点击图片事件触发');
                      const imageUrl = `/api/health/image/${currentImageData.dataId}/${currentImageData.images[currentImageData.currentIndex]?.image_type}`;
                      console.log('打开图片URL:', imageUrl);
                      const newWindow = window.open(imageUrl, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
                      if (!newWindow) {
                        alert('弹窗被浏览器阻止，请允许弹窗后重试');
                      }
                    }}
                  >
                    <img
                      src={`https://via.placeholder.com/400x300/4F46E5/FFFFFF?text=${encodeURIComponent(currentImageData.images[currentImageData.currentIndex]?.description || '演示图片')}`}
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

      {/* 进度监控弹窗 */}
      <ProgressModal
        visible={progressModalVisible}
        onClose={() => {
          setProgressModalVisible(false);
          setProgressDataIds([]);
          fetchData(); // 关闭时刷新数据以获取最新状态
        }}
        dataIds={progressDataIds}
        title={progressDataIds.length > 1 ? '批量预处理进度' : '数据预处理进度'}
      />

      {/* 单个删除确认对话框 */}
      <ConfirmDialog
        visible={deleteConfirmVisible}
        title="确认删除"
        message={`确定要删除"${deleteTarget?.name}"吗？\n此操作无法撤销。`}
        confirmText="删除"
        cancelText="取消"
        type="danger"
        onConfirm={confirmDeleteSingle}
        onCancel={() => {
          setDeleteConfirmVisible(false);
          setDeleteTarget(null);
        }}
      />

      {/* 批量删除确认对话框 */}
      <ConfirmDialog
        visible={batchDeleteConfirmVisible}
        title="确认批量删除"
        message={`确定要删除选中的 ${selectedItems.size} 条数据吗？\n此操作无法撤销。`}
        confirmText="删除"
        cancelText="取消"
        type="danger"
        onConfirm={confirmBatchDelete}
        onCancel={() => setBatchDeleteConfirmVisible(false)}
      />

      {/* 血氧血压输入弹窗 */}
      {bloodModalVisible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">输入血氧血压</h2>
            
            <div className="space-y-4">
              <div>
                <label className="label">血氧饱和度 (%)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  className="input"
                  value={bloodOxygen}
                  onChange={(e) => setBloodOxygen(e.target.value)}
                  placeholder="请输入血氧饱和度，如：98.5"
                />
              </div>
              
              <div>
                <label className="label">血压 (mmHg)</label>
                <input
                  type="text"
                  className="input"
                  value={bloodPressure}
                  onChange={(e) => setBloodPressure(e.target.value)}
                  placeholder="请输入血压，格式：收缩压/舒张压，如：120/80"
                />
                <p className="text-xs text-gray-500 mt-1">格式示例：120/80</p>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setBloodModalVisible(false);
                  setEditingDataId(null);
                  setBloodOxygen('');
                  setBloodPressure('');
                }}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={handleSaveBloodData}
                className="btn btn-primary"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </>
  );
};

export default DataManagePage; 