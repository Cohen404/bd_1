#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 进入项目目录
cd "$SCRIPT_DIR"

# 激活虚拟环境
source venv/bin/activate

# 运行上传客户端
echo "Starting Upload Client..."
python upload_app/upload_window.py
