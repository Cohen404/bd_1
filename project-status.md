# 项目状态

## 系统备份和恢复功能更新 (2024-03-21)

### 已完成
- 在参数管理界面添加系统备份和恢复功能
  - 添加备份按钮和恢复按钮
  - 实现系统备份功能
    - 备份数据库文件
    - 备份data目录（数据存储）
    - 备份model目录（模型文件）
    - 备份data/results目录（结果报告）
  - 实现系统恢复功能
    - 从备份文件恢复数据库
    - 从备份文件恢复data目录
    - 从备份文件恢复model目录
  - 备份文件统一存储在.backup目录
  - 添加完整的错误处理和日志记录
  - 添加用户确认对话框，防止误操作

### 待完成
- 测试备份和恢复功能
- 验证所有数据是否能正确备份和恢复
- 检查错误处理是否完善

### 注意事项
- 备份文件命名格式：system_backup_YYYYMMDD_HHMMSS.zip
- 备份和恢复操作需要谨慎，建议在系统空闲时进行
- 恢复操作会覆盖现有数据，需要用户确认
- 确保有足够的磁盘空间进行备份

## 用户角色管理系统更新

### 已完成
- 修改数据库初始化代码,确保用户角色关系正确
  - 添加参数管理(PERM_PARAM_MANAGE)权限
  - 添加日志管理(PERM_LOG_MANAGE)权限
  - 将新增权限分配给管理员角色
- 更新健康评估界面的权限判断逻辑
- 更新数据管理界面的权限判断逻辑  
- 更新结果管理界面的权限判断逻辑
- 更新普通用户主页(index_backend.py)
  - 添加获取用户权限的函数
  - 根据权限动态显示功能按钮
  - 优化按钮布局,实现紧凑排列
- 更新管理员主页(admin_index_backend.py)
  - 添加获取用户权限的函数
  - 根据权限动态显示功能按钮
  - 优化按钮布局,实现紧凑排列

### 待完成
- 测试所有修改的功能
- 验证用户权限控制是否正确生效
- 检查是否有遗漏的界面需要更新

### 注意事项
- 所有界面使用统一的用户角色判断逻辑
- 使用user_type字段判断用户角色
- 保持原有功能的完整性
- 根据数据库中的权限配置动态显示功能按钮
- 按钮布局采用两行紧凑排列,确保界面美观
- 确保所有功能权限都在数据库中正确定义和分配 

## 2025-01-31 环境配置更新
### GPU 配置问题
- 问题：TensorFlow 无法识别 GPU
- 原因：CUDA 版本不匹配（系统 CUDA 12.4 与 TensorFlow 2.14.0 不兼容）
- 解决方案：
  1. 升级 CUDA 到 12.3 版本
  2. 重新配置 CUDA 环境变量
  3. 确保安装正确版本的 cuDNN

### Qt 插件问题
- 问题：无法加载 Qt platform plugin "xcb"
- 原因：Qt 依赖库配置不完整或冲突
- 解决方案：
  1. 安装 xcb 相关系统依赖：
     ```bash
     sudo apt-get install libxcb-xinerama0 libxcb-cursor0 libxcb1 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-render0 libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-util1 libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0
     ```
  2. 重新安装 PyQt5 相关包：
     ```bash
     pip uninstall -y PyQt5 PyQt5-Qt5 PyQt5-sip PyQtWebEngine PyQtWebEngine-Qt5
     pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6
     ```
  3. 设置 Qt 环境变量：
     ```bash
     export QT_DEBUG_PLUGINS=1
     export QT_QPA_PLATFORM=xcb
     ```

### 环境详情
- GPU: NVIDIA GeForce RTX 2080 Ti
- NVIDIA Driver: 550.142
- Current CUDA: 12.3
- Required CUDA: 12.3
- TensorFlow: 2.17.0

### 更新记录
- 添加 CUDA 12.3 相关依赖到 requirements.txt
  - nvidia-cuda-runtime-cu12==12.3.107
  - nvidia-cuda-cupti-cu12==12.3.101
  - nvidia-cudnn-cu12==8.9.7.29
  - nvidia-cublas-cu12==12.3.4.1
  - nvidia-cufft-cu12==11.0.12.1
  - nvidia-curand-cu12==10.3.4.107
  - nvidia-cusolver-cu12==11.5.4.107
  - nvidia-cusparse-cu12==12.1.3.153
  - nvidia-nccl-cu12==2.19.3

