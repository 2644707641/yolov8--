@echo off
echo ========================================
echo 修复PyTorch版本兼容性问题
echo ========================================
echo.
echo 当前问题: PyTorch 2.8.0 的 weights_only 新特性导致无法加载旧模型
echo 解决方案: 降级到稳定版本 PyTorch 2.0.1
echo.
echo 这个过程需要几分钟...
echo.
pause

cd backend

echo [1] 激活虚拟环境...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 虚拟环境不存在，使用全局Python环境
)

echo.
echo [2] 卸载当前PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo [3] 安装PyTorch 2.0.1 (稳定版)...
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu

echo.
echo [4] 验证安装...
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')"

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 请重启后端服务：
echo   cd backend
echo   python main.py
echo.
pause
