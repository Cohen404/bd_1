#!/bin/bash

# 设置错误时退出
set -e

echo "Starting installation of BJ Health Management System..."

# 检查是否已安装必要的系统包
echo "Checking and installing system dependencies..."
sudo apt-get update

# 添加deadsnakes PPA用于安装Python 3.10
echo "Adding deadsnakes PPA for Python 3.10..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

# 安装Python 3.10.12和其他系统依赖
echo "Installing Python 3.10.12 and other dependencies..."
sudo apt-get install -y \
    python3.10=3.10.12* \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    poppler-utils \
    nvidia-cuda-toolkit \
    nvidia-cuda-toolkit-gcc \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    qtbase5-dev-tools \
    libqt5gui5 \
    libqt5core5a \
    libqt5widgets5 \
    libqt5x11extras5 \
    libqt5x11extras5-dev \
    libqt5webengine5 \
    libqt5webenginecore5 \
    libqt5webenginewidgets5 \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    python3-pyqt5.qtwebchannel \
    python3-pyqt5.qtwebsockets \
    qt5-gtk-platformtheme \
    qt5-style-plugins \
    libqt5svg5-dev \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    '^libxcb.*' \
    libx11-xcb1 \
    libglu1-mesa-dev \
    libxrender-dev \
    libxi-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev

# 安装系统依赖
echo "正在安装系统依赖..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pyqt5 python3-pyqt5.qtwebengine evince xdg-utils

# 设置环境变量
echo "Setting up environment variables..."
sudo bash -c 'cat > /etc/profile.d/qt.sh << EOF
# Qt environment variables
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=gtk2
export QT_STYLE_OVERRIDE=gtk2
export QT_XCB_GL_INTEGRATION=xcb_egl
# 确保使用系统Qt插件而不是OpenCV的
export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins:/usr/lib/qt5/plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH
export PYTHONPATH=/usr/lib/python3/dist-packages:\$PYTHONPATH
# 禁用OpenCV的Qt插件
export OPENCV_QT_DISABLE=1
EOF'

# 设置文件权限
sudo chmod 644 /etc/profile.d/qt.sh

# 立即应用环境变量
source /etc/profile.d/qt.sh

# 同时也添加到当前用户的配置中
echo "Adding environment variables to user profile..."
cat >> ~/.bashrc << EOF

# Qt environment variables
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORMTHEME=gtk2
export QT_STYLE_OVERRIDE=gtk2
export QT_XCB_GL_INTEGRATION=xcb_egl
# 确保使用系统Qt插件而不是OpenCV的
export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins:/usr/lib/qt5/plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH
export PYTHONPATH=/usr/lib/python3/dist-packages:\$PYTHONPATH
# 禁用OpenCV的Qt插件
export OPENCV_QT_DISABLE=1
EOF

source ~/.bashrc

# 确保Qt插件目录存在并设置正确的权限
echo "Setting up Qt plugins directory..."
sudo mkdir -p /usr/lib/x86_64-linux-gnu/qt5/plugins/platforms

# 检查XCB插件是否存在并可用
if [ ! -f "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/libqxcb.so" ]; then
    echo "Error: XCB plugin not found. Installing additional Qt packages..."
    sudo apt-get install -y \
        libqt5x11extras5 \
        libqt5x11extras5-dev \
        qt5-gtk-platformtheme
fi

# 设置Python 3.10为默认版本
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# 创建并激活Python虚拟环境
echo "Creating Python virtual environment..."
rm -rf venv  # 确保删除旧的虚拟环境
python3.10 -m venv venv --clear
source venv/bin/activate

# 验证是否在虚拟环境中
if [[ "$VIRTUAL_ENV" != *"venv"* ]]; then
    echo "Error: Not in virtual environment"
    exit 1
fi

# 验证Python版本和路径
echo "Verifying Python environment..."
python_version=$(python3 --version)
python_path=$(which python3)
if [[ "$python_version" != *"3.10.12"* ]]; then
    echo "Error: Wrong Python version. Expected 3.10.12, got $python_version"
    exit 1
fi
if [[ "$python_path" != *"venv"* ]]; then
    echo "Error: Python is not from virtual environment. Path: $python_path"
    exit 1
fi

# 配置pip使用清华源
echo "Configuring pip to use Tsinghua mirror..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 升级pip并安装wheel
echo "Upgrading pip and installing wheel..."
python3 -m pip install --upgrade pip wheel setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证pip路径
pip_path=$(which pip)
if [[ "$pip_path" != *"venv"* ]]; then
    echo "Error: pip is not from virtual environment. Path: $pip_path"
    exit 1
fi

# 强制重新安装所有Python依赖到虚拟环境
echo "Installing Python dependencies..."
# 先卸载可能存在的包
pip uninstall -y -r requirements.txt || true
# 强制重新安装所有包，忽略已安装的系统包
pip install --ignore-installed -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 验证安装位置
echo "Verifying package installation locations..."
VENV_PATH=$(realpath "./venv")
echo "Virtual environment path: $VENV_PATH"
echo "Checking package locations..."

