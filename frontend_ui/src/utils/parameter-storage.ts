import { Parameter } from '../types';

/**
 * 参数存储工具类
 * 专门处理localStorage操作，用于纯前端参数管理
 */
export class ParameterStorage {
  private static readonly STORAGE_KEY = 'system_parameters';
  
  /**
   * 获取所有参数
   */
  static getParameters(): Parameter[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('获取参数失败:', error);
      return [];
    }
  }
  
  /**
   * 保存参数列表
   */
  static saveParameters(parameters: Parameter[]): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(parameters));
    } catch (error) {
      console.error('保存参数失败:', error);
      throw new Error('保存参数失败');
    }
  }
  
  /**
   * 清空所有参数
   */
  static clearParameters(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.error('清空参数失败:', error);
    }
  }
  
  /**
   * 导出参数为JSON字符串
   */
  static exportParameters(): string {
    try {
      const parameters = this.getParameters();
      return JSON.stringify(parameters, null, 2);
    } catch (error) {
      console.error('导出参数失败:', error);
      throw new Error('导出参数失败');
    }
  }
  
  /**
   * 从JSON字符串导入参数
   */
  static importParameters(jsonData: string): boolean {
    try {
      const parameters = JSON.parse(jsonData);
      if (Array.isArray(parameters)) {
        this.saveParameters(parameters);
        return true;
      } else {
        throw new Error('参数格式不正确');
      }
    } catch (error) {
      console.error('导入参数失败:', error);
      return false;
    }
  }
  
  /**
   * 获取默认参数数据
   */
  static getDefaultParameters(): Parameter[] {
    return [
      {
        id: 1,
        param_name: 'eeg_sampling_frequency',
        param_value: '1000',
        param_type: 'number',
        description: '脑电数据采样频率(Hz)',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        param_name: 'electrode_count',
        param_value: '64',
        param_type: 'number',
        description: '电极数量',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        param_name: 'stress_threshold',
        param_value: '50',
        param_type: 'number',
        description: '压力评估阈值',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 4,
        param_name: 'depression_threshold',
        param_value: '50',
        param_type: 'number',
        description: '抑郁评估阈值',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 5,
        param_name: 'anxiety_threshold',
        param_value: '50',
        param_type: 'number',
        description: '焦虑评估阈值',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 6,
        param_name: 'social_isolation_threshold',
        param_value: '50',
        param_type: 'number',
        description: '社交孤立评估阈值',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 7,
        param_name: 'model_path',
        param_value: '/models/health_assessment',
        param_type: 'string',
        description: 'AI模型存储路径',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 8,
        param_name: 'backup_enabled',
        param_value: 'true',
        param_type: 'boolean',
        description: '是否启用自动备份',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];
  }
  
  /**
   * 重置为默认参数
   */
  static resetToDefault(): void {
    try {
      const defaultParams = this.getDefaultParameters();
      this.saveParameters(defaultParams);
    } catch (error) {
      console.error('重置参数失败:', error);
      throw new Error('重置参数失败');
    }
  }
  
  /**
   * 检查localStorage是否可用
   */
  static isStorageAvailable(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (error) {
      return false;
    }
  }
}