## 2024-03-21 应激评估模型优化（更新）
### 修改内容
1. 修改了 `model/tuili.py`：
   - 添加了静态变量 `_model` 用于存储预加载的模型
   - 添加了静态方法 `load_static_model()` 用于从数据库加载普通应激模型
   - 修改 `predict()` 方法使用静态模型变量
   - 增强了错误处理和日志记录
   - 优化了代码注释

2. 修改了 `backend/init_login_backend.py`：
   - 移除了全局变量 `global_model`
   - 修改预加载逻辑，使用 `EegModel.load_static_model()` 静态方法
   - 从数据库获取模型路径（model_type=0的普通应激模型）
   - 添加了相关的错误处理和日志记录

### 优化效果
1. 提高了应激评估的性能：
   - 模型只需要加载一次，避免了重复加载
   - 系统启动时就预加载模型到内存
   - 使用静态变量存储模型，更高效的内存使用
2. 简化了评估流程：
   - 三种应激评估（普通应激、焦虑、抑郁）共用同一个模型
   - 评估结果完全相同，提高了一致性
   - 从数据库动态获取模型路径，更灵活的模型管理
3. 增强了系统稳定性：
   - 添加了完整的错误处理机制
   - 改进了日志记录，便于问题追踪
   - 使用数据库管理模型信息，更可靠的模型加载

### 注意事项
- 保持了原有的评估结果展示、存储和模型状态检测逻辑不变
- 界面提示仍然保持英文
- 代码风格和架构与原有代码保持一致
- 确保数据库中存在 model_type=0 的普通应激模型记录 

## 环境配置
- Python 3.10
- CUDA 12.3
- TensorFlow 2.17
- PyQt5 5.15.9
- PyQtWebEngine 5.15.6

## 最新更新
- 2024-01-31: 修复了Qt界面显示问题
  - 安装了必要的Qt依赖库(libxcb相关包)
  - 重新安装了PyQt5和PyQtWebEngine
  - 更新了CUDA依赖到12.3版本
  - 程序现在可以正常启动和运行

### 2024-03-21
- 在健康评估功能中添加了进度条显示
  - 修改了 `backend/health_evaluate_backend.py`
  - 添加了实时进度显示功能
  - 每个模型评估占33%进度
  - 保持了原有功能的完整性
  - 所有提示使用中文显示
  - 添加了评估时间计时功能
    - 使用QTimer实现实时计时
    - 显示分钟和秒数
    - 计时器在单独线程运行，不阻塞主进程
    - 评估完成或取消时自动停止计时

### 主要改动
1. 在`Health_Evaluate_WindowActions`类中添加进度条属性和计时器
2. 修改`status_model`方法，实现进度条的创建和初始化
3. 修改`waitTestRes`方法，实现进度条的实时更新
4. 添加`update_timer`方法，实现计时功能
5. 保持了原有的评估逻辑不变

### 2024-03-22 模型评估优化（第五次更新）
- 简化了模型评估流程
  - 创建了新的 `EvaluateThread` 类，在单个线程中处理所有三种评估
  - 第一个模型使用实际推理，后两个模型直接复用结果
  - 保持了原有的评估结果处理逻辑不变
  - 优化了日志记录，方便追踪评估流程

### 主要改动
1. 评估流程优化：
   - 简化为单个评估线程
   - 移除了多余的模型加载和推理
   - 保持了原有的评估结果处理逻辑
2. 错误处理改进：
   - 添加了完整的错误栈输出
   - 优化了错误信息的记录
   - 增强了异常处理机制
3. 代码结构优化：
   - 新增 `EvaluateThread` 类
   - 简化了线程管理
   - 提高了代码可维护性

## 待办事项
- [ ] 优化数据库查询性能
- [ ] 添加更多数据可视化功能
- [ ] 实现用户管理系统
- [ ] 继续优化用户界面体验
- [ ] 完善错误处理机制
- [ ] 优化数据处理性能
