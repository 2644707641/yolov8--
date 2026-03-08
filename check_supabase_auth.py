import os
import requests
import json
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

# 使用Supabase的Auth REST API
# 参考: https://supabase.com/docs/reference/javascript/auth-admin-listusers

def list_users_via_rest():
    """通过REST API获取用户列表"""
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    # 尝试获取用户列表
    try:
        # 方法1: 使用Supabase的Auth Admin API
        auth_url = f"{SUPABASE_URL}/auth/v1/admin/users"
        print(f"\n尝试访问: {auth_url}")

        response = requests.get(auth_url, headers=headers)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            users = response.json()
            print(f"成功获取用户数据")
            return users
        else:
            print(f"API响应: {response.text}")
            return None

    except Exception as e:
        print(f"REST API错误: {e}")
        return None

def check_tables():
    """检查数据库中的表"""
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY
    }

    # 获取数据库表信息
    try:
        # 使用PostgREST API获取表信息
        tables_url = f"{SUPABASE_URL}/rest/v1/"
        response = requests.get(tables_url, headers=headers)

        if response.status_code == 200:
            print("\n数据库表信息:")
            print(response.text[:500])  # 只显示前500字符
        else:
            print(f"获取表信息失败: {response.status_code}")

    except Exception as e:
        print(f"获取表信息错误: {e}")

def test_auth():
    """测试认证功能"""
    print("\n测试用户登录...")

    # 测试用户登录
    test_email = "xuwang23333@gmail.com"
    test_password = "123456"

    auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "email": test_email,
        "password": test_password
    }

    try:
        response = requests.post(auth_url, headers=headers, json=data)
        print(f"登录测试状态码: {response.status_code}")
        print(f"登录测试响应: {response.text[:200]}")

        if response.status_code == 200:
            print("登录成功!")
            user_data = response.json()
            print(f"用户ID: {user_data.get('user', {}).get('id')}")
            print(f"用户邮箱: {user_data.get('user', {}).get('email')}")
        elif response.status_code == 400:
            print("登录失败: 邮箱或密码不正确")
        else:
            print(f"登录失败: {response.text}")

    except Exception as e:
        print(f"登录测试错误: {e}")

# 执行检查
print("=" * 80)
print("Supabase用户信息检查")
print("=" * 80)

# 1. 检查表结构
check_tables()

# 2. 尝试获取用户列表
print("\n" + "=" * 80)
print("尝试获取用户列表")
print("=" * 80)
users = list_users_via_rest()

if users:
    if isinstance(users, list):
        print(f"\n找到 {len(users)} 个用户:")
        for i, user in enumerate(users, 1):
            print(f"\n用户 {i}:")
            print(f"  ID: {user.get('id')}")
            print(f"  邮箱: {user.get('email')}")
            print(f"  创建时间: {user.get('created_at')}")
            print(f"  最后登录: {user.get('last_sign_in_at')}")
            print(f"  邮箱已验证: {user.get('email_confirmed_at') is not None}")
    else:
        print(f"用户数据格式: {type(users)}")
        print(f"用户数据: {json.dumps(users, indent=2, ensure_ascii=False)[:500]}...")
else:
    print("无法获取用户列表")

# 3. 测试登录
print("\n" + "=" * 80)
print("测试用户登录")
print("=" * 80)
test_auth()

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
