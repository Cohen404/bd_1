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
  XCircle,
  BarChart3,
  TrendingUp,
  Clock
} from 'lucide-react';
import { LogEntry } from '@/types';
import { formatDateTime } from '@/utils/helpers';
import { LocalStorageManager, STORAGE_KEYS, LogItem, initializeDemoData } from '@/utils/localStorage';
import toast from 'react-hot-toast';

const LogManagePage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');
  const [filterAction, setFilterAction] = useState('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  // ===== 纯前端演示模式 - 特殊标记 =====
  // 获取日志列表（从localStorage读取）
  const fetchLogs = async () => {
    try {
      setLoading(true);
      console.log('开始获取日志数据...');
      
      // 初始化演示数据（如果还没有）
      initializeDemoData();
      console.log('演示数据初始化完成');
      
      // 从localStorage获取日志数据
      const logsList = LocalStorageManager.get<LogItem[]>(STORAGE_KEYS.LOGS, []);
      console.log('从localStorage获取到的日志数据:', logsList);
      
      // 验证和清理日志数据
      const convertedLogs: LogEntry[] = logsList.map((log, index) => ({
        id: log.id || index,
        user_id: log.user_id || '',
        username: log.username || '未知用户',
        action: log.action || 'UNKNOWN',
        resource: log.resource || '',
        details: log.details || '',
        ip_address: log.ip_address || '',
        user_agent: log.user_agent || '',
        created_at: log.created_at || new Date().toISOString()
      }));
      console.log('转换后的日志数据:', convertedLogs);
      
      setLogs(convertedLogs);
      console.log('日志数据设置完成，数量:', convertedLogs.length);
    } catch (error) {
      console.error('获取日志列表失败:', error);
      toast.error('获取日志列表失败');
    } finally {
      setLoading(false);
    }
  };
  // ============================================

  useEffect(() => {
    fetchLogs();
  }, []);

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
      case 'VIEW_DATA':
        return { icon: FileText, color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'EXPORT_DATA':
        return { icon: Download, color: 'text-green-600', bg: 'bg-green-100' };
      case 'CREATE_MODEL':
      case 'UPDATE_MODEL':
      case 'DELETE_MODEL':
        return { icon: BarChart3, color: 'text-orange-600', bg: 'bg-orange-100' };
      case 'RUN_EVALUATION':
        return { icon: TrendingUp, color: 'text-purple-600', bg: 'bg-purple-100' };
      case 'VIEW_RESULT':
        return { icon: BarChart3, color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'EXPORT_RESULT':
        return { icon: Download, color: 'text-green-600', bg: 'bg-green-100' };
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
      "时间,用户,操作,资源,详情,IP地址,浏览器\n" +
      filteredLogs.map(log => 
        `"${formatDateTime(log.created_at)}","${log.username || '未知用户'}","${log.action}","${log.resource}","${log.details || ''}","${log.ip_address || ''}","${log.user_agent || ''}"`
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

  // 导出JSON格式日志
  const handleExportLogsJSON = () => {
    const jsonContent = JSON.stringify(filteredLogs, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `系统日志_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('JSON格式日志导出成功');
  };

  // 清除所有过滤器
  const handleClearFilters = () => {
    setSearchTerm('');
    setFilterLevel('all');
    setFilterAction('all');
    setDateRange({ start: '', end: '' });
    toast.success('过滤器已清除');
  };

  // 过滤日志列表
  const filteredLogs = logs.filter(log => {
    const matchesSearch = !searchTerm || (
      (log.username && log.username.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (log.action && log.action.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (log.resource && log.resource.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (log.details && log.details.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const matchesLevel = filterLevel === 'all' || getLogLevel(log.action) === filterLevel;
    const matchesAction = filterAction === 'all' || log.action === filterAction;
    
    // 日期范围过滤
    let matchesDateRange = true;
    if (dateRange.start && dateRange.end) {
      const logDate = new Date(log.created_at);
      const startDate = new Date(dateRange.start);
      const endDate = new Date(dateRange.end);
      endDate.setHours(23, 59, 59, 999); // 包含结束日期的整天
      matchesDateRange = logDate >= startDate && logDate <= endDate;
    } else if (dateRange.start) {
      const logDate = new Date(log.created_at);
      const startDate = new Date(dateRange.start);
      matchesDateRange = logDate >= startDate;
    } else if (dateRange.end) {
      const logDate = new Date(log.created_at);
      const endDate = new Date(dateRange.end);
      endDate.setHours(23, 59, 59, 999);
      matchesDateRange = logDate <= endDate;
    }

    return matchesSearch && matchesLevel && matchesAction && matchesDateRange;
  });

  // 获取所有操作类型
  const actionTypes = Array.from(new Set(logs.map(log => log.action)));

  // 添加调试信息
  console.log('LogManagePage render - logs:', logs.length, 'loading:', loading);
  console.log('filteredLogs:', filteredLogs.length);

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">日志管理</h1>
        <p className="text-gray-600 mt-1">查看系统操作日志和审计记录</p>
        <p className="text-sm text-red-500 mt-2">调试信息: 日志数量 = {logs.length}, 加载状态 = {loading ? '加载中' : '已完成'}</p>
        <p className="text-sm text-blue-500 mt-1">过滤后日志数量 = {filteredLogs.length}</p>
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

            {/* 日期范围选择 */}
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <input
                type="date"
                className="input w-36"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                placeholder="开始日期"
              />
              <span className="text-gray-400">至</span>
              <input
                type="date"
                className="input w-36"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                placeholder="结束日期"
              />
            </div>
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
              onClick={handleClearFilters}
              className="btn btn-outline flex items-center space-x-2"
            >
              <Filter className="h-4 w-4" />
              <span>清除过滤</span>
            </button>
            <div className="relative group">
              <button className="btn btn-primary flex items-center space-x-2">
                <Download className="h-4 w-4" />
                <span>导出日志</span>
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <div className="py-1">
                  <button
                    onClick={handleExportLogs}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    导出为CSV格式
                  </button>
                  <button
                    onClick={handleExportLogsJSON}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    导出为JSON格式
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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

      {/* 详细统计图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 操作类型分布 */}
        <div className="card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">操作类型分布</h3>
          </div>
          <div className="space-y-3">
            {actionTypes.slice(0, 8).map(action => {
              const count = logs.filter(log => log.action === action).length;
              const percentage = logs.length > 0 ? (count / logs.length * 100).toFixed(1) : 0;
              return (
                <div key={action} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 truncate flex-1 mr-2">{action}</span>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-8">{count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 用户活动统计 */}
        <div className="card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">用户活动统计</h3>
          </div>
          <div className="space-y-3">
            {Array.from(new Set(logs.map(log => log.username).filter(Boolean))).slice(0, 6).map(username => {
              const userLogs = logs.filter(log => log.username === username);
              const recentLogs = userLogs.filter(log => {
                const logDate = new Date(log.created_at);
                const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
                return logDate >= oneDayAgo;
              });
              return (
                <div key={username} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-600">{username}</span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-500">总计: {userLogs.length}</span>
                    <span className="text-green-600">今日: {recentLogs.length}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

        {/* 时间分布统计 */}
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Clock className="h-5 w-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">24小时活动分布</h3>
        </div>
        <div className="grid grid-cols-12 gap-2">
          {Array.from({ length: 24 }, (_, hour) => {
            try {
              const hourLogs = logs.filter(log => {
                const logDate = new Date(log.created_at);
                return logDate.getHours() === hour;
              });
              const maxCount = Math.max(...Array.from({ length: 24 }, (_, h) => 
                logs.filter(log => new Date(log.created_at).getHours() === h).length
              ));
              const height = maxCount > 0 ? (hourLogs.length / maxCount * 100) : 0;
              
              return (
                <div key={hour} className="flex flex-col items-center">
                  <div className="w-full bg-gray-200 rounded-t h-20 flex items-end">
                    <div 
                      className="w-full bg-purple-500 rounded-t"
                      style={{ height: `${height}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-500 mt-1">{hour}:00</span>
                  <span className="text-xs font-medium text-gray-700">{hourLogs.length}</span>
                </div>
              );
            } catch (error) {
              console.error('Error rendering hour chart for hour', hour, error);
              return (
                <div key={hour} className="flex flex-col items-center">
                  <div className="w-full bg-gray-200 rounded-t h-20"></div>
                  <span className="text-xs text-gray-500 mt-1">{hour}:00</span>
                  <span className="text-xs font-medium text-gray-700">0</span>
                </div>
              );
            }
          })}
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
                            {log.username || '未知用户'}
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