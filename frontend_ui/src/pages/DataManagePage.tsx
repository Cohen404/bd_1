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
  Image,
  RefreshCw,
  FileImage,
  ArrowLeft,
  ArrowRight,
  Play,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react';
// ===== 纯前端演示模式 - 特殊标记 =====
// 注释掉后端API相关导入，使用localStorage存储
// import { apiClient } from '@/utils/api';
import { Data } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, DataOperations, initializeDemoData, DataItem } from '@/utils/localStorage';
import toast from 'react-hot-toast';
// ============================================
import ProgressBar from '@/components/Common/ProgressBar';
import ProgressModal from '@/components/Common/ProgressModal';
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
  const [visualizationType, setVisualizationType] = useState('differential_entropy');
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

  // 可视化指标选项（使用具体的图片类型）
  const visualizationOptions = [
    { value: 'differential_entropy', label: '微分熵特征图' },
    { value: 'theta', label: 'Theta功率特征图' },
    { value: 'alpha', label: 'Alpha功率特征图' },
    { value: 'beta', label: 'Beta功率特征图' },
    { value: 'gamma', label: 'Gamma功率特征图' },
    { value: 'frequency_band_1', label: '均分频带1特征图' },
    { value: 'frequency_band_2', label: '均分频带2特征图' },
    { value: 'frequency_band_3', label: '均分频带3特征图' },
    { value: 'frequency_band_4', label: '均分频带4特征图' },
    { value: 'frequency_band_5', label: '均分频带5特征图' },
    { value: 'time_zero_crossing', label: '时域特征-过零率' },
    { value: 'time_variance', label: '时域特征-方差' },
    { value: 'time_energy', label: '时域特征-能量' },
    { value: 'time_difference', label: '时域特征-差分' },
    { value: 'frequency_wavelet', label: '时频域特征图' },
    { value: 'serum_analysis', label: '血清指标分析' }
  ];

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
    { key: 'differential_entropy', label: '微分熵特征图' },
    { key: 'serum_analysis', label: '血清指标分析' }
  ];

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
        id: item.id,
        personnel_id: item.name.split('_')[0] || 'unknown',
        personnel_name: item.name.split('_')[1]?.replace('.csv', '') || item.name,
        data_path: item.file_path,
        upload_time: item.upload_time,
        upload_user: typeof item.uploader === 'string' ? parseInt(item.uploader) || 1 : item.uploader,
        user_id: typeof item.uploader === 'string' ? item.uploader : String(item.uploader),
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
      const maxTime = 60; // 60秒
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

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 选择前200条（从localStorage读取）
  const selectTop200 = async () => {
    try {
      // 获取前200条数据
      const top200Ids = dataList.slice(0, 200).map(item => item.id);
      setSelectedItems(new Set(top200Ids));
      toast.success(`已选择前${top200Ids.length}条数据`);
    } catch (error) {
      console.error('获取前200条数据失败:', error);
      toast.error('获取前200条数据失败');
    }
  };
  // ============================================

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedItems.size === filteredData.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredData.map(item => item.id)));
    }
  };

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 上传文件（保存到localStorage）
  const handleUpload = async () => {
    if (!formData.file || !formData.personnel_id || !formData.personnel_name) {
      toast.error('请填写完整信息并选择文件');
      return;
    }

    try {
      setUploading(true);
      
      // 模拟上传延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 获取现有数据
      const existingData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      
      // 创建新数据项
      const newDataItem: DataItem = {
        id: DataOperations.getNextId(existingData),
        name: `${formData.personnel_id}_${formData.personnel_name}.csv`,
        description: `用户 ${formData.personnel_name} 上传的数据文件`,
        file_path: `/uploads/data/${formData.personnel_id}_${formData.personnel_name}.csv`,
        file_size: formData.file.size,
        upload_time: new Date().toISOString(),
        uploader: 'user', // 这里应该从当前用户获取
        status: '待处理'
      };
      
      // 保存到localStorage
      existingData.push(newDataItem);
      LocalStorageManager.set(STORAGE_KEYS.DATA, existingData);
      
      // 添加日志
      DataOperations.addLog('UPLOAD_DATA', 'DATA_MANAGEMENT', `用户上传数据文件: ${newDataItem.name}`, 'user', '1');
      
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
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 批量上传文件（保存到localStorage）
  const handleBatchUpload = async () => {
    if (!batchFiles || batchFiles.length === 0) {
      toast.error('请选择要上传的文件');
      return;
    }

    try {
      setBatchUploading(true);
      
      // 模拟上传延迟
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // 获取现有数据
      const existingData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      let successCount = 0;
      let failedCount = 0;
      
      // 处理每个文件
      Array.from(batchFiles).forEach((file) => {
        try {
          // 从文件名解析人员信息
          const fileName = file.name.replace('.zip', '');
          const parts = fileName.split('_');
          const personnelName = parts[1] || fileName;
          
          // 创建新数据项
          const newDataItem: DataItem = {
            id: DataOperations.getNextId(existingData),
            name: file.name,
            description: `用户 ${personnelName} 批量上传的数据文件`,
            file_path: `/uploads/data/${file.name}`,
            file_size: file.size,
            upload_time: new Date().toISOString(),
            uploader: 'user',
            status: '待处理'
          };
          
          existingData.push(newDataItem);
          successCount++;
        } catch (error) {
          console.error('处理文件失败:', file.name, error);
          failedCount++;
        }
      });
      
      // 保存到localStorage
      LocalStorageManager.set(STORAGE_KEYS.DATA, existingData);
      
      // 添加日志
      DataOperations.addLog('BATCH_UPLOAD', 'DATA_MANAGEMENT', `批量上传完成: 成功${successCount}个, 失败${failedCount}个`, 'user', '1');
      
      if (successCount > 0) {
        toast.success(`成功上传 ${successCount} 个文件`);
      }
      
      if (failedCount > 0) {
        toast.error(`${failedCount} 个文件上传失败`);
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
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 批量预处理（模拟处理）
  const handleBatchPreprocess = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要预处理的数据');
      return;
    }

    try {
      setPreprocessing(true);
      
      const selectedIds = Array.from(selectedItems);

      // 直接更新数据状态为处理中
      const existingData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      const updatedData = existingData.map(item => {
        if (selectedIds.includes(item.id)) {
          return { ...item, status: '处理中' };
        }
        return item;
      });
      LocalStorageManager.set(STORAGE_KEYS.DATA, updatedData);
      
      // 刷新数据列表
      fetchData();
      
      // 模拟批量预处理
      toast.success(`已开始预处理 ${selectedIds.length} 条数据`);
      
      // 模拟随机时间后完成处理（每个数据独立完成）
      selectedIds.forEach(dataId => {
        const randomDelay = Math.random() * 20000 + 10000; // 10-30秒随机完成
        setTimeout(() => {
          const currentData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
          const completedData = currentData.map(item => {
            if (item.id === dataId) {
              return { ...item, status: '已处理' };
            }
            return item;
          });
          LocalStorageManager.set(STORAGE_KEYS.DATA, completedData);
          fetchData();
        }, randomDelay);
      });

    } catch (error) {
      console.error('批量预处理失败:', error);
      toast.error('批量预处理失败');
    } finally {
      setPreprocessing(false);
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 批量删除（从localStorage删除）
  const handleBatchDelete = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要删除的数据');
      return;
    }

    if (!window.confirm(`确定要删除选中的${selectedItems.size}条数据吗？此操作无法撤销。`)) {
      return;
    }

    try {
      const selectedIds = Array.from(selectedItems);
      
      // 获取现有数据
      const existingData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      
      // 过滤掉选中的数据
      const filteredData = existingData.filter(item => !selectedIds.includes(item.id));
      
      // 保存到localStorage
      LocalStorageManager.set(STORAGE_KEYS.DATA, filteredData);
      
      // 添加日志
      DataOperations.addLog('BATCH_DELETE_DATA', 'DATA_MANAGEMENT', `批量删除数据: ${selectedIds.length}条`, 'user', '1');
      
      toast.success(`已删除${selectedIds.length}条数据`);
      setSelectedItems(new Set());
      fetchData();
    } catch (error) {
      console.error('批量删除失败:', error);
      toast.error('批量删除失败');
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 单个数据预处理（模拟处理）
  const handlePreprocessSingle = async (dataId: number, fileName: string) => {
    try {
      // 直接更新数据状态为处理中
      const existingData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      const updatedData = existingData.map(item => {
        if (item.id === dataId) {
          return { ...item, status: '处理中' };
        }
        return item;
      });
      LocalStorageManager.set(STORAGE_KEYS.DATA, updatedData);
      
      // 刷新数据列表
      fetchData();
      
      // 模拟预处理
      toast.success(`已开始预处理"${fileName}"`);
      
      // 模拟随机时间后完成处理
      const randomDelay = Math.random() * 20000 + 10000; // 10-30秒随机完成
      setTimeout(() => {
        const currentData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
        const completedData = currentData.map(item => {
          if (item.id === dataId) {
            return { ...item, status: '已处理' };
          }
          return item;
        });
        LocalStorageManager.set(STORAGE_KEYS.DATA, completedData);
        fetchData();
      }, randomDelay);

    } catch (error) {
      console.error('数据预处理失败:', error);
      toast.error('数据预处理失败');
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 删除单个数据（从localStorage删除）
  const handleDeleteSingle = async (dataId: number, fileName: string) => {
    if (!window.confirm(`确定要删除"${fileName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      // 获取现有数据
      const existingData = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
      
      // 过滤掉要删除的数据
      const filteredData = existingData.filter(item => item.id !== dataId);
      
      // 保存到localStorage
      LocalStorageManager.set(STORAGE_KEYS.DATA, filteredData);
      
      // 添加日志
      DataOperations.addLog('DELETE_DATA', 'DATA_MANAGEMENT', `删除数据文件: ${fileName}`, 'user', '1');
      
      toast.success('数据删除成功');
      fetchData();
    } catch (error) {
      console.error('删除数据失败:', error);
      toast.error('删除数据失败');
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 查看数据图像（使用演示数据）
  const handleViewImages = async (dataId: number) => {
    try {
      // 模拟获取图像列表
      const images = imageTypes.map((type) => ({
        image_type: type.key,
        image_name: `${type.key}.png`,
        description: type.label
      }));
      
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
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 处理可视化显示（使用EEG图表）
  const handleVisualizationDisplay = () => {
    if (!selectedDataId || !visualizationType) {
      toast.error('请先选择数据和可视化类型');
      return;
    }
    
    setShowVisualization(true);
    toast.success('正在显示EEG特征图表...');
  };
  // ============================================

  // 选择数据用于可视化
  const handleSelectDataForVisualization = (dataId: number) => {
    setSelectedDataId(dataId);
    setShowVisualization(false);
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
                          className="text-purple-600 hover:text-purple-700"
                          title="选择用于可视化"
                        >
                          <BarChart3 className="h-4 w-4" />
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
              
              {/* 可视化指标选择 */}
              <div>
                <label className="label">可视化指标选择：</label>
                <select
                  className="input"
                  value={visualizationType}
                  onChange={(e) => setVisualizationType(e.target.value)}
                >
                  {visualizationOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
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
                <span>显示图表</span>
              </button>
            </div>

            {/* 可视化图表区域 */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg p-4 min-h-[400px] border-2 border-dashed border-gray-300">
                {showVisualization && selectedDataId ? (
                  <div className="w-full h-full">
                    <EEGVisualization 
                      visualizationType={visualizationType} 
                      dataId={selectedDataId}
                    />
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <Database className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">
                        {selectedDataId ? '点击下方按钮查看可视化图表' : '请先选择数据和指标'}
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
    </div>
  );
};

export default DataManagePage; 