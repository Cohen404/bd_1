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
  AlertTriangle,
  Image,
  RefreshCw,
  Download,
  FileImage,
  ArrowLeft,
  ArrowRight,
  ZoomIn,
  Play,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Data, PreprocessProgress } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';
import ProgressBar from '@/components/Common/ProgressBar';
import ProgressModal from '@/components/Common/ProgressModal';

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
  const [visualizationImage, setVisualizationImage] = useState<string | null>(null);
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
  const [preprocessingProgress, setPreprocessingProgress] = useState<{
    [key: number]: { status: string; message: string }
  }>({});
  const [progressModalVisible, setProgressModalVisible] = useState(false);
  const [progressDataIds, setProgressDataIds] = useState<number[]>([]);
  const [dataProgressMap, setDataProgressMap] = useState<{[key: number]: PreprocessProgress}>({});
  const [processingStartTimes, setProcessingStartTimes] = useState<{[key: number]: number}>({});
  const [simulatedProgress, setSimulatedProgress] = useState<{[key: number]: number}>({});

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

  // 获取数据列表
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getData({ search: searchTerm });
      setDataList(Array.isArray(response) ? response : response?.items || []);
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
      const maxTime = 60; // 60秒
      const maxProgress = 99; // 最大99%
      
      // 使用指数增长模拟，前期快，后期慢
      const progress = Math.min(maxProgress, maxProgress * (1 - Math.exp(-elapsed / (maxTime / 3))));
      
      const simulated = Math.round(progress);
      
      // 更新模拟进度状态
      setSimulatedProgress(prev => ({ ...prev, [dataId]: simulated }));
      
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

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedItems.size === filteredData.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredData.map(item => item.id)));
    }
  };

  // 上传文件
  const handleUpload = async () => {
    if (!formData.file || !formData.personnel_id || !formData.personnel_name) {
      toast.error('请填写完整信息并选择文件');
      return;
    }

    try {
      setUploading(true);
      const uploadFormData = new FormData();
      uploadFormData.append('file', formData.file);
      uploadFormData.append('personnel_id', formData.personnel_id);
      uploadFormData.append('personnel_name', formData.personnel_name);

      await apiClient.uploadData(uploadFormData);
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

  // 批量上传文件
  const handleBatchUpload = async () => {
    if (!batchFiles || batchFiles.length === 0) {
      toast.error('请选择要上传的文件');
      return;
    }

    try {
      setBatchUploading(true);
      const formData = new FormData();
      
      Array.from(batchFiles).forEach((file) => {
        formData.append('files', file);
      });

      const response = await apiClient.batchUploadData(formData);
      
      if (response.success_count > 0) {
        toast.success(`成功上传 ${response.success_count} 个文件`);
      }
      
      if (response.failed_count > 0) {
        toast.error(`${response.failed_count} 个文件上传失败`);
        // 显示具体错误信息
        response.errors?.forEach((error: string) => {
          console.error('上传错误:', error);
        });
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

  // 批量预处理
  const handleBatchPreprocess = async () => {
    if (selectedItems.size === 0) {
      toast.error('请先选择要预处理的数据');
      return;
    }

    try {
      setPreprocessing(true);
      
      const selectedIds = Array.from(selectedItems);
      setProgressDataIds(selectedIds);
      setProgressModalVisible(true);

      // 启动批量预处理
      const response = await apiClient.batchPreprocessData({ data_ids: selectedIds });
      
      toast.success(`批量预处理已启动，请查看进度窗口监控处理状态`);
      
      // 刷新数据列表以获取最新状态
      setTimeout(() => {
        fetchData();
      }, 1000);

    } catch (error) {
      console.error('批量预处理失败:', error);
      toast.error('批量预处理失败');
      setProgressModalVisible(false);
    } finally {
      setPreprocessing(false);
    }
  };

  // 批量删除
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
      const response = await apiClient.batchDeleteData({ data_ids: selectedIds });
      toast.success(response.message || `已删除${selectedIds.length}条数据`);
      setSelectedItems(new Set());
      fetchData();
    } catch (error) {
      console.error('批量删除失败:', error);
      toast.error('批量删除失败');
    }
  };

  // 单个数据预处理
  const handlePreprocessSingle = async (dataId: number, fileName: string) => {
    if (!window.confirm(`确定要预处理"${fileName}"吗？这将进行特征提取和图片生成。`)) {
      return;
    }

    try {
      // 显示单个数据的进度窗口
      setProgressDataIds([dataId]);
      setProgressModalVisible(true);

      // 启动预处理
      const result = await apiClient.preprocessData(dataId);
      
      toast.success('数据预处理已启动，请查看进度窗口监控处理状态');
      
      // 刷新数据列表以获取最新状态
      setTimeout(() => {
        fetchData();
      }, 1000);

    } catch (error) {
      console.error('数据预处理失败:', error);
      toast.error('数据预处理失败');
      setProgressModalVisible(false);
    }
  };

  // 删除单个数据
  const handleDeleteSingle = async (dataId: number, fileName: string) => {
    if (!window.confirm(`确定要删除"${fileName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      await apiClient.deleteData(dataId);
      toast.success('数据删除成功');
      fetchData();
    } catch (error) {
      console.error('删除数据失败:', error);
      toast.error('删除数据失败');
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

  // 处理可视化显示
  const handleVisualizationDisplay = () => {
    if (!selectedDataId || !visualizationType) {
      toast.error('请先选择数据和可视化类型');
      return;
    }
    
    const imageUrl = `/api/health/image/${selectedDataId}/${visualizationType}`;
    setVisualizationImage(imageUrl);
    setShowVisualization(true);
  };

  // 选择数据用于可视化
  const handleSelectDataForVisualization = (dataId: number) => {
    setSelectedDataId(dataId);
    setVisualizationImage(null);
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
            onClick={() => setUploadModalVisible(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>单个上传</span>
          </button>
          <button
            onClick={() => setBatchUploadModalVisible(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Upload className="h-4 w-4" />
            <span>批量上传</span>
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

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* 数据表格 - 占3列 */}
        <div className="xl:col-span-3">
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
                              onClick={() => handleViewImages(item.id)}
                              className="text-blue-600 hover:text-blue-700"
                              title="查看图像"
                            >
                              <Image className="h-4 w-4" />
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
        </div>

        {/* 数据可视化 - 占1列 */}
        <div className="xl:col-span-1">
          <div className="card p-6 bg-primary-50">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 text-center">数据可视化</h3>
              
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
                      setVisualizationImage(null);
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

              {/* 可视化图表区域 */}
              <div className="bg-white rounded-lg p-4 min-h-[300px] flex items-center justify-center border-2 border-dashed border-gray-300">
                {showVisualization && visualizationImage ? (
                  <div className="w-full h-full flex flex-col items-center">
                    <div 
                      className="relative group cursor-pointer"
                      onClick={() => {
                        console.log('可视化图片点击事件触发');
                        console.log('打开可视化图片URL:', visualizationImage);
                        if (visualizationImage) {
                          const newWindow = window.open(visualizationImage, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
                          if (!newWindow) {
                            alert('弹窗被浏览器阻止，请允许弹窗后重试');
                          }
                        }
                      }}
                    >
                      <img
                        src={visualizationImage}
                        alt={visualizationOptions.find(opt => opt.value === visualizationType)?.label}
                        className="max-w-full max-h-64 object-contain rounded-lg shadow-sm hover:shadow-lg transition-shadow"
                        onLoad={() => {
                          console.log('图片加载成功:', visualizationImage);
                        }}
                        onError={(e) => {
                          console.error('图片加载失败:', visualizationImage);
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                          toast.error('图片加载失败，请检查数据是否已预处理');
                        }}
                      />
                      {/* 悬停提示 */}
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black bg-opacity-20 rounded-lg pointer-events-none">
                        <div className="bg-white px-3 py-1 rounded text-sm font-medium shadow-lg">
                          点击在新窗口打开
                        </div>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2 text-center">
                      {visualizationOptions.find(opt => opt.value === visualizationType)?.label}
                    </p>
                  </div>
                ) : (
                  <div className="text-center">
                    <Database className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">
                      {selectedDataId ? '点击下方按钮查看可视化图片' : '请先选择数据和指标'}
                    </p>
                  </div>
                )}
              </div>

              <button 
                className="btn btn-primary w-full flex items-center justify-center space-x-2"
                onClick={handleVisualizationDisplay}
                disabled={!selectedDataId}
              >
                <Eye className="h-4 w-4" />
                <span>显示图片</span>
              </button>
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
            <h2 className="text-lg font-semibold text-gray-900 mb-4">批量上传数据文件</h2>
            
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
                {batchUploading ? '上传中...' : '批量上传'}
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
              {Object.entries(preprocessingProgress).map(([dataId, progress]) => (
                <div key={dataId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">数据ID: {dataId}</span>
                  <div className="flex items-center space-x-2">
                    {progress.status === 'pending' && (
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