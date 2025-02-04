#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 进入项目目录
cd "$SCRIPT_DIR"

# 创建日志目录
mkdir -p "$SCRIPT_DIR/log"
LOG_FILE="$SCRIPT_DIR/log/system.log"

# 将所有输出重定向到日志文件
exec 1>> "$LOG_FILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting BJ Health Management System..."

# 移除OpenCV的Qt插件目录
CV2_QT_PLUGIN_PATH="$SCRIPT_DIR/venv/lib/python3.10/site-packages/cv2/qt/plugins"
if [ -d "$CV2_QT_PLUGIN_PATH" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Removing OpenCV Qt plugins directory..."
    rm -rf "$CV2_QT_PLUGIN_PATH"
fi

# 设置Qt环境变量
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=gtk2
export QT_STYLE_OVERRIDE=gtk2
export QT_XCB_GL_INTEGRATION=xcb_egl

# 强制使用系统Qt插件
export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# 禁用OpenCV的Qt插件
export OPENCV_QT_DISABLE=1
export OPENCV_QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms

# 清除可能冲突的环境变量
unset PYTHONPATH
unset QT_QPA_PLATFORM_PLUGIN_PATH_BACKUP

# 激活虚拟环境
source venv/bin/activate

# 检查PostgreSQL服务是否在运行
if ! systemctl is-active --quiet postgresql; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting PostgreSQL service..."
    sudo systemctl start postgresql
fi

# 检查系统Qt插件
if [ ! -f "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/libqxcb.so" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - System XCB plugin not found. Installing Qt packages..."
    sudo apt-get install -y \
        libqt5gui5 \
        libqt5x11extras5 \
        libqt5x11extras5-dev \
        qt5-gtk-platformtheme
    if [ ! -f "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/libqxcb.so" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to install system XCB plugin."
        exit 1
    fi
fi

# 运行应用
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting application..."
python run.py 