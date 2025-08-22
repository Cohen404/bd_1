import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';
import Cookies from 'js-cookie';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 已移除认证token
api.interceptors.request.use(
  (config) => {
    // 认证已移除，无需添加token
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    const { response } = error;
    
    if (response?.status === 401) {
      // 认证已移除，401错误直接显示错误信息
      toast.error('请求失败：未授权');
    } else if (response?.status === 403) {
      toast.error('权限不足，无法访问该资源');
    } else if (response?.status === 404) {
      toast.error('请求的资源不存在');
    } else if (response?.status === 422) {
      const detail = response.data?.detail;
      if (Array.isArray(detail)) {
        detail.forEach((err: any) => {
          toast.error(`${err.loc?.join('.')}: ${err.msg}`);
        });
      } else {
        toast.error(detail || '参数验证失败');
      }
    } else if (response?.status >= 500) {
      toast.error('服务器内部错误，请稍后重试');
    } else {
      toast.error(response?.data?.detail || response?.data?.message || '请求失败');
    }
    
    return Promise.reject(error);
  }
);

// API类
class API {
  // 认证相关
  async login(data: { username: string; password: string }) {
    const response = await api.post('/login', data);
    return response.data;
  }

  async getCurrentUser() {
    const response = await api.get('/users/me');
    return response.data;
  }

  // 用户管理
  async getUsers(params?: { page?: number; size?: number; search?: string }) {
    const response = await api.get('/users/', { params });
    return response.data;
  }

  async createUser(data: any) {
    const response = await api.post('/users/', data);
    return response.data;
  }

  async updateUser(userId: string, data: any) {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  }

  async deleteUser(userId: string) {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  }

  async getUserById(userId: string) {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  }

  // 角色管理
  async getRoles(params?: { page?: number; size?: number }) {
    const response = await api.get('/roles/', { params });
    return response.data;
  }

  async createRole(data: any) {
    const response = await api.post('/roles/', data);
    return response.data;
  }

  async updateRole(roleId: number, data: any) {
    const response = await api.put(`/roles/${roleId}`, data);
    return response.data;
  }

  async deleteRole(roleId: number) {
    const response = await api.delete(`/roles/${roleId}`);
    return response.data;
  }

  async getRolePermissions(roleId: number) {
    const response = await api.get(`/roles/${roleId}/permissions`);
    return response.data;
  }

  // 数据管理
  async getData(params?: { page?: number; size?: number; search?: string }) {
    const response = await api.get('/data/', { params });
    return response.data;
  }

  async getTop200Data() {
    const response = await api.get('/data/top-200');
    return response.data;
  }

  async uploadData(formData: FormData) {
    const response = await api.post('/data/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async batchUploadData(formData: FormData) {
    const response = await api.post('/data/batch-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async preprocessData(dataId: number) {
    const response = await api.post(`/data/${dataId}/preprocess`);
    return response.data;
  }

  async batchPreprocessData(data: { data_ids: number[] }) {
    const response = await api.post('/data/batch-preprocess', data);
    return response.data;
  }

  async batchDeleteData(data: { data_ids: number[] }) {
    const response = await api.delete('/data/batch-delete', { data });
    return response.data;
  }

  async deleteData(dataId: number) {
    const response = await api.delete(`/data/${dataId}`);
    return response.data;
  }

  async getDataById(dataId: number) {
    const response = await api.get(`/data/${dataId}`);
    return response.data;
  }

  async getDataImages(dataId: number) {
    const response = await api.get(`/health/images/${dataId}`);
    return response.data;
  }

  // 预处理进度相关
  async getDataProgress(dataId: number) {
    const response = await api.get(`/data/progress/single/${dataId}`);
    return response.data;
  }

  async getBatchProgress(dataIds: number[]) {
    const response = await api.get(`/data/progress?data_ids=${dataIds.join(',')}`);
    return response.data;
  }

  async updateDataStatus(dataId: number, data: { processing_status?: string; feature_status?: string }) {
    const response = await api.put(`/data/status/${dataId}`, data);
    return response.data;
  }

  // 健康评估
  async evaluateHealth(data: { data_id: number }) {
    const response = await api.post('/health/evaluate', data);
    return response.data;
  }

  async batchEvaluateHealth(data: { data_ids: number[] }) {
    const response = await api.post('/health/batch-evaluate', data);
    return response.data;
  }

  async getHealthReport(resultId: number) {
    const response = await api.get(`/health/reports/${resultId}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // 结果管理
  async getResults(params?: { page?: number; size?: number; search?: string }) {
    const response = await api.get('/results/', { params });
    return response.data;
  }

  async getResultById(resultId: number) {
    const response = await api.get(`/results/${resultId}`);
    return response.data;
  }

  async deleteResult(resultId: number) {
    const response = await api.delete(`/results/${resultId}`);
    return response.data;
  }

  async getResultReport(resultId: number) {
    const response = await api.get(`/results/${resultId}/report`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // 模型管理
  async getModels(params?: { page?: number; size?: number }) {
    const response = await api.get('/models/', { params });
    return response.data;
  }

  async uploadModel(formData: FormData) {
    const response = await api.post('/models/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteModel(modelId: number) {
    const response = await api.delete(`/models/${modelId}`);
    return response.data;
  }

  async getModelById(modelId: number) {
    const response = await api.get(`/models/${modelId}`);
    return response.data;
  }

  // 参数管理
  async getParameters(params?: { page?: number; size?: number }) {
    const response = await api.get('/parameters/', { params });
    return response.data;
  }

  async createParameter(data: any) {
    const response = await api.post('/parameters/', data);
    return response.data;
  }

  async updateParameter(paramId: number, data: any) {
    const response = await api.put(`/parameters/${paramId}`, data);
    return response.data;
  }

  async deleteParameter(paramId: number) {
    const response = await api.delete(`/parameters/${paramId}`);
    return response.data;
  }

  // 日志管理
  async getLogs(params?: { page?: number; size?: number; search?: string }) {
    const response = await api.get('/logs/', { params });
    return response.data;
  }

  // 系统健康检查
  async healthCheck() {
    const response = await api.get('/', { baseURL: '/' });
    return response.data;
  }

  // 通用GET请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await api.get(url, config);
    return response.data;
  }

  // 通用POST请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await api.post(url, data, config);
    return response.data;
  }

  // 通用PUT请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await api.put(url, data, config);
    return response.data;
  }

  // 通用DELETE请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await api.delete(url, config);
    return response.data;
  }
}

export const apiClient = new API();
export default api; 