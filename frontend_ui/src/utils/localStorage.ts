// ===== 纯前端演示模式 - localStorage存储工具 =====
// 此文件提供localStorage数据存储和读取功能
// 用于在纯前端模式下模拟后端数据存储
// ============================================

// 存储键名常量
export const STORAGE_KEYS = {
  USERS: 'demo_users',
  ROLES: 'demo_roles',
  DATA: 'demo_data',
  RESULTS: 'demo_results',
  MODELS: 'demo_models',
  PARAMETERS: 'demo_parameters',
  LOGS: 'demo_logs',
  CURRENT_USER: 'demo_current_user',
  DEMO_INITIALIZED: 'demo_initialized' // 标记是否已初始化演示数据
} as const;

// 数据类型定义
export interface User {
  id: number;
  username: string;
  password: string;
  role: string;
  created_at: string;
  last_login?: string;
}

export interface Role {
  id: number;
  name: string;
  permissions: string[];
  created_at: string;
}

export interface DataItem {
  id: number;
  name: string;
  description: string;
  file_path: string;
  file_size: number;
  upload_time: string;
  uploader: string;
  status: string;
}

export interface ResultItem {
  id: number;
  user_id: number;
  username: string;
  result_time: string;
  stress_score: number;
  depression_score: number;
  anxiety_score: number;
  social_isolation_score: number;
  overall_risk_level: string;
  recommendations: string;
  personnel_id?: string;
  personnel_name?: string;
  active_learned?: boolean;
  blood_oxygen?: number;
  blood_pressure?: string;
}

export interface Model {
  id: number;
  name: string;
  version: string;
  description: string;
  status: string;
  created_at: string;
  accuracy: number;
}

export interface Parameter {
  id: number;
  name: string;
  value: string;
  description: string;
  category: string;
  updated_at: string;
  param_name?: string;  // 兼容API类型
  param_value?: string; // 兼容API类型
  param_type?: string;  // 兼容API类型
  created_at?: string;  // 兼容API类型
}

export interface LogItem {
  id: number;
  user_id: string;
  username: string;
  action: string;
  resource: string;
  details?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

// 通用存储操作
export class LocalStorageManager {
  // 获取数据
  static get<T>(key: string, defaultValue: T): T {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`获取localStorage数据失败 (${key}):`, error);
      return defaultValue;
    }
  }

  // 保存数据
  static set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`保存localStorage数据失败 (${key}):`, error);
    }
  }

  // 删除数据
  static remove(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`删除localStorage数据失败 (${key}):`, error);
    }
  }

  // 清空所有演示数据
  static clearDemoData(): void {
    Object.values(STORAGE_KEYS).forEach(key => {
      this.remove(key);
    });
  }
  
  // 清空特定类型的数据（保留初始化标记）
  static clearSpecificData(dataType: 'data' | 'results' | 'users' | 'logs'): void {
    switch (dataType) {
      case 'data':
        this.remove(STORAGE_KEYS.DATA);
        break;
      case 'results':
        this.remove(STORAGE_KEYS.RESULTS);
        break;
      case 'users':
        this.remove(STORAGE_KEYS.USERS);
        break;
      case 'logs':
        this.remove(STORAGE_KEYS.LOGS);
        break;
    }
  }
}

