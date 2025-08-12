import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Upload, 
  Search, 
  Trash2, 
  Download,
  FileText,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Model } from '@/types';
import { formatDateTime, formatFileSize } from '@/utils/helpers';
import toast from 'react-hot-toast';

const ModelManagePage: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // 获取模型列表
  const fetchModels = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getModels();
      setModels(Array.isArray(response) ? response : response?.items || []);
    } catch (error) {
      console.error('获取模型列表失败:', error);
      toast.error('获取模型列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  // 上传模型文件
  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 检查文件类型
    if (!file.name.endsWith('.pkl') && !file.name.endsWith('.h5') && !file.name.endsWith('.pt')) {
      toast.error('请选择有效的模型文件（.pkl, .h5, .pt）');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('model_type', '0'); // 默认模型类型

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

      await apiClient.uploadModel(formData);
      
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

  // 删除模型
  const handleDelete = async (modelId: number, modelPath: string) => {
    const fileName = modelPath.split('/').pop() || '未知文件';
    
    if (!window.confirm(`确定要删除模型"${fileName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      await apiClient.deleteModel(modelId);
      toast.success('模型删除成功');
      fetchModels();
    } catch (error) {
      console.error('删除模型失败:', error);
      toast.error('删除模型失败');
    }
  };

  // 获取模型类型名称
  const getModelTypeName = (modelType: number) => {
    const types: { [key: number]: string } = {
      0: '应激评估模型',
      1: '抑郁评估模型',
      2: '焦虑评估模型',
      3: '社交孤立模型',
    };
    return types[modelType] || `模型类型 ${modelType}`;
  };

  // 获取模型状态
  const getModelStatus = (model: Model) => {
    // 简单的状态判断逻辑，实际应该从API获取
    return 'active'; // 可能的状态：active, inactive, error
  };

  // 过滤模型列表
  const filteredModels = models.filter(model =>
    model.model_path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    getModelTypeName(model.model_type).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">模型管理</h1>
        <p className="text-gray-600 mt-1">管理AI健康评估模型文件</p>
      </div>

      {/* 操作栏 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        {/* 搜索 */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="搜索模型文件或类型..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* 上传按钮 */}
        <div className="relative">
          <input
            type="file"
            accept=".pkl,.h5,.pt"
            onChange={handleUpload}
            className="hidden"
            id="model-upload"
            disabled={uploading}
          />
          <label
            htmlFor="model-upload"
            className={`btn btn-primary flex items-center space-x-2 cursor-pointer ${
              uploading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Upload className="h-4 w-4" />
            <span>{uploading ? '上传中...' : '上传模型'}</span>
          </label>
        </div>
      </div>

      {/* 上传进度 */}
      {uploading && (
        <div className="card p-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span>上传进度</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* 模型列表 */}
      <div className="card overflow-hidden">
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
            <p className="text-xs text-gray-400 mt-2">
              支持格式：.pkl, .h5, .pt
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    模型信息
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    模型类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    状态
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
                {filteredModels.map((model) => {
                  const fileName = model.model_path.split('/').pop() || '未知文件';
                  const fileExtension = fileName.split('.').pop()?.toLowerCase();
                  const status = getModelStatus(model);
                  
                  return (
                    <tr key={model.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                            <Brain className="h-5 w-5 text-white" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {fileName}
                            </div>
                            <div className="text-sm text-gray-500">
                              ID: {model.id} • {fileExtension?.toUpperCase()} 文件
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {getModelTypeName(model.model_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {status === 'active' ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                              <span className="text-sm text-green-600">正常</span>
                            </>
                          ) : (
                            <>
                              <AlertCircle className="h-4 w-4 text-yellow-500 mr-2" />
                              <span className="text-sm text-yellow-600">未激活</span>
                            </>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDateTime(model.create_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => {/* 下载功能 */}}
                            className="text-blue-600 hover:text-blue-700"
                            title="下载"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(model.id, model.model_path)}
                            className="text-red-600 hover:text-red-700"
                            title="删除"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 模型信息说明 */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">模型类型说明</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <Brain className="h-4 w-4 text-red-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">应激评估模型</p>
              <p className="text-sm text-gray-500">用于评估用户的应激反应水平</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Brain className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">抑郁评估模型</p>
              <p className="text-sm text-gray-500">用于评估用户的抑郁情绪状态</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <Brain className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">焦虑评估模型</p>
              <p className="text-sm text-gray-500">用于评估用户的焦虑程度</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <Brain className="h-4 w-4 text-purple-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">社交孤立模型</p>
              <p className="text-sm text-gray-500">用于评估用户的社交孤立水平</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelManagePage; 