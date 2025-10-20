@echo off
echo ========================================
echo YOLOv8 智能识别停车位系统 - 快速设置
echo ========================================
echo.

echo [1/4] 检查Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)
echo Node.js 已安装 ✓

echo.
echo [2/4] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)
echo Python 已安装 ✓

echo.
echo [3/4] 安装前端依赖...
call npm install
if errorlevel 1 (
    echo 错误: 前端依赖安装失败
    pause
    exit /b 1
)
echo 前端依赖安装完成 ✓

echo.
echo [4/4] 安装后端依赖...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 后端依赖安装失败
    pause
    exit /b 1
)
cd ..
echo 后端依赖安装完成 ✓

echo.
echo ========================================
echo 设置完成！
echo ========================================
echo.
echo 下一步:
echo 1. 复制 .env.example 为 .env 并填入Supabase配置
echo 2. 复制 backend/.env.example 为 backend/.env
echo 3. 按照 SUPABASE_SETUP.md 配置Supabase
echo 4. 运行 start.bat 启动开发服务器
echo.
pause