// 初始化演示数据
export const initializeDemoData = () => {
  // 检查是否已经初始化过演示数据
  const isInitialized = LocalStorageManager.get<boolean>(STORAGE_KEYS.DEMO_INITIALIZED, false);
  
  // 如果已经初始化过，不再自动初始化
  if (isInitialized) {
    return;
  }
  
  // 初始化用户数据
  const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
  if (users.length === 0) {
    const demoUsers: User[] = [
      {
        id: 1,
        username: 'admin',
        password: 'admin123',
        role: 'admin',
        created_at: '2024-01-01T00:00:00Z',
        last_login: new Date().toISOString()
      },
      {
        id: 2,
        username: 'user',
        password: 'user123',
        role: 'user',
        created_at: '2024-01-01T00:00:00Z',
        last_login: new Date().toISOString()
      }
    ];
    LocalStorageManager.set(STORAGE_KEYS.USERS, demoUsers);
  }

  // 初始化角色数据
  const roles = LocalStorageManager.get<Role[]>(STORAGE_KEYS.ROLES, []);
  if (roles.length === 0) {
    const demoRoles: Role[] = [
      {
        id: 1,
        name: '系统管理员',
        permissions: ['user_manage', 'role_manage', 'model_manage', 'parameter_manage', 'log_manage', 'data_manage', 'result_manage', 'evaluation'],
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 2,
        name: '普通用户',
        permissions: ['data_manage', 'result_manage', 'evaluation'],
        created_at: '2024-01-01T00:00:00Z'
      }
    ];
    LocalStorageManager.set(STORAGE_KEYS.ROLES, demoRoles);
  }

  // 初始化数据文件
  const dataItems = LocalStorageManager.get<DataItem[]>(STORAGE_KEYS.DATA, []);
  if (dataItems.length === 0) {
    const demoData: DataItem[] = [
      {
        id: 1,
        name: '心理健康评估数据_2024Q1.csv',
        description: '2024年第一季度心理健康评估数据',
        file_path: '/uploads/data/mental_health_q1_2024.csv',
        file_size: 1024000,
        upload_time: '2024-01-15T10:30:00Z',
        uploader: 'admin',
        status: '待处理'
      },
      {
        id: 2,
        name: '员工压力测试数据.xlsx',
        description: '员工工作压力测试数据',
        file_path: '/uploads/data/employee_stress_test.xlsx',
        file_size: 512000,
        upload_time: '2024-01-20T14:20:00Z',
        uploader: 'user',
        status: '待处理'
      },
      {
        id: 3,
        name: '焦虑症筛查数据.csv',
        description: '焦虑症筛查问卷数据',
        file_path: '/uploads/data/anxiety_screening.csv',
        file_size: 768000,
        upload_time: '2024-02-01T09:15:00Z',
        uploader: 'admin',
        status: '待处理'
      }
    ];
    LocalStorageManager.set(STORAGE_KEYS.DATA, demoData);
  }

  // 初始化评估结果
  const results = LocalStorageManager.get<ResultItem[]>(STORAGE_KEYS.RESULTS, []);
  // 检查是否有旧数据需要更新人员信息
  const needsUpdate = results.some(result => !result.personnel_id || !result.personnel_name || result.personnel_id === 'unknown');
  
  if (results.length === 0 || needsUpdate) {
    const demoResults: ResultItem[] = [
      {
        id: 1,
        user_id: 2,
        username: 'user',
        result_time: '2024-01-15T10:30:00Z',
        stress_score: 35,
        depression_score: 28,
        anxiety_score: 42,
        social_isolation_score: 25,
        overall_risk_level: '中等',
        recommendations: '建议进行放松训练，适当增加社交活动',
        personnel_id: 'P001',
        personnel_name: '张三'
      },
      {
        id: 2,
        user_id: 2,
        username: 'user',
        result_time: '2024-01-20T14:20:00Z',
        stress_score: 45,
        depression_score: 38,
        anxiety_score: 35,
        social_isolation_score: 30,
        overall_risk_level: '中等',
        recommendations: '建议寻求专业心理咨询，注意工作生活平衡',
        personnel_id: 'P002',
        personnel_name: '李四'
      },
      {
        id: 3,
        user_id: 2,
        username: 'user',
        result_time: '2024-02-01T09:15:00Z',
        stress_score: 28,
        depression_score: 22,
        anxiety_score: 30,
        social_isolation_score: 20,
        overall_risk_level: '低',
        recommendations: '保持良好的心理状态，继续当前的生活方式',
        personnel_id: 'P003',
        personnel_name: '王五'
      }
    ];
    
    if (results.length === 0) {
      // 如果没有数据，直接设置演示数据
      LocalStorageManager.set(STORAGE_KEYS.RESULTS, demoResults);
    } else {
      // 如果有数据但需要更新，更新现有数据的人员信息
      const updatedResults = results.map(result => {
        const demoResult = demoResults.find(demo => demo.id === result.id);
        if (demoResult) {
          return {
            ...result,
            personnel_id: demoResult.personnel_id,
            personnel_name: demoResult.personnel_name
          };
        }
        return result;
      });
      LocalStorageManager.set(STORAGE_KEYS.RESULTS, updatedResults);
    }
  }

  // 初始化AI模型
  const models = LocalStorageManager.get<Model[]>(STORAGE_KEYS.MODELS, []);
  if (models.length === 0) {
    const demoModels: Model[] = [
      {
        id: 1,
        name: '心理健康评估模型',
        version: 'v2.1.0',
        description: '基于深度学习的心理健康综合评估模型',
        status: '已部署',
        created_at: '2024-01-01T00:00:00Z',
        accuracy: 0.92
      },
      {
        id: 2,
        name: '压力检测模型',
        version: 'v1.8.5',
        description: '专门用于检测工作压力的AI模型',
        status: '已部署',
        created_at: '2024-01-01T00:00:00Z',
        accuracy: 0.88
      },
      {
        id: 3,
        name: '抑郁风险评估模型',
        version: 'v3.0.1',
        description: '高精度抑郁风险预测模型',
        status: '已部署',
        created_at: '2024-01-01T00:00:00Z',
        accuracy: 0.95
      },
      {
        id: 4,
        name: '焦虑症状识别模型',
        version: 'v2.3.2',
        description: '焦虑症状早期识别和预警模型',
        status: '已部署',
        created_at: '2024-01-01T00:00:00Z',
        accuracy: 0.90
      }
    ];
    LocalStorageManager.set(STORAGE_KEYS.MODELS, demoModels);
  }

  // 初始化系统参数
  const parameters = LocalStorageManager.get<Parameter[]>(STORAGE_KEYS.PARAMETERS, []);
  if (parameters.length === 0) {
    const demoParameters: Parameter[] = [
      // 评估参数
      {
        id: 1,
        name: '评估阈值_高风险',
        value: '50',
        description: '高风险评估阈值，超过此分数将被标记为高风险',
        category: '评估参数',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 2,
        name: '评估阈值_中等风险',
        value: '30',
        description: '中等风险评估阈值，超过此分数将被标记为中等风险',
        category: '评估参数',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 3,
        name: '评估阈值_低风险',
        value: '15',
        description: '低风险评估阈值，低于此分数将被标记为低风险',
        category: '评估参数',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 4,
        name: '评估权重_压力',
        value: '0.3',
        description: '压力评估在综合评估中的权重',
        category: '评估参数',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 5,
        name: '评估权重_抑郁',
        value: '0.25',
        description: '抑郁评估在综合评估中的权重',
        category: '评估参数',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 6,
        name: '评估权重_焦虑',
        value: '0.25',
        description: '焦虑评估在综合评估中的权重',
        category: '评估参数',
        updated_at: '2024-01-01T00:00:00Z'
      },
      
      // 系统配置
      {
        id: 8,
        name: '数据保留天数',
        value: '365',
        description: '系统数据保留天数，超过此天数的数据将被自动清理',
        category: '系统配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 9,
        name: '文件上传大小限制',
        value: '10485760',
        description: '单个文件上传大小限制（字节），默认10MB',
        category: '系统配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 10,
        name: '批量处理数量限制',
        value: '100',
        description: '批量处理数据文件的数量限制',
        category: '系统配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 11,
        name: 'API请求超时时间',
        value: '30',
        description: 'API请求超时时间（秒）',
        category: '系统配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 12,
        name: '模型推理超时时间',
        value: '60',
        description: 'AI模型推理超时时间（秒）',
        category: '系统配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      
      // 安全配置
      {
        id: 13,
        name: 'JWT Token过期时间',
        value: '7200',
        description: 'JWT Token过期时间（秒），默认2小时',
        category: '安全配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 14,
        name: '密码最小长度',
        value: '8',
        description: '用户密码最小长度要求',
        category: '安全配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 15,
        name: '登录失败次数限制',
        value: '5',
        description: '登录失败次数限制，超过此次数将锁定账户',
        category: '安全配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 16,
        name: '账户锁定时间',
        value: '1800',
        description: '账户锁定时间（秒），默认30分钟',
        category: '安全配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 17,
        name: '会话超时时间',
        value: '3600',
        description: '用户会话超时时间（秒），默认1小时',
        category: '安全配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      
      // 数据库配置
      {
        id: 18,
        name: '数据库连接池大小',
        value: '10',
        description: '数据库连接池最大连接数',
        category: '数据库配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 19,
        name: '数据库查询超时时间',
        value: '30',
        description: '数据库查询超时时间（秒）',
        category: '数据库配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 20,
        name: '数据库备份频率',
        value: 'daily',
        description: '数据库备份频率，可选值：hourly, daily, weekly',
        category: '数据库配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      
      // 日志配置
      {
        id: 21,
        name: '日志级别',
        value: 'INFO',
        description: '系统日志级别，可选值：DEBUG, INFO, WARN, ERROR',
        category: '日志配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 22,
        name: '日志保留天数',
        value: '30',
        description: '日志文件保留天数',
        category: '日志配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 23,
        name: '日志文件最大大小',
        value: '10485760',
        description: '单个日志文件最大大小（字节），默认10MB',
        category: '日志配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      
      // 邮件配置
      {
        id: 24,
        name: '邮件服务器地址',
        value: 'smtp.example.com',
        description: 'SMTP邮件服务器地址',
        category: '邮件配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 25,
        name: '邮件服务器端口',
        value: '587',
        description: 'SMTP邮件服务器端口',
        category: '邮件配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 26,
        name: '邮件发送者地址',
        value: 'noreply@example.com',
        description: '系统邮件发送者地址',
        category: '邮件配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      
      // 模型配置
      {
        id: 27,
        name: '模型推理批处理大小',
        value: '32',
        description: 'AI模型推理时的批处理大小',
        category: '模型配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 28,
        name: '模型置信度阈值',
        value: '0.8',
        description: '模型预测结果的最小置信度阈值',
        category: '模型配置',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 29,
        name: '模型更新检查频率',
        value: 'daily',
        description: '检查模型更新的频率，可选值：hourly, daily, weekly',
        category: '模型配置',
        updated_at: '2024-01-01T00:00:00Z'
      }
    ];
    LocalStorageManager.set(STORAGE_KEYS.PARAMETERS, demoParameters);
  }

  // 初始化日志数据
  const logs = LocalStorageManager.get<LogItem[]>(STORAGE_KEYS.LOGS, []);
  if (logs.length === 0) {
    const now = new Date();
    const demoLogs: LogItem[] = [
      // 最近的登录日志
      {
        id: 1,
        user_id: '1',
        username: 'admin',
        action: 'LOGIN',
        resource: 'AUTH',
        details: '管理员登录系统',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 5 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        user_id: '2',
        username: 'user',
        action: 'LOGIN',
        resource: 'AUTH',
        details: '普通用户登录系统',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 10 * 60 * 1000).toISOString()
      },
      
      // 用户管理操作
      {
        id: 3,
        user_id: '1',
        username: 'admin',
        action: 'CREATE_USER',
        resource: 'USER_MANAGEMENT',
        details: '创建新用户: testuser',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 15 * 60 * 1000).toISOString()
      },
      {
        id: 4,
        user_id: '1',
        username: 'admin',
        action: 'UPDATE_USER',
        resource: 'USER_MANAGEMENT',
        details: '更新用户信息: user',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 20 * 60 * 1000).toISOString()
      },
      
      // 数据管理操作
      {
        id: 5,
        user_id: '2',
        username: 'user',
        action: 'UPLOAD_DATA',
        resource: 'DATA_MANAGEMENT',
        details: '上传数据文件: mental_health_data.csv',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 25 * 60 * 1000).toISOString()
      },
      {
        id: 6,
        user_id: '1',
        username: 'admin',
        action: 'DELETE_DATA',
        resource: 'DATA_MANAGEMENT',
        details: '删除数据文件: old_data.csv',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 30 * 60 * 1000).toISOString()
      },
      
      // 健康评估操作
      {
        id: 7,
        user_id: '2',
        username: 'user',
        action: 'HEALTH_EVALUATE',
        resource: 'EVALUATION',
        details: '执行健康评估，数据ID: 123',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 35 * 60 * 1000).toISOString()
      },
      {
        id: 8,
        user_id: '1',
        username: 'admin',
        action: 'HEALTH_EVALUATE',
        resource: 'EVALUATION',
        details: '执行批量健康评估，数据ID: 124-130',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 40 * 60 * 1000).toISOString()
      },
      
      // 参数管理操作
      {
        id: 9,
        user_id: '1',
        username: 'admin',
        action: 'UPDATE_PARAMETER',
        resource: 'PARAMETER_MANAGEMENT',
        details: '更新系统参数: 数据保留天数',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 45 * 60 * 1000).toISOString()
      },
      {
        id: 10,
        user_id: '1',
        username: 'admin',
        action: 'CREATE_PARAMETER',
        resource: 'PARAMETER_MANAGEMENT',
        details: '创建新参数: 模型置信度阈值',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 50 * 60 * 1000).toISOString()
      },
      
      // 系统错误日志
      {
        id: 11,
        user_id: '1',
        username: 'admin',
        action: 'SYSTEM_ERROR',
        resource: 'SYSTEM',
        details: '数据库连接超时，已自动重连',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 55 * 60 * 1000).toISOString()
      },
      {
        id: 12,
        user_id: '2',
        username: 'user',
        action: 'UPLOAD_ERROR',
        resource: 'DATA_MANAGEMENT',
        details: '文件上传失败: 文件格式不支持',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 60 * 60 * 1000).toISOString()
      },
      
      // 历史日志（更早的时间）
      {
        id: 13,
        user_id: '1',
        username: 'admin',
        action: 'LOGOUT',
        resource: 'AUTH',
        details: '管理员退出系统',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 14,
        user_id: '2',
        username: 'user',
        action: 'HEALTH_EVALUATE',
        resource: 'EVALUATION',
        details: '执行健康评估，数据ID: 100',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 3 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 15,
        user_id: '1',
        username: 'admin',
        action: 'BACKUP_DATA',
        resource: 'DATA_MANAGEMENT',
        details: '执行数据备份操作',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 16,
        user_id: '1',
        username: 'admin',
        action: 'UPDATE_MODEL',
        resource: 'MODEL_MANAGEMENT',
        details: '更新AI评估模型版本',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 5 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 17,
        user_id: '2',
        username: 'user',
        action: 'VIEW_RESULTS',
        resource: 'RESULT_MANAGEMENT',
        details: '查看评估结果详情',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 18,
        user_id: '1',
        username: 'admin',
        action: 'EXPORT_LOGS',
        resource: 'LOG_MANAGEMENT',
        details: '导出系统日志',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 7 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 19,
        user_id: '2',
        username: 'user',
        action: 'UPLOAD_DATA',
        resource: 'DATA_MANAGEMENT',
        details: '上传数据文件: stress_test_data.xlsx',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        created_at: new Date(now.getTime() - 8 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 20,
        user_id: '1',
        username: 'admin',
        action: 'SYSTEM_STARTUP',
        resource: 'SYSTEM',
        details: '系统启动完成',
        ip_address: '192.168.1.100',
        user_agent: 'System',
        created_at: new Date(now.getTime() - 12 * 60 * 60 * 1000).toISOString()
      }
    ];
    LocalStorageManager.set(STORAGE_KEYS.LOGS, demoLogs);
  }
  
  // 标记演示数据已初始化
  LocalStorageManager.set(STORAGE_KEYS.DEMO_INITIALIZED, true);
};

