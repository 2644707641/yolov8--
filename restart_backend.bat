@echo off
REM 统一到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo 重启后端服务
echo ========================================

echo.

echo [1] 查找并关闭占用8000端口的进程..
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 找到进程ID: %%a
    taskkill /F /PID %%a >nul 2>&1
    echo 已关闭进程 %%a
)

echo.

echo [2] 等待端口释放...
timeout /t 2 /nobreak >nul

echo.

echo [3] 检查虚拟环境...
set "VENV_ACT="
if exist "backend\venv\Scripts\activate.bat" set "VENV_ACT=backend\venv\Scripts\activate.bat"
if not defined VENV_ACT if exist ".venv\Scripts\activate.bat" set "VENV_ACT=.venv\Scripts\activate.bat"
if not defined VENV_ACT (
    echo 错误: 未找到虚拟环境，请先创建并安装依赖：
    echo   python -m venv backend\venv
    echo   call backend\venv\Scripts\activate ^&^& pip install -r backend\requirements.txt
    pause
    exit /b 1
)

echo [4] 启动新的后端服务（使用虚拟环境）...
start "YOLOv8 Backend (Fixed)" cmd /k "call "%VENV_ACT%" ^&^& cd backend ^&^& python main.py"

echo.

echo ========================================
echo 后端服务已重启！
echo ========================================

echo.

echo 访问: http://localhost:8000
echo 文档: http://localhost:8000/docs
echo.
pause
