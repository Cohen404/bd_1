import { Model } from '../types';

/**
 * 模型存储工具类
 * 专门处理localStorage操作，用于纯前端模型管理
 */

export interface ModelFormData {
  model_type: number;
  model_name: string;
  description: string;
  file_name: string;
  file_size: number;
}

export interface ModelStatus {
  total_models: number;
  available_models: number;
  missing_models: number;
  model_details: ModelDetail[];
}

export interface ModelDetail {
  id: number;
  model_type: number;
  model_type_name: string;
  model_path: string;
  create_time: string;
  file_exists: boolean;
  file_size_mb: number;
  status: string;
}

export interface ModelVersion {
  id: number | null;
  version: string;
  create_time: string;
  file_path: string;
  file_exists: boolean;
  file_size_mb: number;
  is_current: boolean;
}

export interface ModelPerformance {
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

export class ModelStorage {
  private static readonly STORAGE_KEY = 'ai_models';
  private static readonly STATUS_KEY = 'model_status';
  private static readonly VERSIONS_KEY = 'model_versions';
  private static readonly PERFORMANCE_KEY = 'model_performance';
  
  /**
   * 获取所有模型
   */
  static getAllModels(): Model[] {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('获取模型列表失败:', error);
      return [];
    }
  }

  /**
   * 根据ID获取模型
   */
  static getModelById(id: number): Model | null {
    const models = this.getAllModels();
    return models.find(model => model.id === id) || null;
  }

  /**
   * 添加新模型
   */
  static addModel(modelData: ModelFormData): Model {
    const models = this.getAllModels();
    const newModel: Model = {
      id: this.generateId(),
      model_type: modelData.model_type,
      model_path: modelData.file_name,
      create_time: new Date().toISOString()
    };
    
    models.push(newModel);
    this.saveModels(models);
    return newModel;
  }

  /**
   * 更新模型
   */
  static updateModel(id: number, updates: Partial<Model>): Model | null {
    const models = this.getAllModels();
    const index = models.findIndex(model => model.id === id);
    
    if (index === -1) return null;
    
    models[index] = { ...models[index], ...updates };
    this.saveModels(models);
    return models[index];
  }

  /**
   * 删除模型
   */
  static deleteModel(id: number): boolean {
    const models = this.getAllModels();
    const filteredModels = models.filter(model => model.id !== id);
    
    if (filteredModels.length === models.length) return false;
    
    this.saveModels(filteredModels);
    return true;
  }

  /**
   * 根据类型筛选模型
   */
  static getModelsByType(modelType: number): Model[] {
    const models = this.getAllModels();
    return models.filter(model => model.model_type === modelType);
  }

  /**
   * 搜索模型
   */
  static searchModels(searchTerm: string): Model[] {
    const models = this.getAllModels();
    if (!searchTerm.trim()) return models;
    
    const term = searchTerm.toLowerCase();
    return models.filter(model => 
      model.model_path.toLowerCase().includes(term) ||
      this.getModelTypeName(model.model_type).toLowerCase().includes(term)
    );
  }

  /**
   * 获取模型状态
   */
  static getModelStatus(): ModelStatus {
    try {
      const data = localStorage.getItem(this.STATUS_KEY);
      if (data) {
        return JSON.parse(data);
      }
      
      // 如果没有存储的状态，生成默认状态
      const models = this.getAllModels();
      const modelDetails: ModelDetail[] = models.map(model => ({
        id: model.id,
        model_type: model.model_type,
        model_type_name: this.getModelTypeName(model.model_type),
        model_path: model.model_path,
        create_time: model.create_time,
        file_exists: true, // 纯前端模式下假设文件存在
        file_size_mb: Math.random() * 100 + 10, // 模拟文件大小
        status: '可用'
      }));
      
      const status: ModelStatus = {
        total_models: models.length,
        available_models: models.length,
        missing_models: 0,
        model_details: modelDetails
      };
      
      this.saveModelStatus(status);
      return status;
    } catch (error) {
      console.error('获取模型状态失败:', error);
      return {
        total_models: 0,
        available_models: 0,
        missing_models: 0,
        model_details: []
      };
    }
  }

