import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Upload, 
  Search, 
  Trash2, 
  Download,
  FileText,
  CheckCircle,
  AlertCircle,
  Settings,
  Eye,
  RefreshCw,
  Archive,
  BarChart3,
  Clock,
  HardDrive,
  Activity,
  Package,
  History,
  ExternalLink,
  Info,
  Zap
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Model } from '@/types';
import { formatDateTime, formatFileSize } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, initializeDemoData } from '@/utils/localStorage';
import toast from 'react-hot-toast';

interface ModelStatus {
  total_models: number;
  available_models: number;
  missing_models: number;
  model_details: ModelDetail[];
}

interface ModelDetail {
  id: number;
  model_type: number;
  model_type_name: string;
  model_path: string;
  create_time: string;
  file_exists: boolean;
  file_size_mb: number;
  status: string;
}

interface ModelVersion {
  id: number | null;
  version: string;
  create_time: string;
  file_path: string;
  file_exists: boolean;
  file_size_mb: number;
  is_current: boolean;
}

interface ModelPerformance {
  id: number;
  model_type: number;
  model_type_name: string;
  create_time: string;
  file_exists: boolean;
  accuracy: {
    training: number;
    validation: number;
    test: number;
  };
  loss: {
    training: number;
    validation: number;
  };
  training_epochs: number;
  model_size_mb: number;
}

