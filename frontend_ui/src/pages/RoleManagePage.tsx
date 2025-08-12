import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Key,
  Users,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { Role, Permission } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';

interface RoleFormData {
  role_name: string;
  description: string;
}

const RoleManagePage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [rolePermissions, setRolePermissions] = useState<Permission[]>([]);
  const [formData, setFormData] = useState<RoleFormData>({
    role_name: '',
    description: ''
  });

  // 获取角色列表
  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getRoles();
      setRoles(Array.isArray(response) ? response : response?.items || []);
    } catch (error) {
      console.error('获取角色列表失败:', error);
      toast.error('获取角色列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取权限列表
  const fetchPermissions = async () => {
    try {
      // 模拟权限数据，实际应从API获取
      const mockPermissions: Permission[] = [
        { permission_id: 1, permission_name: '用户管理', description: '管理系统用户', resource: 'user', action: 'manage' },
        { permission_id: 2, permission_name: '角色管理', description: '管理用户角色', resource: 'role', action: 'manage' },
        { permission_id: 3, permission_name: '数据管理', description: '管理数据文件', resource: 'data', action: 'manage' },
        { permission_id: 4, permission_name: '结果管理', description: '管理评估结果', resource: 'result', action: 'manage' },
        { permission_id: 5, permission_name: '模型管理', description: '管理AI模型', resource: 'model', action: 'manage' },
        { permission_id: 6, permission_name: '应激评估', description: '执行健康评估', resource: 'evaluation', action: 'execute' },
        { permission_id: 7, permission_name: '参数管理', description: '管理系统参数', resource: 'parameter', action: 'manage' },
        { permission_id: 8, permission_name: '日志管理', description: '查看系统日志', resource: 'log', action: 'view' },
      ];
      setPermissions(mockPermissions);
    } catch (error) {
      console.error('获取权限列表失败:', error);
    }
  };

  // 获取角色权限
  const fetchRolePermissions = async (roleId: number) => {
    try {
      const response = await apiClient.getRolePermissions(roleId);
      setRolePermissions(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('获取角色权限失败:', error);
      setRolePermissions([]);
    }
  };

  useEffect(() => {
    fetchRoles();
    fetchPermissions();
  }, []);

  // 重置表单
  const resetForm = () => {
    setFormData({
      role_name: '',
      description: ''
    });
    setEditingRole(null);
  };

  // 打开新增角色模态框
  const handleAdd = () => {
    resetForm();
    setShowModal(true);
  };

  // 打开编辑角色模态框
  const handleEdit = (role: Role) => {
    setEditingRole(role);
    setFormData({
      role_name: role.role_name,
      description: role.description || ''
    });
    setShowModal(true);
  };

  // 查看角色权限
  const handleViewPermissions = async (role: Role) => {
    setSelectedRole(role);
    await fetchRolePermissions(role.role_id);
    setShowPermissionsModal(true);
  };

  // 删除角色
  const handleDelete = async (roleId: number, roleName: string) => {
    if (!window.confirm(`确定要删除角色"${roleName}"吗？此操作无法撤销。`)) {
      return;
    }

    try {
      await apiClient.deleteRole(roleId);
      toast.success('角色删除成功');
      fetchRoles();
    } catch (error) {
      console.error('删除角色失败:', error);
      toast.error('删除角色失败');
    }
  };

  // 保存角色
  const handleSave = async () => {
    if (!formData.role_name.trim()) {
      toast.error('请输入角色名称');
      return;
    }

    try {
      if (editingRole) {
        // 更新角色
        await apiClient.updateRole(editingRole.role_id, formData);
        toast.success('角色更新成功');
      } else {
        // 创建角色
        await apiClient.createRole(formData);
        toast.success('角色创建成功');
      }

      setShowModal(false);
      fetchRoles();
      resetForm();
    } catch (error) {
      console.error('保存角色失败:', error);
      toast.error('保存角色失败');
    }
  };

  // 过滤角色列表
  const filteredRoles = roles.filter(role =>
    role.role_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (role.description && role.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // 检查角色是否有某个权限
  const hasPermission = (permissionId: number) => {
    return rolePermissions.some(p => p.permission_id === permissionId);
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">角色管理</h1>
        <p className="text-gray-600 mt-1">管理用户角色和权限配置</p>
      </div>

      {/* 操作栏 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        {/* 搜索 */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="搜索角色名称或描述..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* 新增按钮 */}
        <button
          onClick={handleAdd}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>新增角色</span>
        </button>
      </div>

      {/* 角色列表 */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
            <span className="ml-2 text-gray-500">加载中...</span>
          </div>
        ) : filteredRoles.length === 0 ? (
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm ? '未找到匹配的角色' : '暂无角色数据'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    角色信息
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    描述
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
                {filteredRoles.map((role) => (
                  <tr key={role.role_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                          <Shield className="h-5 w-5 text-white" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {role.role_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-500">
                        {role.description || '暂无描述'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDateTime(role.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleViewPermissions(role)}
                          className="text-blue-600 hover:text-blue-700"
                          title="查看权限"
                        >
                          <Key className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(role)}
                          className="text-primary-600 hover:text-primary-700"
                          title="编辑"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(role.role_id, role.role_name)}
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

      {/* 角色表单模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editingRole ? '编辑角色' : '新增角色'}
            </h2>

            <div className="space-y-4">
              <div>
                <label className="label">角色名称 *</label>
                <input
                  type="text"
                  className="input"
                  value={formData.role_name}
                  onChange={(e) => setFormData({ ...formData, role_name: e.target.value })}
                  placeholder="请输入角色名称"
                />
              </div>

              <div>
                <label className="label">角色描述</label>
                <textarea
                  className="input resize-none h-20"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="请输入角色描述"
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
                className="btn btn-primary"
              >
                {editingRole ? '更新' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 角色权限查看模态框 */}
      {showPermissionsModal && selectedRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                {selectedRole.role_name} - 权限配置
              </h2>
              <button
                onClick={() => setShowPermissionsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-3">
              {permissions.map((permission) => (
                <div
                  key={permission.permission_id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">
                      {permission.permission_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {permission.description}
                    </div>
                  </div>
                  <div className="flex items-center">
                    {hasPermission(permission.permission_id) ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-gray-300" />
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowPermissionsModal(false)}
                className="btn btn-secondary"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleManagePage; 