// 强制重新初始化演示数据
export const forceInitializeDemoData = () => {
  // 清除初始化标记
  LocalStorageManager.remove(STORAGE_KEYS.DEMO_INITIALIZED);
  // 重新初始化
  initializeDemoData();
};

// 数据操作辅助函数
export const DataOperations = {
  // 获取下一个ID
  getNextId: (items: any[]): number => {
    return items.length > 0 ? Math.max(...items.map(item => item.id)) + 1 : 1;
  },

  // 添加日志
  addLog: (action: string, resource: string, details: string, username: string, userId: string, ipAddress?: string, userAgent?: string) => {
    const logs = LocalStorageManager.get<LogItem[]>(STORAGE_KEYS.LOGS, []);
    const newLog: LogItem = {
      id: DataOperations.getNextId(logs),
      user_id: userId,
      username,
      action,
      resource,
      details,
      ip_address: ipAddress || '127.0.0.1',
      user_agent: userAgent || 'Unknown',
      created_at: new Date().toISOString()
    };
    logs.push(newLog);
    LocalStorageManager.set(STORAGE_KEYS.LOGS, logs);
  },

  // 更新用户最后登录时间
  updateUserLastLogin: (username: string) => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    const userIndex = users.findIndex(user => user.username === username);
    if (userIndex !== -1) {
      users[userIndex].last_login = new Date().toISOString();
      LocalStorageManager.set(STORAGE_KEYS.USERS, users);
    }
  }
};