packages_outside_venv=0
while IFS= read -r line; do
    if [[ $line == *"Location:"* ]]; then
        pkg_name=$(echo "$line" | awk '{print $1}')
        pkg_path=$(echo "$line" | awk '{print $2}')
        if [[ "$pkg_path" != "$VENV_PATH"* ]]; then
            echo "Warning: Package '$pkg_name' is installed outside virtual environment at: $pkg_path"
            ((packages_outside_venv++))
        fi
    fi
done < <(pip list -v)

echo "Package verification summary:"
echo "- Total packages checked: $(pip list | wc -l)"
echo "- Packages outside venv: $packages_outside_venv"
echo "Package installation verification completed."

# 打印Python环境信息
echo "Python environment information:"
echo "- Python version: $(python --version)"
echo "- Python path: $(which python)"
echo "- Pip version: $(pip --version)"
echo "- Virtual env: $VIRTUAL_ENV"

# 配置PostgreSQL数据库
echo "Configuring PostgreSQL database..."
# 检查PostgreSQL服务是否在运行
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
echo "Creating database and user..."
sudo -u postgres psql << EOF
CREATE DATABASE bj_health_db;
CREATE USER bj_health_user WITH PASSWORD 'bj_health_pass';
ALTER ROLE bj_health_user SET client_encoding TO 'utf8';
ALTER ROLE bj_health_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE bj_health_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE bj_health_db TO bj_health_user;
\c bj_health_db
EOF

# 导入数据库结构
echo "Importing database schema..."
sudo -u postgres psql bj_health_db < sql_model.sql

# 创建.env文件
echo "Creating .env file..."
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bj_health_db
DB_USER=bj_health_user
DB_PASS=bj_health_pass
SECRET_KEY=your_secret_key_here
DEBUG=False
EOF

# 创建必要的目录
echo "Creating necessary directories..."
mkdir -p log
mkdir -p data
mkdir -p data/results
mkdir -p model
mkdir -p templates
mkdir -p state

# 设置权限
echo "Setting permissions..."
chmod +x run.py

# 创建运行脚本
echo "Creating run script..."
cat > run_system.sh << 'EOF'
#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 进入项目目录
cd "$SCRIPT_DIR"

# 激活虚拟环境
source venv/bin/activate

# 检查PostgreSQL服务是否在运行
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
fi

# 运行应用
echo "Starting BJ Health Management System..."
python run.py
EOF

chmod +x run_system.sh

# 创建桌面启动器
echo "Creating desktop launcher..."
WORKSPACE_PATH=$(pwd)

# 复制系统图标到项目目录
echo "Setting up application icon..."
sudo cp /usr/share/icons/gnome/48x48/apps/system-config-users.png "${WORKSPACE_PATH}/app_icon.png"
sudo chmod 644 "${WORKSPACE_PATH}/app_icon.png"

cat > BJ_Health_System.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BJ Health Management System
Comment=Launch BJ Health Management System
Exec=${WORKSPACE_PATH}/run_system.sh
Icon=${WORKSPACE_PATH}/app_icon.png
Terminal=false
Categories=Application;
EOF

# 设置启动器权限
chmod +x BJ_Health_System.desktop

# 检测桌面目录位置并复制启动器
echo "Detecting desktop directory..."
DESKTOP_DIR=""
# 检查可能的桌面目录
for dir in "$HOME/Desktop" "$HOME/桌面" "$XDG_DESKTOP_DIR" "$(xdg-user-dir DESKTOP)"; do
    if [ -d "$dir" ]; then
        DESKTOP_DIR="$dir"
        break
    fi
done

if [ -z "$DESKTOP_DIR" ]; then
    echo "Warning: Could not find desktop directory. The launcher will be created in home directory."
    echo "Please manually move BJ_Health_System.desktop to your desktop directory."
    DESKTOP_DIR="$HOME"
fi

# 复制启动器到检测到的目录
echo "Copying launcher to $DESKTOP_DIR..."
cp BJ_Health_System.desktop "$DESKTOP_DIR/"
chmod +x "$DESKTOP_DIR/BJ_Health_System.desktop"

# 更新项目状态文件
echo "Updating project status..."
cat >> project-status.md << EOF

## $(date '+%Y-%m-%d %H:%M:%S') - System Installation
- Installed system dependencies
- Created Python virtual environment
- Installed Python packages from requirements.txt
- Configured PostgreSQL database
- Created necessary directories
- Set up environment variables
- Created desktop launcher for easy access
EOF

echo "Installation completed successfully!"
echo "To start using the system, you can either:"
echo "1. Double click the 'BJ Health Management System' icon on your desktop"
echo "2. Or manually:"
echo "   a. Activate the virtual environment: source venv/bin/activate"
echo "   b. Run the application: python run.py"
echo "3. Default admin credentials:"
echo "   Username: admin"
echo "   Password: 123456" 