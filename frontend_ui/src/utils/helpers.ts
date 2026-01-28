import { ScoreLevel, ChartData } from '@/types';

// 格式化日期时间
export const formatDateTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch (error) {
    return dateString;
  }
};

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  } catch (error) {
    return dateString;
  }
};

export const formatTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch (error) {
    return dateString;
  }
};

// 相对时间格式化
export const formatRelativeTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
      return `${days}天前`;
    } else if (hours > 0) {
      return `${hours}小时前`;
    } else if (minutes > 0) {
      return `${minutes}分钟前`;
    } else {
      return '刚刚';
    }
  } catch (error) {
    return dateString;
  }
};

// 文件大小格式化
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// 健康评估分数等级判断
export const getScoreLevel = (score: number): ScoreLevel => {
  if (score < 30) return 'low';
  if (score < 70) return 'medium';
  return 'high';
};

// 获取分数等级颜色
export const getScoreLevelColor = (level: ScoreLevel): string => {
  const colors = {
    low: 'text-green-600',
    medium: 'text-yellow-600',
    high: 'text-red-600',
  };
  return colors[level];
};

export const getScoreLevelBgColor = (level: ScoreLevel): string => {
  const colors = {
    low: 'bg-green-50 border-green-200',
    medium: 'bg-yellow-50 border-yellow-200',
    high: 'bg-red-50 border-red-200',
  };
  return colors[level];
};

// 获取分数等级描述
export const getScoreLevelText = (level: ScoreLevel): string => {
  const texts = {
    low: '正常',
    medium: '中等',
    high: '严重',
  };
  return texts[level];
};

// 健康评估维度名称映射
export const getScoreTypeName = (type: string): string => {
  const names: { [key: string]: string } = {
    stress_score: '应激评分',
    depression_score: '抑郁评分',
    anxiety_score: '焦虑评分',
  };
  return names[type] || type;
};

// 将健康评估结果转换为图表数据
export const transformHealthScoresToChartData = (scores: {
  stress_score: number;
  depression_score: number;
  anxiety_score: number;
}): ChartData[] => {
  return [
    {
      name: '应激',
      value: scores.stress_score,
      level: getScoreLevel(scores.stress_score),
    },
    {
      name: '抑郁',
      value: scores.depression_score,
      level: getScoreLevel(scores.depression_score),
    },
    {
      name: '焦虑',
      value: scores.anxiety_score,
      level: getScoreLevel(scores.anxiety_score),
    },
  ];
};

// 下载文件
export const downloadFile = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// 复制到剪贴板
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('复制失败:', error);
    return false;
  }
};

// 防抖函数
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: ReturnType<typeof setTimeout>;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// 节流函数
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let lastTime = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastTime >= wait) {
      lastTime = now;
      func(...args);
    }
  };
};

// 生成随机ID
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

// 验证邮箱格式
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// 验证手机号格式
export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

// 密码强度检查
export const checkPasswordStrength = (password: string): {
  score: number;
  message: string;
} => {
  let score = 0;
  const messages = [];
  
  if (password.length >= 8) {
    score += 1;
  } else {
    messages.push('至少8个字符');
  }
  
  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    messages.push('包含小写字母');
  }
  
  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    messages.push('包含大写字母');
  }
  
  if (/\d/.test(password)) {
    score += 1;
  } else {
    messages.push('包含数字');
  }
  
  if (/[^a-zA-Z\d]/.test(password)) {
    score += 1;
  } else {
    messages.push('包含特殊字符');
  }
  
  const strengthMap = {
    0: '很弱',
    1: '弱',
    2: '一般',
    3: '较强',
    4: '强',
    5: '很强',
  };
  
  return {
    score,
    message: score >= 3 ? '密码强度良好' : `需要${messages.join('、')}`,
  };
};

// 深度克隆对象
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
  if (obj instanceof Array) return obj.map(deepClone) as unknown as T;
  if (obj instanceof Object) {
    const clonedObj: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
  return obj;
};

// 对象比较
export const isEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  if (obj1 == null || obj2 == null) return false;
  if (typeof obj1 !== typeof obj2) return false;
  
  if (typeof obj1 === 'object') {
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    
    if (keys1.length !== keys2.length) return false;
    
    for (const key of keys1) {
      if (!keys2.includes(key) || !isEqual(obj1[key], obj2[key])) {
        return false;
      }
    }
    return true;
  }
  
  return false;
};

// 数组去重
export const uniqueArray = <T>(array: T[], key?: keyof T): T[] => {
  if (!key) {
    return Array.from(new Set(array));
  }
  
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
}; 