// 用户管理API函数
export const UserAPI = {
  // 获取用户列表
  getUsers: (params?: { search?: string }): User[] => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    if (params?.search) {
      const searchTerm = params.search.toLowerCase();
      return users.filter(user => 
        user.username.toLowerCase().includes(searchTerm) ||
        user.role.toLowerCase().includes(searchTerm)
      );
    }
    return users;
  },

  // 根据ID获取用户
  getUserById: (id: number): User | null => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    return users.find(user => user.id === id) || null;
  },

  // 根据用户名获取用户
  getUserByUsername: (username: string): User | null => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    return users.find(user => user.username === username) || null;
  },

  // 创建用户
  createUser: (userData: Omit<User, 'id' | 'created_at'>): User => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    const newUser: User = {
      ...userData,
      id: DataOperations.getNextId(users),
      created_at: new Date().toISOString()
    };
    users.push(newUser);
    LocalStorageManager.set(STORAGE_KEYS.USERS, users);
    
    // 添加操作日志
    DataOperations.addLog('CREATE_USER', 'USER_MANAGEMENT', `创建用户: ${newUser.username}`, 'admin', '1');
    
    return newUser;
  },

  // 更新用户
  updateUser: (id: number, userData: Partial<Omit<User, 'id' | 'created_at'>>): User | null => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    const userIndex = users.findIndex(user => user.id === id);
    if (userIndex === -1) return null;

    const oldUser = users[userIndex];
    const updatedUser = { ...oldUser, ...userData };
    users[userIndex] = updatedUser;
    LocalStorageManager.set(STORAGE_KEYS.USERS, users);
    
    // 添加操作日志
    DataOperations.addLog('UPDATE_USER', 'USER_MANAGEMENT', `更新用户: ${updatedUser.username}`, 'admin', '1');
    
    return updatedUser;
  },

  // 删除用户
  deleteUser: (id: number): boolean => {
    const users = LocalStorageManager.get<User[]>(STORAGE_KEYS.USERS, []);
    const userIndex = users.findIndex(user => user.id === id);
    if (userIndex === -1) return false;

    const deletedUser = users[userIndex];
    users.splice(userIndex, 1);
    LocalStorageManager.set(STORAGE_KEYS.USERS, users);
    
    // 添加操作日志
    DataOperations.addLog('DELETE_USER', 'USER_MANAGEMENT', `删除用户: ${deletedUser.username}`, 'admin', '1');
    
    return true;
  }
};
