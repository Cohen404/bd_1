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
import { ParameterStorage } from '@/utils/parameter-storage';
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
  const [formData, setFormData] = useState<ParameterFormData>({
    param_name: '',
    param_value: '',
    param_type: 'string',
    description: ''
  });

  // 获取参数列表
  const fetchParameters = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getParameters();
      setParameters(Array.isArray(response) ? response : response?.items || []);
    } catch (error) {
      console.error('获取参数列表失败:', error);
      toast.error('获取参数列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化默认参数数据
  const initializeDefaultParameters = () => {
    try {
      const stored = localStorage.getItem('system_parameters');
      if (!stored) {
        const defaultParams = ParameterStorage.getDefaultParameters();
        ParameterStorage.saveParameters(defaultParams);
        setParameters(defaultParams);
        toast.success('已初始化默认参数数据');
      }
    } catch (error) {
      console.error('初始化默认参数失败:', error);
      toast.error('初始化默认参数失败');
    }
  };

  useEffect(() => {
    fetchParameters();
    // 初始化默认参数数据
    initializeDefaultParameters();
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

  // 删除参数
  const handleDelete = async (paramId: number, paramName: string) => {
    if (!window.confirm(`确定要删除参数"${paramName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      await apiClient.deleteParameter(paramId);
      toast.success('参数删除成功');
      fetchParameters();
    } catch (error) {
      console.error('删除参数失败:', error);
      toast.error('删除参数失败');
    }
  };

  // 保存参数
  const handleSave = async () => {
    // 使用验证工具验证参数
    const validationErrors = validateParameter(formData);
    if (validationErrors.length > 0) {
      validationErrors.forEach(error => toast.error(error));
      return;
    }

    // 验证参数名称是否重复
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
        // 更新参数
        await apiClient.updateParameter(editingParam.id, formData);
        toast.success('参数更新成功');
      } else {
        // 创建参数
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

  // 导出参数
  const handleExport = () => {
    try {
      const jsonData = ParameterStorage.exportParameters();
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

  // 导入参数
  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const jsonData = e.target?.result as string;
        const success = ParameterStorage.importParameters(jsonData);
        if (success) {
          toast.success('参数导入成功');
          fetchParameters();
        } else {
          toast.error('参数导入失败，请检查文件格式');
        }
      } catch (error) {
        console.error('导入参数失败:', error);
        toast.error('导入参数失败');
      }
    };
    reader.readAsText(file);
    
    // 清空input值，允许重复选择同一文件
    event.target.value = '';
  };

  // 重置为默认参数
  const handleReset = () => {
    if (window.confirm('确定要重置为默认参数吗？此操作将清除所有现有参数。')) {
      try {
        ParameterStorage.resetToDefault();
        toast.success('已重置为默认参数');
        fetchParameters();
      } catch (error) {
        console.error('重置参数失败:', error);
        toast.error('重置参数失败');
      }
    }
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

      {/* 系统参数分类说明 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">系统配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 数据库连接配置</p>
            <p>• 文件存储路径设置</p>
            <p>• API接口超时时间</p>
            <p>• 系统运行模式配置</p>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="h-6 w-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">安全配置</h3>
          </div>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• JWT Token过期时间</p>
            <p>• 密码复杂度要求</p>
            <p>• 登录失败次数限制</p>
            <p>• 会话超时设置</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParameterManagePage; 