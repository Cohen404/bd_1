#!/usr/bin/env python3
"""
北京健康评估系统API完整测试脚本
测试所有24个API接口的功能和可用性
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class CompleteAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            "users": [],
            "roles": [],
            "data": [],
            "models": [],
            "results": [],
            "parameters": []
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", status_code: int = None):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        status_info = f" [{status_code}]" if status_code else ""
        print(f"{status} {test_name}{status_info}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "status_code": status_code
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
        print("\n=== 1. 基础端点测试 ===")
        
        # 1. GET /
        success, result = self.make_request("GET", "/")
        if success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /", True, f"返回: {data.get('message', '')}", result.status_code)
        else:
            self.log_test("GET /", False, f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
            
        # 2. GET /health
        success, result = self.make_request("GET", "/health")
        if success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /health", True, f"状态: {data.get('status', '')}", result.status_code)
        else:
            self.log_test("GET /health", False, f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
    
    def test_authentication_endpoints(self):
        """测试认证相关接口"""
        print("\n=== 2. 认证接口测试 ===")
        
        # 3. POST /api/login
        login_data = {"username": "admin", "password": "admin123"}
        success, result = self.make_request("POST", "/api/login", login_data)
        if success and result.status_code == 200:
            data = result.json()
            self.token = data.get("access_token")
            self.log_test("POST /api/login", True, f"用户类型: {data.get('user_type', '')}", result.status_code)
        else:
            self.log_test("POST /api/login", False, f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
            
        # 4. POST /api/token (OAuth2格式)
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_data = "username=admin&password=admin123"
        try:
            response = self.session.post(f"{self.base_url}/api/token", 
                                       headers=token_headers, data=token_data)
            if response.status_code == 200:
                self.log_test("POST /api/token", True, "OAuth2格式登录成功", response.status_code)
            else:
                self.log_test("POST /api/token", False, f"状态码: {response.status_code}", response.status_code)
        except Exception as e:
            self.log_test("POST /api/token", False, f"异常: {str(e)}")
    
    def test_user_endpoints(self):
        """测试用户管理接口"""
        print("\n=== 3. 用户管理接口测试 ===")
        
        if not self.token:
            self.log_test("用户管理测试", False, "缺少认证token")
            return
            
        # 5. GET /api/users/me
        success, result = self.make_request("GET", "/api/users/me", auth_required=True)
        if success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /api/users/me", True, f"用户: {data.get('username', '')}", result.status_code)
        else:
            self.log_test("GET /api/users/me", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 6. GET /api/users/
        success, result = self.make_request("GET", "/api/users/", auth_required=True)
        current_user_id = None
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            if isinstance(data, list) and len(data) > 0:
                current_user_id = data[0].get('user_id')
            self.log_test("GET /api/users/", True, f"用户数量: {count}", result.status_code)
        else:
            self.log_test("GET /api/users/", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 7. GET /api/users/{user_id}
        if current_user_id:
            success, result = self.make_request("GET", f"/api/users/{current_user_id}", auth_required=True)
            if success and result.status_code == 200:
                data = result.json()
                self.log_test("GET /api/users/{user_id}", True, 
                             f"获取用户详情: {data.get('username', '')}", result.status_code)
            else:
                self.log_test("GET /api/users/{user_id}", False, 
                             f"状态码: {result.status_code if success else 'N/A'}", 
                             result.status_code if success else None)
        else:
            self.log_test("GET /api/users/{user_id}", False, "无法获取用户ID")
    
    def test_role_endpoints(self):
        """测试角色管理接口"""
        print("\n=== 4. 角色管理接口测试 ===")
        
        if not self.token:
            self.log_test("角色管理测试", False, "缺少认证token")
            return
            
        # 8. GET /api/roles/
        success, result = self.make_request("GET", "/api/roles/", auth_required=True)
        role_id = None
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            if isinstance(data, list) and len(data) > 0:
                role_id = data[0].get('role_id')
            self.log_test("GET /api/roles/", True, f"角色数量: {count}", result.status_code)
        else:
            self.log_test("GET /api/roles/", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 9. GET /api/roles/{role_id}
        if role_id:
            success, result = self.make_request("GET", f"/api/roles/{role_id}", auth_required=True)
            if success and result.status_code == 200:
                data = result.json()
                self.log_test("GET /api/roles/{role_id}", True, 
                             f"角色详情: {data.get('role_name', '')}", result.status_code)
            else:
                self.log_test("GET /api/roles/{role_id}", False, 
                             f"状态码: {result.status_code if success else 'N/A'}", 
                             result.status_code if success else None)
        else:
            self.log_test("GET /api/roles/{role_id}", False, "无法获取角色ID")
            
        # 10. GET /api/roles/{role_id}/permissions
        if role_id:
            success, result = self.make_request("GET", f"/api/roles/{role_id}/permissions", auth_required=True)
            if success and result.status_code == 200:
                data = result.json()
                count = len(data) if isinstance(data, list) else 1
                self.log_test("GET /api/roles/{role_id}/permissions", True, 
                             f"权限数量: {count}", result.status_code)
            else:
                self.log_test("GET /api/roles/{role_id}/permissions", False, 
                             f"状态码: {result.status_code if success else 'N/A'}", 
                             result.status_code if success else None)
        else:
            self.log_test("GET /api/roles/{role_id}/permissions", False, "无法获取角色ID")
            
        # 11. DELETE /api/roles/{role_id}/permissions/{permission_id} (测试不存在的权限)
        if role_id:
            success, result = self.make_request("DELETE", f"/api/roles/{role_id}/permissions/999", auth_required=True)
            if success and result.status_code in [404, 422]:
                self.log_test("DELETE /api/roles/{role_id}/permissions/{permission_id}", True, 
                             "正确返回权限不存在", result.status_code)
            else:
                self.log_test("DELETE /api/roles/{role_id}/permissions/{permission_id}", False, 
                             f"状态码: {result.status_code if success else 'N/A'}", 
                             result.status_code if success else None)
        else:
            self.log_test("DELETE /api/roles/{role_id}/permissions/{permission_id}", False, "无法获取角色ID")
    
    def test_data_endpoints(self):
        """测试数据管理接口"""
        print("\n=== 5. 数据管理接口测试 ===")
        
        if not self.token:
            self.log_test("数据管理测试", False, "缺少认证token")
            return
            
        # 12. GET /api/data/
        success, result = self.make_request("GET", "/api/data/", auth_required=True)
        data_id = None
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            if isinstance(data, list) and len(data) > 0:
                data_id = data[0].get('id')
            self.log_test("GET /api/data/", True, f"数据条数: {count}", result.status_code)
        else:
            self.log_test("GET /api/data/", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 13. GET /api/data/{data_id} (测试不存在的数据)
        success, result = self.make_request("GET", "/api/data/999", auth_required=True)
        if success and result.status_code == 404:
            self.log_test("GET /api/data/{data_id}", True, "正确返回数据不存在", result.status_code)
        elif success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /api/data/{data_id}", True, f"获取数据详情", result.status_code)
        else:
            self.log_test("GET /api/data/{data_id}", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
    
    def test_model_endpoints(self):
        """测试模型管理接口"""
        print("\n=== 6. 模型管理接口测试 ===")
        
        if not self.token:
            self.log_test("模型管理测试", False, "缺少认证token")
            return
            
        # 14. GET /api/models/
        success, result = self.make_request("GET", "/api/models/", auth_required=True)
        model_id = None
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            if isinstance(data, list) and len(data) > 0:
                model_id = data[0].get('id')
            self.log_test("GET /api/models/", True, f"模型数量: {count}", result.status_code)
        else:
            self.log_test("GET /api/models/", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 15. GET /api/models/{model_id} (测试不存在的模型)
        success, result = self.make_request("GET", "/api/models/999", auth_required=True)
        if success and result.status_code == 404:
            self.log_test("GET /api/models/{model_id}", True, "正确返回模型不存在", result.status_code)
        elif success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /api/models/{model_id}", True, "获取模型详情", result.status_code)
        else:
            self.log_test("GET /api/models/{model_id}", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
    
    def test_result_endpoints(self):
        """测试结果管理接口"""
        print("\n=== 7. 结果管理接口测试 ===")
        
        if not self.token:
            self.log_test("结果管理测试", False, "缺少认证token")
            return
            
        # 16. GET /api/results/
        success, result = self.make_request("GET", "/api/results/", auth_required=True)
        result_id = None
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            if isinstance(data, list) and len(data) > 0:
                result_id = data[0].get('id')
            self.log_test("GET /api/results/", True, f"结果数量: {count}", result.status_code)
        else:
            self.log_test("GET /api/results/", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 17. GET /api/results/{result_id} (测试不存在的结果)
        success, result = self.make_request("GET", "/api/results/999", auth_required=True)
        if success and result.status_code == 404:
            self.log_test("GET /api/results/{result_id}", True, "正确返回结果不存在", result.status_code)
        elif success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /api/results/{result_id}", True, "获取结果详情", result.status_code)
        else:
            self.log_test("GET /api/results/{result_id}", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
            
        # 18. GET /api/results/{result_id}/report (测试不存在的报告)
        success, result = self.make_request("GET", "/api/results/999/report", auth_required=True)
        if success and result.status_code == 404:
            self.log_test("GET /api/results/{result_id}/report", True, "正确返回报告不存在", result.status_code)
        elif success and result.status_code == 200:
            self.log_test("GET /api/results/{result_id}/report", True, "获取报告成功", result.status_code)
        else:
            self.log_test("GET /api/results/{result_id}/report", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
    
    def test_parameter_endpoints(self):
        """测试参数管理接口"""
        print("\n=== 8. 参数管理接口测试 ===")
        
        if not self.token:
            self.log_test("参数管理测试", False, "缺少认证token")
            return
            
        # 19. GET /api/parameters/
        success, result = self.make_request("GET", "/api/parameters/", auth_required=True)
        param_id = None
        if success and result.status_code == 200:
            data = result.json()
            count = len(data) if isinstance(data, list) else 1
            if isinstance(data, list) and len(data) > 0:
                param_id = data[0].get('id')
            self.log_test("GET /api/parameters/", True, f"参数数量: {count}", result.status_code)
        else:
            self.log_test("GET /api/parameters/", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
        
        # 20. GET /api/parameters/{param_id} (测试不存在的参数)
        success, result = self.make_request("GET", "/api/parameters/999", auth_required=True)
        if success and result.status_code == 404:
            self.log_test("GET /api/parameters/{param_id}", True, "正确返回参数不存在", result.status_code)
        elif success and result.status_code == 200:
            data = result.json()
            self.log_test("GET /api/parameters/{param_id}", True, "获取参数详情", result.status_code)
        else:
            self.log_test("GET /api/parameters/{param_id}", False, 
                         f"状态码: {result.status_code if success else 'N/A'}", 
                         result.status_code if success else None)
    
    def test_log_endpoints(self):
        """测试日志管理接口"""
        print("\n=== 9. 日志管理接口测试 ===")
        
        if not self.token:
            self.log_test("日志管理测试", False, "缺少认证token")
            return
            
        # 21. GET /api/logs/
        success, result = self.make_request("GET", "/api/logs/", auth_required=True)
        if success:
            if result.status_code == 200:
                data = result.json()
                count = len(data) if isinstance(data, list) else 1
                self.log_test("GET /api/logs/", True, f"日志条数: {count}", result.status_code)
            else:
                self.log_test("GET /api/logs/", False, f"状态码: {result.status_code}", result.status_code)
        else:
            self.log_test("GET /api/logs/", False, "请求失败")
    
    def test_health_endpoints(self):
        """测试健康评估接口"""
        print("\n=== 10. 健康评估接口测试 ===")
        
        if not self.token:
            self.log_test("健康评估测试", False, "缺少认证token")
            return
            
        # 22. POST /api/health/evaluate
        eval_data = {"data_id": 999}
        success, result = self.make_request("POST", "/api/health/evaluate", eval_data, auth_required=True)
        if success:
            if result.status_code == 404:
                self.log_test("POST /api/health/evaluate", True, "正确返回数据不存在", result.status_code)
            elif result.status_code == 422:
                self.log_test("POST /api/health/evaluate", True, "正确验证参数", result.status_code)
            else:
                self.log_test("POST /api/health/evaluate", False, f"意外状态码: {result.status_code}", result.status_code)
        else:
            self.log_test("POST /api/health/evaluate", False, "请求失败")
            
        # 23. POST /api/health/batch-evaluate
        batch_data = {"data_ids": [999, 1000]}
        success, result = self.make_request("POST", "/api/health/batch-evaluate", batch_data, auth_required=True)
        if success:
            if result.status_code in [404, 422]:
                self.log_test("POST /api/health/batch-evaluate", True, "正确处理批量评估", result.status_code)
            elif result.status_code == 200:
                self.log_test("POST /api/health/batch-evaluate", True, "批量评估成功", result.status_code)
            else:
                self.log_test("POST /api/health/batch-evaluate", False, f"意外状态码: {result.status_code}", result.status_code)
        else:
            self.log_test("POST /api/health/batch-evaluate", False, "请求失败")
            
        # 24. GET /api/health/reports/{result_id}
        success, result = self.make_request("GET", "/api/health/reports/999", auth_required=True)
        if success:
            if result.status_code == 404:
                self.log_test("GET /api/health/reports/{result_id}", True, "正确返回报告不存在", result.status_code)
            elif result.status_code == 200:
                self.log_test("GET /api/health/reports/{result_id}", True, "获取报告成功", result.status_code)
            else:
                self.log_test("GET /api/health/reports/{result_id}", False, f"意外状态码: {result.status_code}", result.status_code)
        else:
            self.log_test("GET /api/health/reports/{result_id}", False, "请求失败")
    
    def generate_summary(self):
        """生成测试总结"""
        print("\n" + "="*60)
        print("🧪 完整API接口测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        # 按状态码分组统计
        status_codes = {}
        for test in self.test_results:
            if test["status_code"]:
                code = test["status_code"]
                if code not in status_codes:
                    status_codes[code] = 0
                status_codes[code] += 1
        
        if status_codes:
            print(f"\n状态码分布:")
            for code, count in sorted(status_codes.items()):
                print(f"  {code}: {count}次")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for test in self.test_results:
                if not test["success"]:
                    status_info = f" [{test['status_code']}]" if test['status_code'] else ""
                    print(f"  - {test['test']}{status_info}: {test['details']}")
        
        return passed_tests, failed_tests
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始完整API接口测试...")
        print(f"测试目标: {self.base_url}")
        print("预期接口数量: 24个")
        
        # 按顺序执行测试
        self.test_basic_endpoints()           # 2个接口
        self.test_authentication_endpoints()  # 2个接口  
        self.test_user_endpoints()           # 3个接口
        self.test_role_endpoints()           # 4个接口
        self.test_data_endpoints()           # 2个接口
        self.test_model_endpoints()          # 2个接口
        self.test_result_endpoints()         # 3个接口
        self.test_parameter_endpoints()      # 2个接口
        self.test_log_endpoints()            # 1个接口
        self.test_health_endpoints()         # 3个接口
        
        # 生成总结
        passed, failed = self.generate_summary()
        
        return failed == 0

def main():
    """主函数"""
    tester = CompleteAPITester()
    
    # 运行所有测试
    success = tester.run_all_tests()
    
    # 退出码：0表示成功，1表示有失败
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 