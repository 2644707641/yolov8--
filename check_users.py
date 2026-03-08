import os
from supabase import create_client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("错误: 未找到Supabase配置")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {SUPABASE_KEY}")
    exit(1)

print(f"连接到Supabase: {SUPABASE_URL}")

try:
    # 创建Supabase客户端
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 查询用户表（Supabase Auth的用户信息在auth.users表中）
    print("\n正在查询用户信息...")

    # 方法1: 使用Supabase的Auth API获取用户列表
    # 注意：需要service_role权限才能查看所有用户
    try:
        # 使用Supabase的Auth API
        from supabase import Client
        response = supabase.auth.admin.list_users()

        if hasattr(response, 'users'):
            users = response.users
            print(f"找到 {len(users)} 个用户:")
            print("-" * 80)
            for i, user in enumerate(users, 1):
                print(f"用户 {i}:")
                print(f"  ID: {user.id}")
                print(f"  邮箱: {user.email}")
                print(f"  创建时间: {user.created_at}")
                print(f"  最后登录: {user.last_sign_in_at}")
                print(f"  邮箱已验证: {user.email_confirmed_at is not None}")
                print()
        else:
            print("无法获取用户列表，尝试其他方法...")

    except Exception as auth_error:
        print(f"Auth API错误: {auth_error}")

    # 方法2: 直接查询数据库表（如果权限允许）
    try:
        print("\n尝试查询数据库表...")
        # 查询auth.users表
        response = supabase.table("auth.users").select("*").execute()

        if hasattr(response, 'data') and response.data:
            users = response.data
            print(f"从数据库找到 {len(users)} 个用户:")
            print("-" * 80)
            for i, user in enumerate(users, 1):
                print(f"用户 {i}:")
                print(f"  ID: {user.get('id')}")
                print(f"  邮箱: {user.get('email')}")
                print(f"  创建时间: {user.get('created_at')}")
                print(f"  最后登录: {user.get('last_sign_in_at')}")
                print(f"  邮箱已验证: {user.get('email_confirmed_at') is not None}")
                print()
        else:
            print("无法从数据库获取用户信息")

    except Exception as db_error:
        print(f"数据库查询错误: {db_error}")

    # 方法3: 检查是否有其他相关表
    try:
        print("\n检查其他相关表...")
        tables_to_check = ["users", "profiles", "user_profiles"]

        for table_name in tables_to_check:
            try:
                response = supabase.table(table_name).select("count").execute()
                print(f"表 '{table_name}' 存在")
            except:
                print(f"表 '{table_name}' 不存在或无法访问")

    except Exception as table_error:
        print(f"表检查错误: {table_error}")

except Exception as e:
    print(f"连接Supabase失败: {e}")
    print("请检查:")
    print("1. Supabase URL和Key是否正确")
    print("2. 网络连接是否正常")
    print("3. Supabase项目是否正常运行")
