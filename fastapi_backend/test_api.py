#!/usr/bin/env python3
"""
急进高原新兵心理应激多模态神经生理监测预警系统API测试脚本
测试所有API接口的功能和可用性
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def get_auth_headers(self) -> Dict[str, str]:
        """获取带认证的请求头"""
        headers = self.headers.copy()
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
        
    def make_request(self, method: str, endpoint: str, data: Any = None, 
                    auth_required: bool = False, files: Any = None) -> tuple:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_auth_headers() if auth_required else self.headers
        
        try:
            if files:
                # 文件上传不需要Content-Type: application/json
                headers = {k: v for k, v in headers.items() if k != "Content-Type"}
                
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, headers=headers, data=data, files=files)
                else:
                    response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                return False, f"不支持的HTTP方法: {method}"
                
            return True, response
        except Exception as e:
            return False, f"请求异常: {str(e)}"
    
    def test_basic_endpoints(self):
        """测试基础端点"""
        print("\n=== 基础端点测试 ===")
        
        # 测试根路径
        success, result = self.make_request("GET", "/")
        if success and result.status_code == 200:
            data = result.json()
            self.log_test("根路径 (/)", True, f"返回: {data.get('message', '')}")
        else:
            self.log_test("根路径 (/)", False, f"状态码: {result.status_code if success else 'N/A'}")
            
        # 测试健康检查
        success, result = self.make_request("GET", "/health")
        if success and result.status_code == 200:
            data = result.json()
            self.log_test("健康检查 (/health)", True, f"状态: {data.get('status', '')}")
        else:
            self.log_test("健康检查 (/health)", False, f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_authentication(self):
        """测试认证相关接口"""
        print("\n=== 认证接口测试 ===")
        
        # 测试登录接口 (JSON格式)
        login_data = {"username": "admin", "password": "admin123"}
        success, result = self.make_request("POST", "/api/login", login_data)
        if success and result.status_code == 200:
            data = result.json()
            self.token = data.get("access_token")
            self.log_test("用户登录 (/api/login)", True, f"用户类型: {data.get('user_type', '')}")
        else:
            self.log_test("用户登录 (/api/login)", False, f"状态码: {result.status_code if success else 'N/A'}")
            
        # 测试Token接口 (OAuth2格式)
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_data = "username=admin&password=admin123"
        try:
            response = self.session.post(f"{self.base_url}/api/token", 
                                       headers=token_headers, data=token_data)
            if response.status_code == 200:
                self.log_test("Token获取 (/api/token)", True, "OAuth2格式登录成功")
            else:
                self.log_test("Token获取 (/api/token)", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("Token获取 (/api/token)", False, f"异常: {str(e)}")
    
    def test_user_management(self):
        """测试用户管理接口"""
        print("\n=== 用户管理接口测试 ===")
        
        if not self.token:
            self.log_test("用户管理测试", False, "缺少认证token")
            return
            
        # 获取当前用户信息
        success, result = self.make_request("GET", "/api/users/me", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            self.log_test("获取当前用户 (/api/users/me)", True, f"用户: {data.get('username', '')}")
        else:
            self.log_test("获取当前用户 (/api/users/me)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
        
        # 获取用户列表
        success, result = self.make_request("GET", "/api/users/", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            self.log_test("获取用户列表 (/api/users/)", True, f"用户数量: {count}")
        else:
            self.log_test("获取用户列表 (/api/users/)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_roles_management(self):
        """测试角色管理接口"""
        print("\n=== 角色管理接口测试 ===")
        
        if not self.token:
            self.log_test("角色管理测试", False, "缺少认证token")
            return
            
        # 获取角色列表
        success, result = self.make_request("GET", "/api/roles/", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            self.log_test("获取角色列表 (/api/roles/)", True, f"角色数量: {count}")
        else:
            self.log_test("获取角色列表 (/api/roles/)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_data_management(self):
        """测试数据管理接口"""
        print("\n=== 数据管理接口测试 ===")
        
        if not self.token:
            self.log_test("数据管理测试", False, "缺少认证token")
            return
            
        # 获取数据列表
        success, result = self.make_request("GET", "/api/data/", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            self.log_test("获取数据列表 (/api/data/)", True, f"数据条数: {count}")
        else:
            self.log_test("获取数据列表 (/api/data/)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_model_management(self):
        """测试模型管理接口"""
        print("\n=== 模型管理接口测试 ===")
        
        if not self.token:
            self.log_test("模型管理测试", False, "缺少认证token")
            return
            
        # 获取模型列表
        success, result = self.make_request("GET", "/api/models/", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            self.log_test("获取模型列表 (/api/models/)", True, f"模型数量: {count}")
        else:
            self.log_test("获取模型列表 (/api/models/)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_results_management(self):
        """测试结果管理接口"""
        print("\n=== 结果管理接口测试 ===")
        
        if not self.token:
            self.log_test("结果管理测试", False, "缺少认证token")
            return
            
        # 获取结果列表
        success, result = self.make_request("GET", "/api/results/", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            self.log_test("获取结果列表 (/api/results/)", True, f"结果数量: {count}")
        else:
            self.log_test("获取结果列表 (/api/results/)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_parameters_management(self):
        """测试参数管理接口"""
        print("\n=== 参数管理接口测试 ===")
        
        if not self.token:
            self.log_test("参数管理测试", False, "缺少认证token")
            return
            
        # 获取参数列表
        success, result = self.make_request("GET", "/api/parameters/", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            self.log_test("获取参数列表 (/api/parameters/)", True, f"参数数量: {count}")
        else:
            self.log_test("获取参数列表 (/api/parameters/)", False, 
                         f"状态码: {result.status_code if success else 'N/A'}")
    
    def test_logs_management(self):
        """测试日志管理接口"""
        print("\n=== 日志管理接口测试 ===")
        
        if not self.token:
            self.log_test("日志管理测试", False, "缺少认证token")
            return
            
        # 获取日志列表
        success, result = self.make_request("GET", "/api/logs/", auth_required=True)
        if success:
            if result.status_code == 200:
                data = result.json()
                count = len(data) if isinstance(data, list) else 1
                self.log_test("获取日志列表 (/api/logs/)", True, f"日志条数: {count}")
            else:
                self.log_test("获取日志列表 (/api/logs/)", False, f"状态码: {result.status_code}")
        else:
            self.log_test("获取日志列表 (/api/logs/)", False, "请求失败")
    
    def test_health_evaluation(self):
        """测试健康评估接口"""
        print("\n=== 健康评估接口测试 ===")
        
        if not self.token:
            self.log_test("健康评估测试", False, "缺少认证token")
            return
            
        # 测试健康评估接口（需要数据ID，暂时用不存在的ID测试接口是否响应）
        eval_data = {"data_id": 999}  # 使用不存在的ID
        success, result = self.make_request("POST", "/api/health/evaluate", eval_data, auth_required=True)
        if success:
            if result.status_code == 404:
                self.log_test("健康评估接口 (/api/health/evaluate)", True, "接口正常响应（数据不存在）")
            elif result.status_code == 422:
                self.log_test("健康评估接口 (/api/health/evaluate)", True, "接口正常响应（参数验证）")
            else:
                self.log_test("健康评估接口 (/api/health/evaluate)", False, f"意外状态码: {result.status_code}")
        else:
            self.log_test("健康评估接口 (/api/health/evaluate)", False, "请求失败")
    
    def generate_summary(self):
        """生成测试总结"""
        print("\n" + "="*50)
        print("🧪 API接口测试总结")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['details']}")
        
        return passed_tests, failed_tests
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始API接口测试...")
        print(f"测试目标: {self.base_url}")
        
        # 按顺序执行测试
        self.test_basic_endpoints()
        self.test_authentication()
        self.test_user_management()
        self.test_roles_management()
        self.test_data_management()
        self.test_model_management()
        self.test_results_management()
        self.test_parameters_management()
        self.test_logs_management()
        self.test_health_evaluation()
        
        # 生成总结
        passed, failed = self.generate_summary()
        
        return failed == 0  # 如果没有失败的测试，返回True

def main():
    """主函数"""
    tester = APITester()
    
    # 运行所有测试
    success = tester.run_all_tests()
    
    # 退出码：0表示成功，1表示有失败
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 