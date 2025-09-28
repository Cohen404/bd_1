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
// import { apiClient } from '@/utils/api'; // 注释后端API调用
import { Model } from '@/types';
import { formatDateTime, formatFileSize } from '@/utils/helpers';
import { ModelStorage, ModelFormData } from '@/utils/model-storage';
import { validateModel, validateFileUpload, getModelTypeName, getModelTypeOptions } from '@/utils/model-validation';
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

  // 获取模型列表 - 纯前端实现
  const fetchModels = async () => {
    try {
      setLoading(true);
      // 初始化示例数据（如果不存在）
      ModelStorage.initializeSampleData();
      const response = ModelStorage.getAllModels();
      setModels(response);
    } catch (error) {
      console.error('获取模型列表失败:', error);
      toast.error('获取模型列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取模型状态 - 纯前端实现
  const fetchModelStatus = async () => {
    try {
      const response = ModelStorage.getModelStatus();
      setModelStatus(response);
    } catch (error) {
      console.error('获取模型状态失败:', error);
      toast.error('获取模型状态失败');
    }
  };

  // 获取模型版本 - 纯前端实现
  const fetchModelVersions = async (modelType: number) => {
    try {
      const response = ModelStorage.getModelVersions(modelType);
      setModelVersions(response);
      setSelectedModelType(modelType);
      setShowVersions(true);
    } catch (error) {
      console.error('获取模型版本失败:', error);
      toast.error('获取模型版本失败');
    }
  };

  // 获取模型性能信息 - 纯前端实现
  const fetchModelPerformance = async () => {
    try {
      const response = ModelStorage.getModelPerformance();
      setModelPerformance(response);
    } catch (error) {
      console.error('获取模型性能信息失败:', error);
      toast.error('获取模型性能信息失败');
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  // 上传模型文件 - 纯前端实现
  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 验证文件
    const fileErrors = validateFileUpload(file);
    if (fileErrors.length > 0) {
      fileErrors.forEach(error => toast.error(error));
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      // 模拟上传进度
      const progressTimer = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressTimer);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // 创建模型数据
      const modelData: ModelFormData = {
        model_type: selectedUploadType,
        model_name: file.name.replace(/\.[^/.]+$/, ""), // 移除扩展名
        description: `上传的${getModelTypeName(selectedUploadType)}文件`,
        file_name: file.name,
        file_size: file.size
      };

      // 验证模型数据
      const validationErrors = validateModel(modelData);
      if (validationErrors.length > 0) {
        validationErrors.forEach(error => toast.error(error));
        setUploading(false);
        setUploadProgress(0);
        return;
      }

      // 模拟上传延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 添加到本地存储
      ModelStorage.addModel(modelData);
      
      clearInterval(progressTimer);
      setUploadProgress(100);

      toast.success('模型上传成功！');
      fetchModels();

      setTimeout(() => {
        setUploadProgress(0);
        setUploading(false);
      }, 1000);

    } catch (error) {
      console.error('模型上传失败:', error);
      toast.error('模型上传失败');
      setUploading(false);
      setUploadProgress(0);
    }

    // 重置文件输入
    event.target.value = '';
  };

  // 删除模型 - 纯前端实现
  const handleDelete = async (modelId: number, modelType: number) => {
    const modelTypeName = modelTypes[modelType as keyof typeof modelTypes] || '未知类型';
    
    if (!window.confirm(`确定要删除"${modelTypeName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      const success = ModelStorage.deleteModel(modelId);
      if (success) {
        toast.success('模型删除成功');
        fetchModels();
      } else {
        toast.error('模型不存在或删除失败');
      }
    } catch (error) {
      console.error('删除模型失败:', error);
      toast.error('删除模型失败');
    }
  };

  // 导出单个模型 - 纯前端实现（模拟）
  const handleExportModel = async (modelId: number) => {
    try {
      const model = ModelStorage.getModelById(modelId);
      if (!model) {
        toast.error('模型不存在');
        return;
      }

      // 模拟导出文件
      const exportData = {
        id: model.id,
        model_type: model.model_type,
        model_path: model.model_path,
        create_time: model.create_time,
        export_time: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `model_${modelId}_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('模型信息导出成功');
    } catch (error) {
      console.error('导出模型失败:', error);
      toast.error('导出模型失败');
    }
  };

  // 导出所有模型 - 纯前端实现（模拟）
  const handleExportAllModels = async () => {
    try {
      const allModels = ModelStorage.getAllModels();
      const exportData = {
        models: allModels,
        export_time: new Date().toISOString(),
        total_count: allModels.length
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `all_models_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('所有模型信息导出成功');
    } catch (error) {
      console.error('导出所有模型失败:', error);
      toast.error('导出所有模型失败');
    }
  };

  // 恢复模型版本 - 纯前端实现（模拟）
  const handleRestoreVersion = async (modelType: number, backupFilename: string) => {
    if (!window.confirm(`确定要恢复到此版本吗？当前版本将被备份。`)) {
      return;
    }

    try {
      // 模拟版本恢复
      toast.success('模型版本恢复成功（模拟）');
      fetchModels();
      fetchModelVersions(modelType);
    } catch (error) {
      console.error('恢复模型版本失败:', error);
      toast.error('恢复模型版本失败');
    }
  };

  // 过滤模型 - 使用存储类的搜索功能
  const filteredModels = searchTerm 
    ? ModelStorage.searchModels(searchTerm)
    : models;

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
            onClick={() => setShowStatus(!showStatus)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Activity className="h-4 w-4" />
            <span>状态监控</span>
          </button>
          <button
            onClick={() => {
              setShowPerformance(!showPerformance);
              if (!showPerformance) fetchModelPerformance();
            }}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <BarChart3 className="h-4 w-4" />
            <span>性能信息</span>
          </button>
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
              accept=".keras,.h5,.pt"
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
          <span>支持格式：.keras, .h5, .pt</span>
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