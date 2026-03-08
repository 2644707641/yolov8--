import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("错误: 未找到Supabase配置")
    exit(1)

print(f"Supabase URL: {SUPABASE_URL}")
print(f"使用Service Role Key: {SUPABASE_KEY[:20]}...")

# 设置请求头
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# 获取用户列表
url = f"{SUPABASE_URL}/auth/v1/admin/users"
print(f"\n请求URL: {url}")

try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        users = data.get("users", [])

        print(f"\n找到 {len(users)} 个用户:")
        print("=" * 60)

        for i, user in enumerate(users, 1):
            print(f"用户 {i}:")
            print(f"  ID: {user.get('id')}")
            print(f"  邮箱: {user.get('email')}")
            print(f"  创建时间: {user.get('created_at')}")
            print(f"  最后登录: {user.get('last_sign_in_at')}")
            print(f"  邮箱已验证: {user.get('email_confirmed_at') is not None}")
            print()

        print("=" * 60)

        # 检查是否有 xuwang23333@gmail.com 这个用户
        target_email = "xuwang23333@gmail.com"
        found = False
        for user in users:
            if user.get("email") == target_email:
                found = True
                print(f"\n找到目标用户: {target_email}")
                print(f"用户ID: {user.get('id')}")
                print(f"邮箱已验证: {user.get('email_confirmed_at') is not None}")
                break

        if not found:
            print(f"\n数据库中不存在用户: {target_email}")
            print("可能的原因:")
            print("1. 该用户尚未注册")
            print("2. 注册时使用了不同的邮箱")
            print("3. 用户已被删除")

    else:
        print(f"错误: {response.status_code}")
        print(f"响应: {response.text}")

except Exception as e:
    print(f"请求失败: {e}")
