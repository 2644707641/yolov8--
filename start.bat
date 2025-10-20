@echo off
REM 统一到脚本所在目录，避免路径问题（例如中文/空格路径）
cd /d "%~dp0"

echo ========================================
echo YOLOv8 智能识别停车位系统 - 启动服务
echo ========================================

echo.

echo 检查环境变量文件..
if not exist .env (
    echo 警告: 未找到 .env 文件
    echo 请复制 .env.example 为 .env 并配置Supabase信息
    pause
    exit /b 1
)

if not exist backend\.env (
    echo 警告: 未找到 backend\.env 文件
    echo 请复制 backend\.env.example 为 backend\.env
    pause
    exit /b 1
)

echo 检查虚拟环境...
set "VENV_ACT="
if exist "backend\venv\Scripts\activate.bat" set "VENV_ACT=backend\venv\Scripts\activate.bat"
if not defined VENV_ACT if exist ".venv\Scripts\activate.bat" set "VENV_ACT=.venv\Scripts\activate.bat"
if not defined VENV_ACT (
    echo 错误: 未找到虚拟环境，请先创建并安装依赖：
    echo   1^) 后端目录创建虚拟环境:  python -m venv backend\venv
    echo   2^) 激活并安装依赖:      call backend\venv\Scripts\activate ^&^& pip install -r backend\requirements.txt
    pause
    exit /b 1
)

echo 环境变量与虚拟环境已就绪。
echo.

echo 启动后端服务（使用虚拟环境）...
start "YOLOv8 Backend" cmd /k "call "%VENV_ACT%" ^&^& cd backend ^&^& python main.py"

echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo 启动前端服务...
start "YOLOv8 Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo 服务已启动！
echo ========================================
echo.
echo 前端: http://localhost:3000
echo 后端: http://localhost:8000
echo 后端文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口..
pause >nul
