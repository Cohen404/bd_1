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
  AlertTriangle
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Data } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';

const DataManagePage: React.FC = () => {
  const [dataList, setDataList] = useState<Data[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [visualizationType, setVisualizationType] = useState('differential_entropy');
  const [showVisualization, setShowVisualization] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    personnel_id: '',
    personnel_name: '',
    file: null as File | null
  });

  // 可视化指标选项
  const visualizationOptions = [
    { value: 'differential_entropy', label: 'Differential Entropy' },
    { value: 'frequency_domain_features', label: 'Frequency Domain Features' },
    { value: 'theta_alpha_beta_gamma_powers', label: 'Theta Alpha Beta Gamma Powers' },
    { value: 'time_domain_features', label: 'Time Domain Features' },
    { value: 'time_frequency_features', label: 'Time Frequency Features' }
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

  useEffect(() => {
    fetchData();
  }, [searchTerm]);

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
  const selectTop200 = () => {
    const top200 = dataList.slice(0, 200).map(item => item.id);
    setSelectedItems(new Set(top200));
    toast.success(`已选择前${Math.min(200, dataList.length)}条数据`);
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
      await Promise.all(selectedIds.map(id => apiClient.deleteData(id)));
      toast.success(`已删除${selectedIds.length}条数据`);
      setSelectedItems(new Set());
      fetchData();
    } catch (error) {
      console.error('批量删除失败:', error);
      toast.error('批量删除失败');
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
            onClick={() => toast('批量预处理功能正在开发中', { icon: '🔧' })}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Settings className="h-4 w-4" />
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
              已选择: {selectedItems.size}/{Math.min(200, filteredData.length)}
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
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              onClick={() => toast('查看功能正在开发中', { icon: '👁️' })}
                              className="text-blue-600 hover:text-blue-700"
                              title="查看详情"
                            >
                              <Eye className="h-4 w-4" />
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
              <div className="bg-white rounded-lg p-4 min-h-[200px] flex items-center justify-center border-2 border-dashed border-gray-300">
                {showVisualization ? (
                  <div className="text-center">
                    <BarChart3 className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">图表显示区域</p>
                    <p className="text-xs text-gray-400 mt-1">当前指标: {visualizationOptions.find(opt => opt.value === visualizationType)?.label}</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <Database className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">请选择数据查看可视化</p>
                  </div>
                )}
              </div>

              <button 
                className="btn btn-primary w-full flex items-center justify-center space-x-2"
                onClick={() => setShowVisualization(!showVisualization)}
              >
                <Eye className="h-4 w-4" />
                <span>图片查看</span>
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
                  accept=".csv,.xlsx,.xls"
                  className="input"
                  onChange={(e) => setFormData({ ...formData, file: e.target.files?.[0] || null })}
                />
                <p className="text-xs text-gray-500 mt-1">支持格式：CSV、Excel文件</p>
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
    </div>
  );
};

export default DataManagePage; 