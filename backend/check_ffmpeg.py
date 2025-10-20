"""
检查FFmpeg是否已安装
"""

import subprocess
import sys

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout.decode()
            version_line = output.split('\n')[0]
            print(f"✓ FFmpeg已安装: {version_line}")
            print("\n视频将自动优化为流畅的H264格式！")
            return True
        else:
            print("✗ FFmpeg未正确安装")
            return False
            
    except FileNotFoundError:
        print("✗ FFmpeg未安装")
        print("\n=== 如何安装FFmpeg ===")
        print("\n方式1: 使用Scoop（推荐）")
        print("  1. 安装Scoop: https://scoop.sh/")
        print("  2. 运行: scoop install ffmpeg")
        print("\n方式2: 手动安装")
        print("  1. 下载: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("  2. 选择: ffmpeg-master-latest-win64-gpl.zip")
        print("  3. 解压到任意目录")
        print("  4. 将 bin 目录添加到系统PATH环境变量")
        print("\n方式3: 使用Chocolatey")
        print("  运行: choco install ffmpeg")
        print("\n安装后请重启命令行和后端服务")
        return False
        
    except Exception as e:
        print(f"✗ 检查FFmpeg时出错: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FFmpeg 安装检查")
    print("=" * 60)
    check_ffmpeg()
    print("=" * 60)
