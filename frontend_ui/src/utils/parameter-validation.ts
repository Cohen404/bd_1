/**
 * 参数验证工具类
 * 用于验证参数数据的格式和有效性
 */

export interface ParameterFormData {
  param_name: string;
  param_value: string;
  param_type: string;
  description: string;
}

/**
 * 参数值验证
 */
export const validateParameter = (param: ParameterFormData): string[] => {
  const errors: string[] = [];
  
  // 参数名称验证
  if (!param.param_name.trim()) {
    errors.push('参数名称不能为空');
  } else if (param.param_name.length > 50) {
    errors.push('参数名称长度不能超过50个字符');
  } else if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(param.param_name)) {
    errors.push('参数名称只能包含字母、数字和下划线，且必须以字母或下划线开头');
  }
  
  // 参数值验证
  if (!param.param_value.trim()) {
    errors.push('参数值不能为空');
  } else if (param.param_value.length > 255) {
    errors.push('参数值长度不能超过255个字符');
  }
  
  // 根据参数类型验证值格式
  if (param.param_type === 'number') {
    if (isNaN(Number(param.param_value))) {
      errors.push('数字类型参数值必须是有效数字');
    } else {
      const num = Number(param.param_value);
      if (!isFinite(num)) {
        errors.push('数字类型参数值必须是有限数字');
      }
    }
  }
  
  if (param.param_type === 'boolean') {
    if (!['true', 'false'].includes(param.param_value.toLowerCase())) {
      errors.push('布尔类型参数值必须是true或false');
    }
  }
  
  if (param.param_type === 'json') {
    try {
      JSON.parse(param.param_value);
    } catch (error) {
      errors.push('JSON类型参数值必须是有效的JSON格式');
    }
  }
  
  // 参数类型验证
  const validTypes = ['string', 'number', 'boolean', 'json'];
  if (!validTypes.includes(param.param_type)) {
    errors.push(`参数类型必须是以下之一: ${validTypes.join(', ')}`);
  }
  
  // 描述验证
  if (param.description && param.description.length > 255) {
    errors.push('参数描述长度不能超过255个字符');
  }
  
  return errors;
};

/**
 * 验证参数名称是否重复
 */
export const validateParameterName = (
  paramName: string, 
  paramType: string, 
  existingParams: any[], 
  excludeId?: number
): string[] => {
  const errors: string[] = [];
  
  const duplicate = existingParams.find(param => 
    param.param_name === paramName && 
    param.param_type === paramType && 
    param.id !== excludeId
  );
  
  if (duplicate) {
    errors.push(`参数名"${paramName}"在类型"${paramType}"中已存在`);
  }
  
  return errors;
};

/**
 * 验证IP地址格式
 */
export const validateIPAddress = (ip: string): boolean => {
  const pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!pattern.test(ip)) {
    return false;
  }
  
  const parts = ip.split('.');
  return parts.every(part => {
    const num = parseInt(part, 10);
    return num >= 0 && num <= 255;
  });
};

/**
 * 验证文件路径格式
 */
export const validateFilePath = (path: string): boolean => {
  // 基本的文件路径验证
  const invalidChars = /[<>:"|?*]/;
  return !invalidChars.test(path) && path.length > 0;
};

/**
 * 验证数值范围
 */
export const validateNumberRange = (
  value: number, 
  min?: number, 
  max?: number
): string[] => {
  const errors: string[] = [];
  
  if (min !== undefined && value < min) {
    errors.push(`数值不能小于${min}`);
  }
  
  if (max !== undefined && value > max) {
    errors.push(`数值不能大于${max}`);
  }
  
  return errors;
};

/**
 * 验证JSON格式
 */
export const validateJSON = (jsonString: string): { valid: boolean; error?: string } => {
  try {
    JSON.parse(jsonString);
    return { valid: true };
  } catch (error) {
    return { 
      valid: false, 
      error: error instanceof Error ? error.message : '无效的JSON格式' 
    };
  }
};

/**
 * 验证参数值的格式
 */
export const validateParameterValue = (value: string, type: string): string[] => {
  const errors: string[] = [];
  
  switch (type) {
    case 'number':
      if (isNaN(Number(value))) {
        errors.push('必须是有效数字');
      }
      break;
      
    case 'boolean':
      if (!['true', 'false'].includes(value.toLowerCase())) {
        errors.push('必须是true或false');
      }
      break;
      
    case 'json':
      const jsonValidation = validateJSON(value);
      if (!jsonValidation.valid) {
        errors.push(`JSON格式错误: ${jsonValidation.error}`);
      }
      break;
      
    case 'string':
      // 字符串类型基本不需要额外验证
      break;
      
    default:
      errors.push(`不支持的类型: ${type}`);
  }
  
  return errors;
};
