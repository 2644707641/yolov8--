@echo off
chcp 65001 > nul
echo ============================================
echo FFmpeg 快速安装工具
echo ============================================
echo.

REM 检查是否已安装
where ffmpeg >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ FFmpeg已经安装
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo 视频将自动优化为流畅格式！
    goto :end
)

echo FFmpeg未安装，准备安装...
echo.
echo 请选择安装方式：
echo.
echo [1] 使用Scoop安装（推荐，自动化）
echo [2] 使用Chocolatey安装
echo [3] 手动下载安装
echo [4] 取消
echo.

set /p choice="请输入选项 [1-4]: "

if "%choice%"=="1" goto :scoop
if "%choice%"=="2" goto :choco
if "%choice%"=="3" goto :manual
if "%choice%"=="4" goto :end

echo 无效选项，退出
goto :end

:scoop
echo.
echo === 使用Scoop安装 ===
echo.

REM 检查Scoop是否安装
where scoop >nul 2>&1
if %errorlevel% neq 0 (
    echo Scoop未安装，正在安装Scoop...
    echo 需要管理员权限，请允许...
    powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    powershell -Command "irm get.scoop.sh | iex"
    
    if %errorlevel% neq 0 (
        echo Scoop安装失败
        goto :manual
    )
)

echo 正在安装FFmpeg...
call scoop install ffmpeg

if %errorlevel% == 0 (
    echo.
    echo ✓ FFmpeg安装成功！
    ffmpeg -version | findstr "ffmpeg version"
) else (
    echo ✗ FFmpeg安装失败
)
goto :end

:choco
echo.
echo === 使用Chocolatey安装 ===
echo.

REM 检查Chocolatey是否安装
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo Chocolatey未安装
    echo 请访问 https://chocolatey.org/install 安装Chocolatey
    echo 或选择其他安装方式
    pause
    goto :end
)

echo 正在安装FFmpeg...
choco install ffmpeg -y

if %errorlevel% == 0 (
    echo.
    echo ✓ FFmpeg安装成功！
    refreshenv
    ffmpeg -version | findstr "ffmpeg version"
) else (
    echo ✗ FFmpeg安装失败
)
goto :end

:manual
echo.
echo === 手动安装指南 ===
echo.
echo 1. 访问: https://github.com/BtbN/FFmpeg-Builds/releases
echo 2. 下载: ffmpeg-master-latest-win64-gpl.zip
echo 3. 解压到任意目录（如 C:\ffmpeg）
echo 4. 将 bin 目录添加到系统PATH环境变量
echo.
echo 详细步骤：
echo   - 右键"此电脑" → 属性 → 高级系统设置
echo   - 环境变量 → 系统变量 → Path → 编辑
echo   - 新建 → 输入FFmpeg的bin目录路径
echo   - 确定保存
echo.
echo 是否打开下载页面？[Y/N]
set /p open="请选择: "

if /i "%open%"=="Y" (
    start https://github.com/BtbN/FFmpeg-Builds/releases
)
goto :end

:end
echo.
echo ============================================
echo 安装完成后，请重启命令行和后端服务
echo ============================================
pause
