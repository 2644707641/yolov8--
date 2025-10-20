@echo off
echo ========================================
echo 在虚拟环境中修复PyTorch版本问题
echo ========================================
echo.
echo 当前问题: PyTorch 2.8.0 与旧模型不兼容
echo 解决方案: 降级到 PyTorch 2.5.1 (最后一个稳定的2.x版本)
echo.
pause

echo.
echo [1] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo [2] 检查当前PyTorch版本...
python -c "import torch; print('当前PyTorch版本:', torch.__version__)"

echo.
echo [3] 卸载当前PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo [4] 安装PyTorch 2.5.1...
pip install torch==2.5.1 torchvision==0.20.1

echo.
echo [5] 验证新版本...
python -c "import torch; print('新PyTorch版本:', torch.__version__)"

echo.
echo [6] 测试模型加载...
python test_model.py

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 现在请重启后端服务：
echo   双击运行 restart_backend.bat
echo.
pause
