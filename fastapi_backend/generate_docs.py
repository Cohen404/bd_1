#!/usr/bin/env python3
"""
API文档生成脚本
从OpenAPI规范生成README格式的API文档
"""

import json
import requests
from typing import Dict, Any, List
from datetime import datetime

class DocGenerator:
    def __init__(self, openapi_url: str = "http://localhost:8000/openapi.json"):
        self.openapi_url = openapi_url
        self.api_spec = None
        
    def fetch_openapi_spec(self):
        """获取OpenAPI规范"""
        try:
            response = requests.get(self.openapi_url)
            response.raise_for_status()
            self.api_spec = response.json()
            return True
        except Exception as e:
            print(f"获取OpenAPI规范失败: {e}")
            return False
    
    def generate_markdown_docs(self) -> str:
        """生成Markdown格式的API文档"""
        if not self.api_spec:
            return "无法生成文档：OpenAPI规范未加载"
            
        md = []
        
        # 标题和基本信息
        info = self.api_spec.get("info", {})
        md.append(f"# {info.get('title', '北京健康评估系统API')}")
        md.append("")
        md.append(f"**版本**: {info.get('version', '1.0.0')}")
        md.append(f"**描述**: {info.get('description', '北京健康评估系统的后端API接口')}")
        md.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")
        
        # 服务器信息
        servers = self.api_spec.get("servers", [])
        if servers:
            md.append("## 🌐 服务器")
            for server in servers:
                md.append(f"- **{server.get('description', '默认服务器')}**: {server.get('url', 'http://localhost:8000')}")
            md.append("")
            
        # 认证说明
        md.append("## 🔐 认证")
        md.append("本API使用JWT Bearer Token认证。")
        md.append("")
        md.append("### 获取Token")
        md.append("```bash")
        md.append("# 方式1: JSON格式登录")
        md.append('curl -X POST "http://localhost:8000/api/login" \\')
        md.append('  -H "Content-Type: application/json" \\')
        md.append('  -d \'{"username":"admin","password":"admin123"}\'')
        md.append("")
        md.append("# 方式2: OAuth2格式登录")
        md.append('curl -X POST "http://localhost:8000/api/token" \\')
        md.append('  -H "Content-Type: application/x-www-form-urlencoded" \\')
        md.append('  -d "username=admin&password=admin123"')
        md.append("```")
        md.append("")
        md.append("### 使用Token")
        md.append("```bash")
        md.append('curl -X GET "http://localhost:8000/api/users/me" \\')
        md.append('  -H "Authorization: Bearer YOUR_TOKEN_HERE"')
        md.append("```")
        md.append("")
        
        # API接口列表
        paths = self.api_spec.get("paths", {})
        if paths:
            md.append("## 📚 API接口")
            md.append("")
            
            # 按标签分组
            grouped_paths = self._group_paths_by_tags(paths)
            
            for tag, endpoints in grouped_paths.items():
                md.append(f"### {tag}")
                md.append("")
                
                for path, path_info in endpoints:
                    for method, method_info in path_info.items():
                        if method in ['get', 'post', 'put', 'delete', 'patch']:
                            md.extend(self._format_endpoint(path, method, method_info))
                            md.append("")
                        
        # 数据模型
        components = self.api_spec.get("components", {})
        schemas = components.get("schemas", {})
        if schemas:
            md.append("## 📋 数据模型")
            md.append("")
            for schema_name, schema_info in schemas.items():
                if not schema_name.startswith("HTTPValidationError"):
                    md.extend(self._format_schema(schema_name, schema_info))
                    md.append("")
                    
        # 错误代码
        md.append("## ⚠️ 错误代码")
        md.append("")
        md.append("| 状态码 | 说明 |")
        md.append("|--------|------|")
        md.append("| 200 | 请求成功 |")
        md.append("| 201 | 创建成功 |")
        md.append("| 400 | 请求参数错误 |")
        md.append("| 401 | 未授权（未登录或token无效） |")
        md.append("| 403 | 禁止访问（权限不足） |")
        md.append("| 404 | 资源不存在 |")
        md.append("| 422 | 参数验证失败 |")
        md.append("| 500 | 服务器内部错误 |")
        md.append("")
        
        return "\n".join(md)
    
    def _group_paths_by_tags(self, paths: Dict) -> Dict[str, List]:
        """按标签分组路径"""
        grouped = {}
        
        for path, path_info in paths.items():
            for method, method_info in path_info.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tags = method_info.get("tags", ["其他"])
                    tag = tags[0] if tags else "其他"
                    
                    if tag not in grouped:
                        grouped[tag] = []
                    grouped[tag].append((path, {method: method_info}))
                    
        return grouped
    
    def _format_endpoint(self, path: str, method: str, method_info: Dict) -> List[str]:
        """格式化单个接口文档"""
        lines = []
        
        summary = method_info.get("summary", "")
        description = method_info.get("description", "")
        
        # 接口标题
        lines.append(f"#### `{method.upper()}` {path}")
        if summary:
            lines.append(f"**{summary}**")
        if description and description != summary:
            lines.append(f"{description}")
        lines.append("")
        
        # 请求参数
        parameters = method_info.get("parameters", [])
        request_body = method_info.get("requestBody", {})
        
        if parameters:
            lines.append("**请求参数:**")
            lines.append("| 参数名 | 类型 | 位置 | 必须 | 描述 |")
            lines.append("|--------|------|------|------|------|")
            for param in parameters:
                name = param.get("name", "")
                param_type = param.get("schema", {}).get("type", "string")
                location = param.get("in", "")
                required = "是" if param.get("required", False) else "否"
                desc = param.get("description", "")
                lines.append(f"| {name} | {param_type} | {location} | {required} | {desc} |")
            lines.append("")
            
        if request_body:
            content = request_body.get("content", {})
            if "application/json" in content:
                lines.append("**请求体:** JSON格式")
                schema = content["application/json"].get("schema", {})
                if "$ref" in schema:
                    ref_name = schema["$ref"].split("/")[-1]
                    lines.append(f"参考数据模型: `{ref_name}`")
                lines.append("")
        
        # 响应示例
        responses = method_info.get("responses", {})
        if "200" in responses:
            response_200 = responses["200"]
            lines.append("**成功响应 (200):**")
            description = response_200.get("description", "")
            if description:
                lines.append(description)
            
            content = response_200.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                if "$ref" in schema:
                    ref_name = schema["$ref"].split("/")[-1]
                    lines.append(f"返回数据模型: `{ref_name}`")
            lines.append("")
        
        # 示例请求
        lines.append("**示例请求:**")
        lines.append("```bash")
        
        if method.upper() == "GET":
            lines.append(f'curl -X GET "http://localhost:8000{path}" \\')
            lines.append('  -H "Authorization: Bearer YOUR_TOKEN"')
        elif method.upper() == "POST":
            lines.append(f'curl -X POST "http://localhost:8000{path}" \\')
            lines.append('  -H "Content-Type: application/json" \\')
            lines.append('  -H "Authorization: Bearer YOUR_TOKEN" \\')
            if request_body:
                lines.append('  -d \'{"key": "value"}\'')
        elif method.upper() in ["PUT", "PATCH"]:
            lines.append(f'curl -X {method.upper()} "http://localhost:8000{path}" \\')
            lines.append('  -H "Content-Type: application/json" \\')
            lines.append('  -H "Authorization: Bearer YOUR_TOKEN" \\')
            lines.append('  -d \'{"key": "value"}\'')
        elif method.upper() == "DELETE":
            lines.append(f'curl -X DELETE "http://localhost:8000{path}" \\')
            lines.append('  -H "Authorization: Bearer YOUR_TOKEN"')
            
        lines.append("```")
        
        return lines
    
    def _format_schema(self, schema_name: str, schema_info: Dict) -> List[str]:
        """格式化数据模型"""
        lines = []
        
        lines.append(f"### {schema_name}")
        
        description = schema_info.get("description", "")
        if description:
            lines.append(description)
            lines.append("")
        
        properties = schema_info.get("properties", {})
        required = schema_info.get("required", [])
        
        if properties:
            lines.append("| 字段名 | 类型 | 必须 | 描述 |")
            lines.append("|--------|------|------|------|")
            
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "string")
                if "format" in prop_info:
                    prop_type += f" ({prop_info['format']})"
                elif "$ref" in prop_info:
                    prop_type = prop_info["$ref"].split("/")[-1]
                elif prop_info.get("type") == "array":
                    items = prop_info.get("items", {})
                    if "$ref" in items:
                        prop_type = f"array[{items['$ref'].split('/')[-1]}]"
                    else:
                        prop_type = f"array[{items.get('type', 'object')}]"
                        
                is_required = "是" if prop_name in required else "否"
                prop_desc = prop_info.get("description", "")
                
                lines.append(f"| {prop_name} | {prop_type} | {is_required} | {prop_desc} |")
        
        return lines
    
    def save_openapi_json(self, filename: str = "openapi_generated.json"):
        """保存OpenAPI JSON文档"""
        if not self.api_spec:
            return False
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.api_spec, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存OpenAPI JSON失败: {e}")
            return False
    
    def save_markdown_docs(self, filename: str = "API_DOCS.md"):
        """保存Markdown文档"""
        try:
            md_content = self.generate_markdown_docs()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            return True
        except Exception as e:
            print(f"保存Markdown文档失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 开始生成API文档...")
    
    generator = DocGenerator()
    
    # 获取OpenAPI规范
    if not generator.fetch_openapi_spec():
        print("❌ 无法获取OpenAPI规范，请确保服务正在运行")
        return False
    
    print("✅ OpenAPI规范获取成功")
    
    # 保存OpenAPI JSON
    if generator.save_openapi_json("openapi_generated.json"):
        print("✅ OpenAPI JSON文档已生成: openapi_generated.json")
    else:
        print("❌ OpenAPI JSON文档生成失败")
    
    # 保存Markdown文档
    if generator.save_markdown_docs("API_DOCS.md"):
        print("✅ Markdown API文档已生成: API_DOCS.md")
    else:
        print("❌ Markdown API文档生成失败")
    
    print("\n📚 文档生成完成！")
    print("- OpenAPI规范: openapi_generated.json")
    print("- API文档: API_DOCS.md")
    print("- 在线API文档: http://localhost:8000/docs")
    print("- ReDoc文档: http://localhost:8000/redoc")
    
    return True

if __name__ == "__main__":
    main() 