  /**
   * 保存模型状态
   */
  static saveModelStatus(status: ModelStatus): void {
    try {
      localStorage.setItem(this.STATUS_KEY, JSON.stringify(status));
    } catch (error) {
      console.error('保存模型状态失败:', error);
    }
  }

  /**
   * 获取模型版本
   */
  static getModelVersions(modelType: number): ModelVersion[] {
    try {
      const data = localStorage.getItem(this.VERSIONS_KEY);
      if (data) {
        const allVersions = JSON.parse(data);
        return allVersions[modelType] || [];
      }
      return [];
    } catch (error) {
      console.error('获取模型版本失败:', error);
      return [];
    }
  }

  /**
   * 保存模型版本
   */
  static saveModelVersions(modelType: number, versions: ModelVersion[]): void {
    try {
      const data = localStorage.getItem(this.VERSIONS_KEY);
      const allVersions = data ? JSON.parse(data) : {};
      allVersions[modelType] = versions;
      localStorage.setItem(this.VERSIONS_KEY, JSON.stringify(allVersions));
    } catch (error) {
      console.error('保存模型版本失败:', error);
    }
  }

  /**
   * 获取模型性能数据
   */
  static getModelPerformance(): ModelPerformance[] {
    try {
      const data = localStorage.getItem(this.PERFORMANCE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('获取模型性能数据失败:', error);
      return [];
    }
  }

  /**
   * 保存模型性能数据
   */
  static saveModelPerformance(performance: ModelPerformance[]): void {
    try {
      localStorage.setItem(this.PERFORMANCE_KEY, JSON.stringify(performance));
    } catch (error) {
      console.error('保存模型性能数据失败:', error);
    }
  }

  /**
   * 获取模型类型名称
   */
  static getModelTypeName(modelType: number): string {
    const modelTypes = {
      0: "普通应激模型",
      1: "抑郁评估模型", 
      2: "焦虑评估模型",
      3: "社交孤立评估模型"
    };
    return modelTypes[modelType as keyof typeof modelTypes] || "未知模型";
  }

  /**
   * 生成唯一ID
   */
  private static generateId(): number {
    const models = this.getAllModels();
    const maxId = models.length > 0 ? Math.max(...models.map(m => m.id)) : 0;
    return maxId + 1;
  }

  /**
   * 保存模型列表
   */
  private static saveModels(models: Model[]): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(models));
    } catch (error) {
      console.error('保存模型列表失败:', error);
    }
  }

  /**
   * 清空所有模型数据
   */
  static clearAll(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      localStorage.removeItem(this.STATUS_KEY);
      localStorage.removeItem(this.VERSIONS_KEY);
      localStorage.removeItem(this.PERFORMANCE_KEY);
    } catch (error) {
      console.error('清空模型数据失败:', error);
    }
  }

  /**
   * 初始化示例数据
   */
  static initializeSampleData(): void {
    const existingModels = this.getAllModels();
    if (existingModels.length > 0) return;

    const sampleModels: Model[] = [
      {
        id: 1,
        model_type: 0,
        model_path: "stress_model_v1.pkl",
        create_time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        model_type: 1,
        model_path: "depression_model_v2.pkl",
        create_time: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 3,
        model_type: 2,
        model_path: "anxiety_model_v1.pkl",
        create_time: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 4,
        model_type: 3,
        model_path: "isolation_model_v1.pkl",
        create_time: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      }
    ];

    this.saveModels(sampleModels);

    // 初始化性能数据
    const samplePerformance: ModelPerformance[] = sampleModels.map(model => ({
      id: model.id,
      model_type: model.model_type,
      model_type_name: this.getModelTypeName(model.model_type),
      create_time: model.create_time,
      file_exists: true,
      accuracy: {
        training: 0.85 + Math.random() * 0.1,
        validation: 0.80 + Math.random() * 0.1,
        test: 0.78 + Math.random() * 0.1
      },
      loss: {
        training: 0.1 + Math.random() * 0.05,
        validation: 0.15 + Math.random() * 0.05
      },
      training_epochs: 50 + Math.floor(Math.random() * 50),
      model_size_mb: 10 + Math.random() * 90
    }));

    this.saveModelPerformance(samplePerformance);
  }
}
