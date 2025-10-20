"""
视频修复工具
如果OpenCV生成的视频有问题，可以使用FFmpeg重新编码
"""

import subprocess
import os
from pathlib import Path

def reencode_video_with_ffmpeg(input_path: Path, output_path: Path = None) -> bool:
    """
    使用FFmpeg重新编码视频，提高兼容性
    
    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径（如果为None，则覆盖原文件）
    
    Returns:
        bool: 是否成功
    """
    if output_path is None:
        temp_path = input_path.with_suffix('.temp.mp4')
        output_path = input_path
        use_temp = True
    else:
        use_temp = False
        temp_path = output_path
    
    try:
        # FFmpeg命令：重新编码为H.264，质量较高
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',        # 使用H.264编码
            '-preset', 'medium',       # 编码速度（fast/medium/slow）
            '-crf', '23',             # 质量（18-28，越小质量越好）
            '-pix_fmt', 'yuv420p',    # 像素格式（兼容性最好）
            '-y',                     # 覆盖输出文件
            str(temp_path)
        ]
        
        print(f"[INFO] 使用FFmpeg重新编码视频...")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            if use_temp:
                # 替换原文件
                if output_path.exists():
                    output_path.unlink()
                temp_path.rename(output_path)
            
            print(f"[INFO] 视频重新编码成功")
            return True
        else:
            print(f"[ERROR] FFmpeg编码失败: {result.stderr.decode()}")
            return False
            
    except FileNotFoundError:
        print(f"[ERROR] FFmpeg未安装，请先安装FFmpeg")
        print(f"[INFO] Windows: 下载 https://ffmpeg.org/download.html")
        print(f"[INFO] 或使用 scoop install ffmpeg")
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] FFmpeg编码超时")
        return False
    except Exception as e:
        print(f"[ERROR] 重新编码失败: {e}")
        return False
    finally:
        # 清理临时文件
        if use_temp and temp_path.exists() and temp_path != output_path:
            temp_path.unlink()


def check_ffmpeg_available() -> bool:
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


if __name__ == "__main__":
    # 测试
    print("检查FFmpeg是否可用...")
    if check_ffmpeg_available():
        print("✓ FFmpeg已安装")
    else:
        print("✗ FFmpeg未安装")
