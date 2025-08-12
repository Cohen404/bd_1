import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  Filter, 
  RefreshCw, 
  Download,
  Calendar,
  User,
  Activity,
  AlertTriangle,
  CheckCircle,
  Info,
  XCircle
} from 'lucide-react';
import { apiClient } from '@/utils/api';
import { LogEntry } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import toast from 'react-hot-toast';

const LogManagePage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');
  const [filterAction, setFilterAction] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  // 获取日志列表
  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getLogs({ search: searchTerm });
      // 模拟日志数据，实际应从API获取
      const mockLogs: LogEntry[] = [
        {
          id: 1,
          user_id: '1',
          username: 'admin',
          action: 'LOGIN',
          resource: 'AUTH',
          details: '管理员登录系统',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          user_id: '1',
          username: 'admin',
          action: 'CREATE_USER',
          resource: 'USER_MANAGEMENT',
          details: '创建新用户: testuser',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          created_at: new Date(Date.now() - 300000).toISOString()
        },
        {
          id: 3,
          user_id: '2',
          username: 'user1',
          action: 'HEALTH_EVALUATE',
          resource: 'EVALUATION',
          details: '执行健康评估，数据ID: 123',
          ip_address: '192.168.1.101',
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          created_at: new Date(Date.now() - 600000).toISOString()
        },
        {
          id: 4,
          user_id: '1',
          username: 'admin',
          action: 'DELETE_DATA',
          resource: 'DATA_MANAGEMENT',
          details: '删除数据文件: old_data.csv',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          created_at: new Date(Date.now() - 900000).toISOString()
        },
        {
          id: 5,
          user_id: '3',
          username: 'user2',
          action: 'UPLOAD_DATA',
          resource: 'DATA_MANAGEMENT',
          details: '上传新数据文件: subject_new.csv',
          ip_address: '192.168.1.102',
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          created_at: new Date(Date.now() - 1200000).toISOString()
        }
      ];
      setLogs(mockLogs);
    } catch (error) {
      console.error('获取日志列表失败:', error);
      toast.error('获取日志列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [searchTerm]);

  // 获取操作类型图标和颜色
  const getActionIcon = (action: string) => {
    switch (action) {
      case 'LOGIN':
        return { icon: User, color: 'text-green-600', bg: 'bg-green-100' };
      case 'LOGOUT':
        return { icon: User, color: 'text-gray-600', bg: 'bg-gray-100' };
      case 'CREATE_USER':
      case 'UPDATE_USER':
      case 'DELETE_USER':
        return { icon: User, color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'HEALTH_EVALUATE':
        return { icon: Activity, color: 'text-purple-600', bg: 'bg-purple-100' };
      case 'UPLOAD_DATA':
      case 'DELETE_DATA':
        return { icon: FileText, color: 'text-orange-600', bg: 'bg-orange-100' };
      case 'ERROR':
        return { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-100' };
      default:
        return { icon: Info, color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  // 获取日志级别
  const getLogLevel = (action: string) => {
    if (action.includes('ERROR') || action.includes('DELETE')) return 'error';
    if (action.includes('CREATE') || action.includes('UPDATE')) return 'warning';
    if (action.includes('LOGIN') || action.includes('EVALUATE')) return 'success';
    return 'info';
  };

  // 导出日志
  const handleExportLogs = () => {
    const csvContent = "data:text/csv;charset=utf-8," + 
      "时间,用户,操作,资源,详情,IP地址\n" +
      filteredLogs.map(log => 
        `"${formatDateTime(log.created_at)}","${log.username}","${log.action}","${log.resource}","${log.details}","${log.ip_address}"`
      ).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `系统日志_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('日志导出成功');
  };

  // 过滤日志列表
  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.details && log.details.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesLevel = filterLevel === 'all' || getLogLevel(log.action) === filterLevel;
    const matchesAction = filterAction === 'all' || log.action === filterAction;

    return matchesSearch && matchesLevel && matchesAction;
  });

  // 获取所有操作类型
  const actionTypes = Array.from(new Set(logs.map(log => log.action)));

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">日志管理</h1>
        <p className="text-gray-600 mt-1">查看系统操作日志和审计记录</p>
      </div>

      {/* 操作栏 */}
      <div className="card p-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          {/* 搜索和过滤 */}
          <div className="flex flex-col sm:flex-row gap-4 flex-1">
            {/* 搜索 */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="搜索用户、操作或详情..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* 级别过滤 */}
            <select
              className="input w-32"
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
            >
              <option value="all">所有级别</option>
              <option value="info">信息</option>
              <option value="success">成功</option>
              <option value="warning">警告</option>
              <option value="error">错误</option>
            </select>

            {/* 操作过滤 */}
            <select
              className="input w-40"
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
            >
              <option value="all">所有操作</option>
              {actionTypes.map(action => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
          </div>

          {/* 操作按钮 */}
          <div className="flex space-x-2">
            <button
              onClick={fetchLogs}
              className="btn btn-secondary flex items-center space-x-2"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>刷新</span>
            </button>
            <button
              onClick={handleExportLogs}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>导出日志</span>
            </button>
          </div>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">总日志数</p>
              <p className="text-lg font-bold text-gray-900">{logs.length}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">成功操作</p>
              <p className="text-lg font-bold text-gray-900">
                {logs.filter(log => getLogLevel(log.action) === 'success').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">警告操作</p>
              <p className="text-lg font-bold text-gray-900">
                {logs.filter(log => getLogLevel(log.action) === 'warning').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">错误操作</p>
              <p className="text-lg font-bold text-gray-900">
                {logs.filter(log => getLogLevel(log.action) === 'error').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 日志列表 */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent"></div>
            <span className="ml-2 text-gray-500">加载中...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm || filterLevel !== 'all' || filterAction !== 'all' 
                ? '未找到匹配的日志记录' 
                : '暂无日志记录'
              }
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto custom-scrollbar">
            {filteredLogs.map((log) => {
              const actionInfo = getActionIcon(log.action);
              const level = getLogLevel(log.action);
              
              return (
                <div key={log.id} className="p-4 hover:bg-gray-50">
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${actionInfo.bg} flex-shrink-0`}>
                      <actionInfo.icon className={`h-4 w-4 ${actionInfo.color}`} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900">
                            {log.username}
                          </p>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            level === 'error' ? 'bg-red-100 text-red-800' :
                            level === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                            level === 'success' ? 'bg-green-100 text-green-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {log.action}
                          </span>
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            {log.resource}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {formatDateTime(log.created_at)}
                        </p>
                      </div>
                      
                      <p className="mt-1 text-sm text-gray-600">
                        {log.details}
                      </p>
                      
                      <div className="mt-2 flex items-center text-xs text-gray-400 space-x-4">
                        <span>IP: {log.ip_address}</span>
                        <span title={log.user_agent}>
                          浏览器: {log.user_agent?.split(' ')[0]}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 日志说明 */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">日志级别说明</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-600">信息 - 一般操作记录</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">成功 - 操作成功完成</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-gray-600">警告 - 重要操作记录</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-sm text-gray-600">错误 - 删除等危险操作</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogManagePage; 