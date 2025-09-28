/**
 * 模型验证工具类
 * 用于验证模型数据的格式和有效性
 */

import { ModelFormData } from './model-storage';

/**
 * 模型表单数据验证
 */
export const validateModel = (model: ModelFormData): string[] => {
  const errors: string[] = [];
  
  // 模型类型验证
  if (model.model_type === undefined || model.model_type === null) {
    errors.push('请选择模型类型');
  } else if (![0, 1, 2, 3].includes(model.model_type)) {
    errors.push('模型类型无效');
  }
  
  // 模型名称验证
  if (!model.model_name || !model.model_name.trim()) {
    errors.push('请输入模型名称');
  } else if (model.model_name.trim().length < 2) {
    errors.push('模型名称至少需要2个字符');
  } else if (model.model_name.trim().length > 50) {
    errors.push('模型名称不能超过50个字符');
  }
  
  // 文件名验证
  if (!model.file_name || !model.file_name.trim()) {
    errors.push('请输入文件名');
  } else {
    const fileName = model.file_name.trim();
    
    // 检查文件扩展名
    const validExtensions = ['.pkl', '.joblib', '.h5', '.pt', '.pth', '.onnx'];
    const hasValidExtension = validExtensions.some(ext => 
      fileName.toLowerCase().endsWith(ext)
    );
    
    if (!hasValidExtension) {
      errors.push('文件必须是模型文件格式（.pkl, .joblib, .h5, .pt, .pth, .onnx）');
    }
    
    // 检查文件名格式
    if (fileName.length < 3) {
      errors.push('文件名至少需要3个字符');
    } else if (fileName.length > 100) {
      errors.push('文件名不能超过100个字符');
    }
    
    // 检查特殊字符
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(fileName)) {
      errors.push('文件名不能包含特殊字符：< > : " / \\ | ? *');
    }
  }
  
  // 文件大小验证
  if (model.file_size === undefined || model.file_size === null) {
    errors.push('文件大小不能为空');
  } else if (model.file_size <= 0) {
    errors.push('文件大小必须大于0');
  } else if (model.file_size > 1024 * 1024 * 1024) { // 1GB
    errors.push('文件大小不能超过1GB');
  }
  
  // 描述验证（可选）
  if (model.description && model.description.trim().length > 500) {
    errors.push('描述不能超过500个字符');
  }
  
  return errors;
};

/**
 * 验证模型名称是否唯一
 */
export const validateModelName = (modelName: string, excludeId?: number): string[] => {
  const errors: string[] = [];
  
  if (!modelName || !modelName.trim()) {
    errors.push('模型名称不能为空');
    return errors;
  }
  
  // 这里可以添加检查数据库中是否已存在相同名称的逻辑
  // 在纯前端模式下，我们检查localStorage中的模型名称
  try {
    const existingModels = JSON.parse(localStorage.getItem('ai_models') || '[]');
    const duplicateModel = existingModels.find((model: any) => 
      model.model_path.toLowerCase() === modelName.trim().toLowerCase() &&
      model.id !== excludeId
    );
    
    if (duplicateModel) {
      errors.push('模型名称已存在，请使用其他名称');
    }
  } catch (error) {
    console.error('验证模型名称时出错:', error);
  }
  
  return errors;
};

/**
 * 验证文件上传
 */
export const validateFileUpload = (file: File): string[] => {
  const errors: string[] = [];
  
  if (!file) {
    errors.push('请选择要上传的文件');
    return errors;
  }
  
  // 检查文件类型
  const validExtensions = ['.pkl', '.joblib', '.h5', '.pt', '.pth', '.onnx'];
  const fileName = file.name.toLowerCase();
  const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
  
  if (!hasValidExtension) {
    errors.push('只支持以下模型文件格式：.pkl, .joblib, .h5, .pt, .pth, .onnx');
  }
  
  // 检查文件大小
  const maxSize = 1024 * 1024 * 1024; // 1GB
  if (file.size > maxSize) {
    errors.push('文件大小不能超过1GB');
  }
  
  if (file.size === 0) {
    errors.push('文件不能为空');
  }
  
  // 检查文件名
  if (file.name.length < 3) {
    errors.push('文件名至少需要3个字符');
  } else if (file.name.length > 100) {
    errors.push('文件名不能超过100个字符');
  }
  
  // 检查特殊字符
  const invalidChars = /[<>:"/\\|?*]/;
  if (invalidChars.test(file.name)) {
    errors.push('文件名不能包含特殊字符：< > : " / \\ | ? *');
  }
  
  return errors;
};

/**
 * 验证模型类型
 */
export const validateModelType = (modelType: number): string[] => {
  const errors: string[] = [];
  
  if (modelType === undefined || modelType === null) {
    errors.push('请选择模型类型');
  } else if (![0, 1, 2, 3].includes(modelType)) {
    errors.push('模型类型无效，请选择：普通应激模型、抑郁评估模型、焦虑评估模型或社交孤立评估模型');
  }
  
  return errors;
};

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * 获取模型类型名称
 */
export const getModelTypeName = (modelType: number): string => {
  const modelTypes = {
    0: "普通应激模型",
    1: "抑郁评估模型", 
    2: "焦虑评估模型",
    3: "社交孤立评估模型"
  };
  return modelTypes[modelType as keyof typeof modelTypes] || "未知模型";
};

/**
 * 获取所有模型类型选项
 */
export const getModelTypeOptions = () => {
  return [
    { value: 0, label: "普通应激模型" },
    { value: 1, label: "抑郁评估模型" },
    { value: 2, label: "焦虑评估模型" },
    { value: 3, label: "社交孤立评估模型" }
  ];
};

/**
 * 验证搜索关键词
 */
export const validateSearchTerm = (searchTerm: string): string[] => {
  const errors: string[] = [];
  
  if (searchTerm && searchTerm.trim().length > 100) {
    errors.push('搜索关键词不能超过100个字符');
  }
  
  // 检查特殊字符
  const dangerousChars = /[<>:"/\\|?*]/;
  if (searchTerm && dangerousChars.test(searchTerm)) {
    errors.push('搜索关键词不能包含特殊字符');
  }
  
  return errors;
};

/**
 * 清理文件名
 */
export const sanitizeFileName = (fileName: string): string => {
  // 移除或替换危险字符
  return fileName
    .replace(/[<>:"/\\|?*]/g, '_')
    .replace(/\s+/g, '_')
    .replace(/_{2,}/g, '_')
    .trim();
};

/**
 * 验证模型ID
 */
export const validateModelId = (id: number): string[] => {
  const errors: string[] = [];
  
  if (!id || id <= 0) {
    errors.push('模型ID无效');
  }
  
  if (!Number.isInteger(id)) {
    errors.push('模型ID必须是整数');
  }
  
  return errors;
};
