import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Save,
  RefreshCw,
  Database,
  Shield,
  Download,
  Upload,
  RotateCcw
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Parameter } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { validateParameter, validateParameterName } from '@/utils/parameter-validation';
import toast from 'react-hot-toast';

interface ParameterFormData {
  param_name: string;
  param_value: string;
  param_type: string;
  description: string;
}

const ParameterManagePage: React.FC = () => {
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingParam, setEditingParam] = useState<Parameter | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingParam, setDeletingParam] = useState<{ id: number; name: string } | null>(null);
  const [formData, setFormData] = useState<ParameterFormData>({
    param_name: '',
    param_value: '',
    param_type: 'string',
    description: ''
  });

  const fetchParameters = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getParameters();
      setParameters(response.items || response);
    } catch (error) {
      console.error('获取参数列表失败:', error);
      toast.error('获取参数列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchParameters();
  }, []);

  // 重置表单
  const resetForm = () => {
    setFormData({
      param_name: '',
      param_value: '',
      param_type: 'string',
      description: ''
    });
    setEditingParam(null);
  };

  // 打开新增参数模态框
  const handleAdd = () => {
    resetForm();
    setShowModal(true);
  };

  // 打开编辑参数模态框
  const handleEdit = (param: Parameter) => {
    setEditingParam(param);
    setFormData({
      param_name: param.param_name,
      param_value: param.param_value,
      param_type: param.param_type,
      description: param.description || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (paramId: number, paramName: string) => {
    setDeletingParam({ id: paramId, name: paramName });
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deletingParam) return;

    try {
      await apiClient.deleteParameter(deletingParam.id);
      toast.success('参数删除成功');
      fetchParameters();
      setShowDeleteConfirm(false);
      setDeletingParam(null);
    } catch (error) {
      console.error('删除参数失败:', error);
      toast.error('删除参数失败');
    }
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setDeletingParam(null);
  };

  const handleSave = async () => {
    const validationErrors = validateParameter(formData);
    if (validationErrors.length > 0) {
      validationErrors.forEach(error => toast.error(error));
      return;
    }

    const nameErrors = validateParameterName(
      formData.param_name, 
      formData.param_type, 
      parameters, 
      editingParam?.id
    );
    if (nameErrors.length > 0) {
      nameErrors.forEach(error => toast.error(error));
      return;
    }

    try {
      if (editingParam) {
        await apiClient.updateParameter(editingParam.id, formData);
        toast.success('参数更新成功');
      } else {
        await apiClient.createParameter(formData);
        toast.success('参数创建成功');
      }

      setShowModal(false);
      fetchParameters();
      resetForm();
    } catch (error) {
      console.error('保存参数失败:', error);
      toast.error('保存参数失败');
    }
  };

  // 获取参数类型显示名称
  const getParamTypeDisplay = (paramType: string) => {
    const types: { [key: string]: { name: string; color: string } } = {
      string: { name: '字符串', color: 'bg-blue-100 text-blue-800' },
      number: { name: '数字', color: 'bg-green-100 text-green-800' },
      boolean: { name: '布尔值', color: 'bg-purple-100 text-purple-800' },
      json: { name: 'JSON', color: 'bg-orange-100 text-orange-800' },
    };
    return types[paramType] || { name: paramType, color: 'bg-gray-100 text-gray-800' };
  };

  // 过滤参数列表
  const filteredParameters = parameters.filter(param =>
    param.param_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    param.param_value.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (param.description && param.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleExport = () => {
    try {
      const jsonData = JSON.stringify(parameters, null, 2);
      const blob = new Blob([jsonData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `system_parameters_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('参数导出成功');
    } catch (error) {
      console.error('导出参数失败:', error);
      toast.error('导出参数失败');
    }
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const jsonData = e.target?.result as string;
        const importedParams = JSON.parse(jsonData);
        
        if (!Array.isArray(importedParams)) {
          toast.error('参数导入失败，文件格式不正确');
          return;
        }

        for (const param of importedParams) {
          try {
            await apiClient.createParameter({
              param_name: param.param_name,
              param_value: param.param_value,
              param_type: param.param_type,
              description: param.description
            });
          } catch (error) {
            console.error('导入参数失败:', param, error);
          }
        }

        toast.success('参数导入成功');
        fetchParameters();
      } catch (error) {
        console.error('导入参数失败:', error);
        toast.error('导入参数失败，请检查文件格式');
      }
    };
    reader.readAsText(file);
    
    event.target.value = '';
  };

  const handleReset = () => {
    toast.info('重置功能暂不可用，请手动删除参数');
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">参数管理</h1>
        <p className="text-gray-600 mt-1">管理系统配置参数和设置</p>
      </div>

      {/* 操作栏 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        {/* 搜索 */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="搜索参数名称、值或描述..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* 操作按钮 */}
        <div className="flex space-x-2">
          <button
            onClick={fetchParameters}
            className="btn btn-secondary flex items-center space-x-2"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>刷新</span>
          </button>
          <button
            onClick={handleExport}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>导出</span>
          </button>
          <label className="btn btn-secondary flex items-center space-x-2 cursor-pointer">
            <Upload className="h-4 w-4" />
            <span>导入</span>
            <input
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
          </label>
          <button
            onClick={handleReset}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RotateCcw className="h-4 w-4" />
            <span>重置</span>
          </button>
          <button
            onClick={handleAdd}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>新增参数</span>
          </button>
        </div>
      </div>

      {/* 参数列表 */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
            <span className="ml-2 text-gray-500">加载中...</span>
          </div>
        ) : filteredParameters.length === 0 ? (
          <div className="text-center py-8">
            <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm ? '未找到匹配的参数' : '暂无系统参数'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    参数信息
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    参数值
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    更新时间
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredParameters.map((param) => {
                  const typeInfo = getParamTypeDisplay(param.param_type);
                  
                  return (
                    <tr key={param.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                            <Settings className="h-5 w-5 text-white" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {param.param_name}
                            </div>
                            {param.description && (
                              <div className="text-sm text-gray-500">
                                {param.description}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs truncate">
                          {param.param_value}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${typeInfo.color}`}>
                          {typeInfo.name}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {param.updated_at ? formatDateTime(param.updated_at) : formatDateTime(param.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEdit(param)}
                            className="text-primary-600 hover:text-primary-700"
                            title="编辑"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(param.id, param.param_name)}
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

      {/* 参数表单模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editingParam ? '编辑参数' : '新增参数'}
            </h2>

            <div className="space-y-4">
              <div>
                <label className="label">参数名称 *</label>
                <input
                  type="text"
                  className="input"
                  value={formData.param_name}
                  onChange={(e) => setFormData({ ...formData, param_name: e.target.value })}
                  placeholder="请输入参数名称"
                />
              </div>

              <div>
                <label className="label">参数值 *</label>
                {formData.param_type === 'boolean' ? (
                  <select
                    className="input"
                    value={formData.param_value}
                    onChange={(e) => setFormData({ ...formData, param_value: e.target.value })}
                  >
                    <option value="">请选择</option>
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : formData.param_type === 'json' ? (
                  <textarea
                    className="input resize-none h-20"
                    value={formData.param_value}
                    onChange={(e) => setFormData({ ...formData, param_value: e.target.value })}
                    placeholder="请输入JSON格式的参数值"
                  />
                ) : (
                  <input
                    type={formData.param_type === 'number' ? 'number' : 'text'}
                    className="input"
                    value={formData.param_value}
                    onChange={(e) => setFormData({ ...formData, param_value: e.target.value })}
                    placeholder="请输入参数值"
                  />
                )}
              </div>

              <div>
                <label className="label">参数类型</label>
                <select
                  className="input"
                  value={formData.param_type}
                  onChange={(e) => setFormData({ ...formData, param_type: e.target.value, param_value: '' })}
                >
                  <option value="string">字符串</option>
                  <option value="number">数字</option>
                  <option value="boolean">布尔值</option>
                  <option value="json">JSON对象</option>
                </select>
              </div>

              <div>
                <label className="label">参数描述</label>
                <textarea
                  className="input resize-none h-20"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="请输入参数描述"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={handleSave}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Save className="h-4 w-4" />
                <span>{editingParam ? '更新' : '创建'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 删除确认弹窗 */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">确认删除</h2>
                <p className="text-sm text-gray-500">此操作无法撤销</p>
              </div>
            </div>

            <div className="mb-6">
              <p className="text-gray-700">
                确定要删除参数 <span className="font-semibold text-gray-900">"{deletingParam?.name}"</span> 吗？
              </p>
              <p className="text-sm text-gray-500 mt-2">
                删除后该参数将无法恢复，请谨慎操作。
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelDelete}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={confirmDelete}
                className="btn btn-danger flex items-center space-x-2"
              >
                <Trash2 className="h-4 w-4" />
                <span>确认删除</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 系统参数分类说明 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">系统配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 数据保留天数</p>
            <p>• 文件上传大小限制</p>
            <p>• API请求超时时间</p>
            <p>• 批量处理数量限制</p>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="h-6 w-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">安全配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• JWT Token过期时间</p>
            <p>• 密码最小长度</p>
            <p>• 登录失败次数限制</p>
            <p>• 账户锁定时间</p>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Settings className="h-6 w-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">评估参数</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 高风险评估阈值</p>
            <p>• 各维度评估权重</p>
            <p>• 综合评估算法参数</p>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="h-6 w-6 text-orange-600" />
            <h3 className="text-lg font-semibold text-gray-900">数据库配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 数据库连接池大小</p>
            <p>• 查询超时时间</p>
            <p>• 数据库备份频率</p>
            <p>• 连接重试次数</p>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <RefreshCw className="h-6 w-6 text-indigo-600" />
            <h3 className="text-lg font-semibold text-gray-900">日志配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 日志级别设置</p>
            <p>• 日志保留天数</p>
            <p>• 日志文件最大大小</p>
            <p>• 日志轮转策略</p>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Settings className="h-6 w-6 text-pink-600" />
            <h3 className="text-lg font-semibold text-gray-900">模型配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 模型推理批处理大小</p>
            <p>• 模型置信度阈值</p>
            <p>• 模型更新检查频率</p>
            <p>• 推理超时时间</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParameterManagePage; 