"""
上传默认权重到 Supabase Storage 的辅助脚本

使用方法:
    python upload_default_weight.py <权重文件路径>

示例:
    python upload_default_weight.py ../best.pt
    python upload_default_weight.py D:/models/best.pt
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def upload_default_weight(weight_file_path: str | Path) -> bool:
    """
    上传默认权重文件到 Supabase Storage

    Args:
        weight_file_path: 权重文件的本地路径

    Returns:
        上传是否成功
    """
    # 检查环境变量
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ 错误: 未配置 SUPABASE_URL 或 SUPABASE_KEY")
        print("请在 .env 文件中配置这些环境变量")
        return False

    # 检查文件是否存在
    weight_path = Path(weight_file_path)
    if not weight_path.exists():
        print(f"❌ 错误: 文件不存在: {weight_path}")
        return False

    # 检查文件扩展名
    if weight_path.suffix not in [".pt", ".pth"]:
        print(f"❌ 错误: 不支持的文件格式: {weight_path.suffix}")
        print("仅支持 .pt 或 .pth 格式")
        return False

    # 获取配置
    bucket_name = os.getenv("MODEL_WEIGHTS_BUCKET", "model-weights")
    storage_path = os.getenv("DEFAULT_MODEL_PATH", "default/best.pt")
    model_name = os.getenv("DEFAULT_MODEL_NAME", "默认停车位检测模型")

    print(f"\n📋 上传信息:")
    print(f"   - 本地文件: {weight_path.absolute()}")
    print(f"   - 文件大小: {weight_path.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"   - 存储桶: {bucket_name}")
    print(f"   - 存储路径: {storage_path}")
    print(f"   - 模型名称: {model_name}")

    try:
        # 创建 Supabase 客户端
        print("\n🔗 连接到 Supabase...")
        supabase = create_client(supabase_url, supabase_key)

        # 读取文件
        print("📁 读取权重文件...")
        with open(weight_path, "rb") as f:
            file_content = f.read()

        # 检查存储桶是否存在
        print(f"🗂️  检查存储桶 '{bucket_name}'...")
        try:
            buckets = supabase.storage.list_buckets()
            bucket_exists = any(b["name"] == bucket_name for b in buckets)
            if not bucket_exists:
                print(f"⚠️  存储桶 '{bucket_name}' 不存在，尝试创建...")
                supabase.storage.create_bucket(
                    bucket_name, options={"public": False}
                )
                print(f"✅ 存储桶 '{bucket_name}' 创建成功")
        except Exception as e:
            print(f"⚠️  检查存储桶时出现警告: {e}")
            print("   继续尝试上传...")

        # 检查文件是否已存在
        print(f"🔍 检查文件是否已存在...")
        try:
            existing_files = supabase.storage.from_(bucket_name).list(
                path="default"
            )
            file_exists = any(f["name"] == storage_path.split("/")[-1] for f in existing_files)
            
            if file_exists:
                print(f"⚠️  文件 '{storage_path}' 已存在")
                response = input("   是否覆盖？(y/n): ")
                if response.lower() != "y":
                    print("❌ 取消上传")
                    return False

                # 删除旧文件
                print("🗑️  删除旧文件...")
                supabase.storage.from_(bucket_name).remove([storage_path])
        except Exception as e:
            print(f"ℹ️  检查现有文件时出现提示: {e}")

        # 上传文件
        print(f"⬆️  上传权重文件到 Supabase...")
        supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": "application/octet-stream"},
        )

        print(f"\n✅ 默认权重上传成功!")
        print(f"\n📝 配置信息:")
        print(f"   请确保 .env 文件中包含以下配置:")
        print(f"   DEFAULT_MODEL_PATH={storage_path}")
        print(f"   DEFAULT_MODEL_NAME={model_name}")
        print(f"\n🔄 下次使用默认权重时，系统会自动从 Supabase 下载")

        return True

    except Exception as e:
        print(f"\n❌ 上传失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("📦 YOLOv8 默认权重上传工具")
    print("=" * 60)

    # 检查命令行参数
    if len(sys.argv) < 2:
        print("\n❌ 错误: 请提供权重文件路径")
        print("\n使用方法:")
        print("    python upload_default_weight.py <权重文件路径>")
        print("\n示例:")
        print("    python upload_default_weight.py ../best.pt")
        print("    python upload_default_weight.py D:/models/best.pt")
        sys.exit(1)

    weight_file_path = sys.argv[1]

    # 上传权重
    success = upload_default_weight(weight_file_path)

    if success:
        print("\n✨ 完成！现在所有新用户都可以使用这个默认权重了")
        sys.exit(0)
    else:
        print("\n❌ 上传失败，请检查错误信息并重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
