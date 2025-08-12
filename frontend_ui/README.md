# 北京健康评估系统 - 前端界面

基于React + TypeScript + Tailwind CSS构建的现代化Web前端应用，为北京健康评估系统提供用户界面。

## 🚀 功能特性

### 🔐 用户认证
- 登录/登出功能
- JWT Token认证
- 用户角色权限控制

### 👥 用户功能
- **控制台**: 数据概览和快速操作
- **健康评估**: EEG数据的实时健康评估
- **数据管理**: 数据文件上传、管理和处理
- **结果管理**: 评估结果查看和报告下载

### 🔧 管理员功能
- **管理控制台**: 系统监控和管理
- **用户管理**: 用户账户管理
- **角色管理**: 权限配置
- **模型管理**: AI模型文件管理
- **参数管理**: 系统配置
- **日志管理**: 操作日志审计

## 🛠️ 技术栈

- **框架**: React 18 + TypeScript
- **路由**: React Router DOM v6
- **样式**: Tailwind CSS
- **状态管理**: React Hooks + Context
- **表单处理**: React Hook Form
- **HTTP客户端**: Axios
- **UI组件**: Lucide React图标
- **通知**: React Hot Toast
- **图表**: Recharts
- **构建工具**: Vite

## 📦 安装依赖

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🔧 开发配置

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 开发服务器
- 前端端口: http://localhost:3000
- 后端API代理: http://127.0.0.1:8000

### API代理配置
开发环境下，所有 `/api` 请求会被代理到后端服务器 `http://127.0.0.1:8000`。

## 📁 项目结构

```
frontend_ui/
├── public/                 # 静态资源
├── src/                   # 源代码
│   ├── components/        # 可复用组件
│   │   ├── Common/       # 通用组件
│   │   └── Layout/       # 布局组件
│   ├── hooks/            # 自定义Hooks
│   ├── pages/            # 页面组件
│   ├── types/            # TypeScript类型定义
│   ├── utils/            # 工具函数
│   │   ├── api.ts        # API请求封装
│   │   ├── auth.ts       # 认证工具
│   │   └── helpers.ts    # 辅助函数
│   ├── App.tsx           # 应用根组件
│   ├── main.tsx          # 应用入口
│   └── index.css         # 全局样式
├── package.json          # 项目配置
├── tailwind.config.js    # Tailwind配置
├── tsconfig.json         # TypeScript配置
└── vite.config.ts        # Vite配置
```

## 🔐 认证系统

### 默认登录账户
- **管理员**: admin / admin123
- **普通用户**: user / user123

### 权限控制
- 管理员: 拥有所有功能权限
- 普通用户: 基础功能权限（控制台、健康评估、数据管理、结果管理）

## 🎨 界面设计

### 设计系统
- **主色调**: 蓝色系 (#0ea5e9)
- **背景色**: #d4e2f4 (与原应用保持一致)
- **字体**: Inter字体族
- **图标**: Lucide React

### 响应式设计
- 支持桌面端 (1200px+)
- 支持平板端 (768px-1199px)
- 支持移动端 (320px-767px)

## 🔌 API集成

### API基础配置
- 基础URL: `/api`
- 认证方式: Bearer Token
- 请求超时: 30秒
- 自动错误处理和提示

### 主要API端点
- **认证**: POST /api/login
- **用户管理**: /api/users/*
- **数据管理**: /api/data/*
- **健康评估**: /api/health/*
- **结果管理**: /api/results/*
- **模型管理**: /api/models/*

## 🎯 开发指南

### 代码规范
- 使用TypeScript严格模式
- 遵循React最佳实践
- 使用ESLint代码检查
- 统一的代码格式化

### 组件开发
- 使用函数式组件 + Hooks
- Props类型定义
- 合理的组件拆分
- 可复用组件设计

### 状态管理
- 本地状态: useState/useReducer
- 全局状态: Context + useReducer
- 服务端状态: 自定义hooks封装

## 🚀 部署说明

### 生产构建
```bash
npm run build
```

### 环境变量
生产环境需要配置：
- API服务器地址
- 其他环境相关配置

### 静态文件部署
构建后的 `dist` 目录可以部署到任何静态文件服务器。

## 📚 相关文档

- [React官方文档](https://react.dev/)
- [TypeScript文档](https://www.typescriptlang.org/)
- [Tailwind CSS文档](https://tailwindcss.com/)
- [Vite文档](https://vitejs.dev/)

## 🆘 常见问题

### 1. 启动失败
- 检查Node.js版本 (>=16.0.0)
- 清除node_modules重新安装: `rm -rf node_modules && npm install`

### 2. API请求失败
- 检查后端服务是否启动
- 确认API代理配置正确

### 3. 登录问题
- 使用默认账户测试
- 检查后端认证服务

## 📄 版权信息

© 2024 北京健康评估系统 v1.0.0 