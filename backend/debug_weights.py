"""
权重管理调试脚本
用于诊断权重上传和显示问题
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def main():
    print("🔍 开始诊断权重管理系统...")
    print(f"📡 Supabase URL: {SUPABASE_URL}")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ 错误: 未找到 Supabase 配置")
        print("   请检查 .env 文件")
        return

    # 创建 Supabase 客户端
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase 客户端创建成功\n")

    # 查询所有权重记录
    print("📊 查询所有权重记录...")
    try:
        response = supabase.table("model_weights").select("*").order(
            "created_at", desc=True
        ).execute()
        weights = response.data

        print(f"✅ 找到 {len(weights)} 条权重记录\n")

        if len(weights) == 0:
            print("⚠️  数据库中没有权重记录")
            print("   可能原因:")
            print("   1. 用户还没有上传过权重")
            print("   2. 权重记录被意外删除")
            print("   3. RLS 策略阻止了查询（使用 Service Role Key 应该可以查看所有数据）")
        else:
            print("权重记录详情:")
            print("-" * 80)
            for idx, weight in enumerate(weights, 1):
                print(f"\n{idx}. 权重 ID: {weight.get('id')}")
                print(f"   用户 ID: {weight.get('user_id')}")
                print(f"   名称: {weight.get('name')}")
                print(f"   文件路径: {weight.get('file_path')}")
                print(f"   文件大小: {weight.get('file_size')} bytes")
                print(f"   是否活跃: {weight.get('is_active')}")
                print(f"   描述: {weight.get('description') or '(无)'}")
                print(f"   创建时间: {weight.get('created_at')}")
                print(f"   更新时间: {weight.get('updated_at')}")

        print("\n" + "=" * 80)

        # 按用户分组统计
        user_weights = {}
        for weight in weights:
            user_id = weight.get("user_id")
            if user_id not in user_weights:
                user_weights[user_id] = []
            user_weights[user_id].append(weight)

        print("\n📈 按用户统计")
        print("-" * 80)
        for user_id, user_weight_list in user_weights.items():
            print(f"\n用户 {user_id}:")
            print(f"  - 总权重数: {len(user_weight_list)}")
            active_weights = [w for w in user_weight_list if w.get("is_active")]
            print(f"  - 活跃权重数: {len(active_weights)}")
            if len(active_weights) > 1:
                print("  ⚠️  警告: 该用户有多个活跃权重（应该只有一个）")

            print("  - 权重列表:")
            for w in user_weight_list:
                status = "🟢 活跃" if w.get("is_active") else "⚪ 非活跃"
                print(f"    {status} {w.get('name')} ({w.get('created_at')})")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"❌ 查询失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return

    # 检查存储桶
    print("\n📦 检查存储桶...")
    try:
        buckets = supabase.storage.list_buckets()
        print(f"✅ 找到 {len(buckets)} 个存储桶")

        model_weights_bucket = None
        for bucket in buckets:
            bucket_name = bucket.get("name") if isinstance(bucket, dict) else bucket.name
            print(f"   - {bucket_name}")
            if bucket_name == "model-weights":
                model_weights_bucket = bucket

        if not model_weights_bucket:
            print("\n⚠️  警告: 未找到 'model-weights' 存储桶")
            print("   请确认已创建并配置正确")
        else:
            print("\n✅ 找到 'model-weights' 存储桶")

            # 列出存储桶中的文件
            print("\n📁 存储桶中的文件")
            try:
                files = supabase.storage.from_("model-weights").list()
                if not files:
                    print("   (空)")
                else:
                    for file in files:
                        file_name = file.get("name") if isinstance(file, dict) else file.name
                        print(f"   - {file_name}")

                        # 如果是文件夹，列出其中的文件
                        try:
                            subfiles = supabase.storage.from_("model-weights").list(file_name)
                            for subfile in subfiles:
                                subfile_name = (
                                    subfile.get("name")
                                    if isinstance(subfile, dict)
                                    else subfile.name
                                )
                                print(f"     └─ {subfile_name}")
                        except Exception:
                            pass
            except Exception as e:
                print(f"   ❌ 无法列出文件: {e}")

    except Exception as e:
        print(f"❌ 检查存储桶失败: {e}")

    print("\n" + "=" * 80)
    print("🎯 诊断完成")
    print("\n如果发现问题，请检查：")
    print("1. Supabase 数据库表 'model_weights' 是否正确创建")
    print("2. RLS 策略是否正确配置")
    print("3. 存储桶 'model-weights' 是否存在")
    print("4. 后端日志中是否有错误信息")
    print("5. 前端浏览器控制台是否有错误")


if __name__ == "__main__":
    main()