const ModelManagePage: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showStatus, setShowStatus] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [selectedModelType, setSelectedModelType] = useState<number | null>(null);
  const [modelVersions, setModelVersions] = useState<ModelVersion[]>([]);
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>([]);
  const [selectedUploadType, setSelectedUploadType] = useState<number>(0);

  const modelTypes = {
    0: "普通应激模型",
    1: "抑郁评估模型", 
    2: "焦虑评估模型",
    3: "社交孤立评估模型"
  };

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取模型列表（从localStorage读取）
  const fetchModels = async () => {
    try {
      setLoading(true);
      
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 从localStorage获取模型数据
      const modelsList = LocalStorageManager.get<Model[]>(STORAGE_KEYS.MODELS, []);
      
      // 转换为前端Model类型（如果需要的话）
      const convertedModels: Model[] = modelsList.map(model => ({
        id: model.id,
        model_type: model.id % 4, // 将id映射到0-3的模型类型
        model_path: `/models/${model.name.toLowerCase().replace(/\s+/g, '_')}_${model.version}.pkl`,
        create_time: model.created_at,
        update_time: model.created_at,
        status: model.status === '已部署' ? 'active' : 'inactive',
        version: model.version,
        accuracy: model.accuracy,
        description: model.description
      }));
      
      setModels(convertedModels);
    } catch (error) {
      console.error('获取模型列表失败:', error);
      toast.error('获取模型列表失败');
    } finally {
      setLoading(false);
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取模型状态（从localStorage读取）
  const fetchModelStatus = async () => {
    try {
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 从localStorage获取模型数据
      const modelsList = LocalStorageManager.get<Model[]>(STORAGE_KEYS.MODELS, []);
      
      // 计算模型状态
      const totalModels = modelsList.length;
      const availableModels = modelsList.filter(model => model.status === '已部署').length;
      const missingModels = totalModels - availableModels;
      
      // 生成模型详情
      const modelDetails = modelsList.map((model, index) => ({
        id: model.id,
        model_type: index % 4,
        model_path: `/models/${model.name.toLowerCase().replace(/\s+/g, '_')}_${model.version}.pkl`,
        status: model.status === '已部署' ? 'available' : 'missing',
        version: model.version,
        accuracy: model.accuracy,
        last_updated: model.created_at
      }));
      
      const status: ModelStatus = {
        total_models: totalModels,
        available_models: availableModels,
        missing_models: missingModels,
        model_details: modelDetails
      };
      
      setModelStatus(status);
    } catch (error) {
      console.error('获取模型状态失败:', error);
      toast.error('获取模型状态失败');
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取模型版本（从localStorage读取）
  const fetchModelVersions = async (modelType: number) => {
    try {
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 从localStorage获取模型数据
      const modelsList = LocalStorageManager.get<Model[]>(STORAGE_KEYS.MODELS, []);
      
      // 根据模型类型过滤并生成版本信息
      const filteredModels = modelsList.filter((_, index) => index % 4 === modelType);
      
      const versions: ModelVersion[] = filteredModels.map(model => ({
        id: model.id,
        version: model.version,
        created_at: model.created_at,
        status: model.status === '已部署' ? 'active' : 'inactive',
        accuracy: model.accuracy,
        description: model.description,
        file_size: parseFloat((Math.random() * 150 + 30).toFixed(2)) // 模拟文件大小，30-180MB，保留两位小数
      }));
      
      setModelVersions(versions);
      setSelectedModelType(modelType);
      setShowVersions(true);
    } catch (error) {
      console.error('获取模型版本失败:', error);
      toast.error('获取模型版本失败');
    }
  };
  // ============================================

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取模型性能信息（从localStorage读取）
  const fetchModelPerformance = async () => {
    try {
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      
      // 从localStorage获取模型数据
      const modelsList = LocalStorageManager.get<Model[]>(STORAGE_KEYS.MODELS, []);
      
      // 生成性能数据
      const performanceData: ModelPerformance[] = modelsList.map((model, index) => ({
        model_id: model.id,
        model_name: model.name,
        model_type: index % 4,
        accuracy: model.accuracy,
        precision: parseFloat((model.accuracy - 0.02 + Math.random() * 0.04).toFixed(4)), // 模拟精度
        recall: parseFloat((model.accuracy - 0.01 + Math.random() * 0.02).toFixed(4)), // 模拟召回率
        f1_score: parseFloat((model.accuracy - 0.015 + Math.random() * 0.03).toFixed(4)), // 模拟F1分数
        training_time_hours: Math.floor(Math.random() * 48) + 12, // 模拟训练时间
        training_epochs: Math.floor(Math.random() * 100) + 50, // 模拟训练轮数
        model_size_mb: parseFloat((Math.random() * 180 + 35).toFixed(2)) // 模拟模型大小，35-215MB，保留两位小数
      }));
      
      setModelPerformance(performanceData);
    } catch (error) {
      console.error('获取模型性能信息失败:', error);
      toast.error('获取模型性能信息失败');
    }
  };
  // ============================================

  useEffect(() => {
    fetchModels();
  }, []);

  // 上传模型文件
  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 检查文件类型
    if (!file.name.endsWith('.keras') && !file.name.endsWith('.h5') && !file.name.endsWith('.pt') && !file.name.endsWith('.pkl')) {
      toast.error('请选择有效的模型文件（.keras, .h5, .pt, .pkl）');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      // 模拟上传进度（纯前端演示，不实际上传）
      const progressTimer = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressTimer);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // 模拟一点延迟，等待进度条接近完成
      await new Promise(resolve => setTimeout(resolve, 1200));

      // 仅更新前端模型列表的信息
      const newModelPath = `/models/${selectedUploadType}/${file.name}`;
      setModels(prev => prev.map(m => (
        m.model_type === selectedUploadType
          ? { ...m, model_path: newModelPath, create_time: new Date().toISOString() }
          : m
      )));

      setUploadProgress(100);
      toast.success('模型信息更新成功！');

      // 稍后复位上传状态
      setTimeout(() => {
        setUploadProgress(0);
        setUploading(false);
      }, 800);

    } catch (error) {
      console.error('更新模型信息失败:', error);
      toast.error('更新模型信息失败');
      setUploading(false);
      setUploadProgress(0);
    }

    // 重置文件输入
    event.target.value = '';
  };

  // 删除模型
  const handleDelete = async (modelId: number, modelType: number) => {
    const modelTypeName = modelTypes[modelType as keyof typeof modelTypes] || '未知类型';
    
    if (!window.confirm(`确定要删除"${modelTypeName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      await apiClient.delete(`/models/${modelId}`);
      toast.success('模型删除成功');
      fetchModels();
    } catch (error) {
      console.error('删除模型失败:', error);
      toast.error('删除模型失败');
    }
  };

  // 导出单个模型
  const handleExportModel = async (modelId: number) => {
    try {
      // 查找对应的模型
      const model = models.find(m => m.id === modelId);
      if (!model) {
        toast.error('未找到模型');
        return;
      }

      // 从模型路径中提取文件名（base name）
      const fileName = model.model_path.split('/').pop() || `model_${modelId}.pkl`;

      // 根据模型 ID 生成文件大小（35-215MB），使用模型 ID 作为随机种子
      // 使用简单的伪随机算法，确保同一个模型每次导出大小相同但看起来随机
      const seed = modelId * 9301 + 49297; // 简单的线性同余生成器
      const random = (seed % 233280) / 233280; // 生成 0-1 之间的伪随机数
      const fileSizeMB = parseFloat((35 + random * 180).toFixed(2)); // 35-215MB，保留两位小数
      const fileSizeBytes = Math.floor(fileSizeMB * 1024 * 1024);

      // 生成随机内容
      // crypto.getRandomValues 有最大限制（通常是 65536 字节），所以使用较小的块
      const chunkSize = 65536; // 64KB chunks (crypto.getRandomValues 的安全限制)
      const chunks = [];
      const numChunks = Math.ceil(fileSizeBytes / chunkSize);

      for (let i = 0; i < numChunks; i++) {
        const size = i === numChunks - 1 ? fileSizeBytes % chunkSize || chunkSize : chunkSize;
        const chunk = new Uint8Array(size);
        // 填充随机数据
        crypto.getRandomValues(chunk);
        chunks.push(chunk);
      }

      // 创建 Blob
      const blob = new Blob(chunks, { type: 'application/octet-stream' });

      // 触发下载
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('模型导出成功');
    } catch (error) {
      console.error('导出模型失败，完整错误栈:', error);
      if (error instanceof Error) {
        console.error('错误消息:', error.message);
        console.error('错误堆栈:', error.stack);
      }
      toast.error('导出模型失败');
    }
  };

  // 导出所有模型
  const handleExportAllModels = async () => {
    try {
      if (models.length === 0) {
        toast.error('没有可导出的模型');
        return;
      }

      // 依次导出每个模型
      for (let i = 0; i < models.length; i++) {
        const model = models[i];
        
        // 从模型路径中提取文件名（base name）
        const fileName = model.model_path.split('/').pop() || `model_${model.id}.pkl`;

        // 根据模型 ID 生成文件大小（35-215MB），使用模型 ID 作为随机种子
        // 使用简单的伪随机算法，确保同一个模型每次导出大小相同但看起来随机
        const seed = model.id * 9301 + 49297; // 简单的线性同余生成器
        const random = (seed % 233280) / 233280; // 生成 0-1 之间的伪随机数
        const fileSizeMB = parseFloat((35 + random * 180).toFixed(2)); // 35-215MB，保留两位小数
        const fileSizeBytes = Math.floor(fileSizeMB * 1024 * 1024);

        // 生成随机内容
        // crypto.getRandomValues 有最大限制（通常是 65536 字节），所以使用较小的块
        const chunkSize = 65536; // 64KB chunks (crypto.getRandomValues 的安全限制)
        const chunks = [];
        const numChunks = Math.ceil(fileSizeBytes / chunkSize);

        for (let j = 0; j < numChunks; j++) {
          const size = j === numChunks - 1 ? fileSizeBytes % chunkSize || chunkSize : chunkSize;
          const chunk = new Uint8Array(size);
          // 填充随机数据
          crypto.getRandomValues(chunk);
          chunks.push(chunk);
        }

        // 创建 Blob
        const blob = new Blob(chunks, { type: 'application/octet-stream' });

        // 触发下载
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        // 如果不是最后一个文件，稍微延迟一下，避免浏览器同时下载太多文件
        if (i < models.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      toast.success(`成功导出 ${models.length} 个模型`);
    } catch (error) {
      console.error('导出所有模型失败，完整错误栈:', error);
      if (error instanceof Error) {
        console.error('错误消息:', error.message);
        console.error('错误堆栈:', error.stack);
      }
      toast.error('导出所有模型失败');
    }
  };

  // 恢复模型版本
  const handleRestoreVersion = async (modelType: number, backupFilename: string) => {
    if (!window.confirm(`确定要恢复到此版本吗？当前版本将被备份。`)) {
      return;
    }

    try {
      const formData = new FormData();
      formData.append('backup_filename', backupFilename);

      await apiClient.post(`/models/restore/${modelType}`, formData);
      toast.success('模型版本恢复成功');
      fetchModels();
      fetchModelVersions(modelType);
    } catch (error) {
      console.error('恢复模型版本失败:', error);
      toast.error('恢复模型版本失败');
    }
  };

  // 过滤模型
  const filteredModels = models.filter(model => {
    const modelTypeName = modelTypes[model.model_type as keyof typeof modelTypes] || '';
    return modelTypeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
           model.model_path.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">模型管理</h1>
        <p className="text-gray-600 mt-1">管理AI模型文件，监控模型状态和性能</p>
      </div>

      {/* 操作栏 */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* 搜索 */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="搜索模型类型或路径..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* 操作按钮 */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleExportAllModels}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Archive className="h-4 w-4" />
            <span>导出全部</span>
          </button>
          <button
            onClick={fetchModels}
            disabled={loading}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>刷新</span>
          </button>
        </div>
      </div>

      {/* 模型状态面板 */}
      {showStatus && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">模型状态监控</h3>
            <button
              onClick={fetchModelStatus}
              className="btn btn-secondary btn-sm flex items-center space-x-2"
            >
              <RefreshCw className="h-4 w-4" />
              <span>刷新状态</span>
            </button>
          </div>
          
          {modelStatus ? (
            <div className="space-y-4">
              {/* 状态概览 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-blue-900">总模型数</span>
                    <Package className="h-5 w-5 text-blue-600" />
                  </div>
                  <p className="text-2xl font-bold text-blue-900 mt-2">{modelStatus.total_models}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-green-900">可用模型</span>
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  <p className="text-2xl font-bold text-green-900 mt-2">{modelStatus.available_models}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-red-900">缺失模型</span>
                    <AlertCircle className="h-5 w-5 text-red-600" />
                  </div>
                  <p className="text-2xl font-bold text-red-900 mt-2">{modelStatus.missing_models}</p>
                </div>
              </div>

              {/* 详细状态 */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        模型类型
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        文件大小
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        创建时间
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        状态
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {modelStatus.model_details.map((detail) => (
                      <tr key={detail.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {detail.model_type_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            类型 {detail.model_type}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {detail.file_size_mb.toFixed(2)} MB
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDateTime(detail.create_time)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            detail.file_exists 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {detail.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => fetchModelVersions(detail.model_type)}
                            className="text-blue-600 hover:text-blue-700 mr-2"
                            title="查看版本"
                          >
                            <History className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">点击刷新状态获取模型状态信息</p>
            </div>
          )}
        </div>
      )}

      {/* 模型性能面板 */}
      {showPerformance && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">模型性能信息</h3>
          
          {modelPerformance.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      模型类型
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      准确率
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      损失
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      训练轮数
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      模型大小
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {modelPerformance.map((perf) => (
                    <tr key={perf.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {perf.model_type_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-xs space-y-1">
                          <div>训练: {(perf.accuracy.training * 100).toFixed(1)}%</div>
                          <div>验证: {(perf.accuracy.validation * 100).toFixed(1)}%</div>
                          <div>测试: {(perf.accuracy.test * 100).toFixed(1)}%</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-xs space-y-1">
                          <div>训练: {perf.loss.training.toFixed(4)}</div>
                          <div>验证: {perf.loss.validation.toFixed(4)}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {perf.training_epochs}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {perf.model_size_mb.toFixed(2)} MB
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">暂无性能数据</p>
            </div>
          )}
        </div>
      )}

      {/* 上传区域 */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">上传新模型</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="label">模型类型</label>
            <select
              className="input"
              value={selectedUploadType}
              onChange={(e) => setSelectedUploadType(parseInt(e.target.value))}
            >
              {Object.entries(modelTypes).map(([value, name]) => (
                <option key={value} value={value}>{name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">模型文件</label>
          <input
            type="file"
              accept=".keras,.h5,.pt,.pkl"
            onChange={handleUpload}
            disabled={uploading}
              className="input"
            />
        </div>
      </div>

      {/* 上传进度 */}
      {uploading && (
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">上传进度</span>
              <span className="text-sm text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>支持格式：.keras, .h5, .pt, .pkl</span>
          {uploading && <span>正在上传...</span>}
        </div>
      </div>

      {/* 模型列表 */}
      <div className="card overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">模型列表</h3>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
            <span className="ml-2 text-gray-500">加载中...</span>
          </div>
        ) : filteredModels.length === 0 ? (
          <div className="text-center py-8">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm ? '未找到匹配的模型' : '暂无模型文件'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    模型类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    文件路径
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    创建时间
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredModels.map((model) => (
                    <tr key={model.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {model.id}
                    </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                        <Brain className="h-4 w-4 text-gray-400 mr-2" />
                        <div>
                            <div className="text-sm font-medium text-gray-900">
                            {modelTypes[model.model_type as keyof typeof modelTypes] || '未知类型'}
                            </div>
                            <div className="text-sm text-gray-500">
                            类型 {model.model_type}
                            </div>
                          </div>
                        </div>
                      </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate" title={model.model_path}>
                        {model.model_path}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(model.create_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                          onClick={() => fetchModelVersions(model.model_type)}
                            className="text-blue-600 hover:text-blue-700"
                          title="查看版本"
                        >
                          <History className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleExportModel(model.id)}
                          className="text-green-600 hover:text-green-700"
                          title="导出模型"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                          <button
                          onClick={() => handleDelete(model.id, model.model_type)}
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

      {/* 模型版本模态框 */}
      {showVersions && selectedModelType !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                {modelTypes[selectedModelType as keyof typeof modelTypes]} - 版本历史
              </h2>
              <button
                onClick={() => setShowVersions(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-3">
              {modelVersions.map((version, index) => (
                <div 
                  key={index} 
                  className={`p-4 rounded-lg border ${
                    version.is_current ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
            <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-900">{version.version}</h4>
                        {version.is_current && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            当前版本
                          </span>
                        )}
            </div>
                      <p className="text-sm text-gray-500 mt-1">
                        大小: {version.file_size_mb.toFixed(2)} MB | 
                        创建时间: {formatDateTime(version.create_time)}
                      </p>
          </div>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        version.file_exists 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {version.file_exists ? '文件存在' : '文件缺失'}
                      </span>
                      {!version.is_current && version.file_exists && (
                        <button
                          onClick={() => {
                            const filename = version.file_path.split('/').pop() || '';
                            handleRestoreVersion(selectedModelType, filename);
                          }}
                          className="btn btn-sm btn-secondary"
                        >
                          恢复此版本
                        </button>
                      )}
            </div>
            </div>
          </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelManagePage; 