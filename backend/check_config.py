#!/usr/bin/env python3
"""
Supabase 配置诊断脚本
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]

# 加载配置文件
load_dotenv(BASE_DIR / ".env", override=False)

print("=" * 60)
print("Supabase 配置检查")
print("=" * 60)

print("\n【前端配置（来自根目录 .env）】")
frontend_url = os.getenv("VITE_SUPABASE_URL")
frontend_key = os.getenv("VITE_SUPABASE_ANON_KEY")

if frontend_url:
    print(f"✅ VITE_SUPABASE_URL: {frontend_url}")
else:
    print("❌ VITE_SUPABASE_URL: 未配置")

if frontend_key:
    print(f"✅ VITE_SUPABASE_ANON_KEY: {frontend_key[:20]}...")
else:
    print("❌ VITE_SUPABASE_ANON_KEY: 未配置")

print("\n【后端配置（来自 .env）】")
backend_url = os.getenv("SUPABASE_URL")
backend_key = os.getenv("SUPABASE_KEY")

if backend_url:
    print(f"✅ SUPABASE_URL: {backend_url}")
else:
    print("❌ SUPABASE_URL: 未配置")

if backend_key:
    print(f"✅ SUPABASE_KEY: {backend_key[:20]}...")
    if backend_key.startswith("eyJhbGci"):
        print("  ℹ️  看起来是 JWT 格式的密钥")
    print("\n⚠️ 重要提示：")
    print("  后端必须使用 SERVICE ROLE KEY，不能使用 ANON KEY")
    print("  请在 Supabase 控制台 Settings > API 中获取 service_role key")
else:
    print("❌ SUPABASE_KEY: 未配置")

print("\n【一致性检查】")
if frontend_url and backend_url:
    if frontend_url == backend_url:
        print(f"✅ 前后端使用同一 Supabase 项目: {frontend_url}")
    else:
        print("❌ 警告：前后端使用不同的 Supabase 项目")
        print(f"  前端: {frontend_url}")
        print(f"  后端: {backend_url}")
else:
    print("⚠️ 无法检查：URL 未完全配置")

print("\n" + "=" * 60)
print("配置建议")
print("=" * 60)
print(
    """
1. 确保 .env 文件存在并包含：
   SUPABASE_URL=https://你的项目.supabase.co
   SUPABASE_KEY=你的_service_role_密钥

2. 后端必须使用 SERVICE ROLE KEY，获取方式：
   Supabase 控制台 > Settings > API > Project API keys > service_role

3. 前后端必须使用同一 Supabase 项目的配置
4. 重启后端服务使配置生效：
   python backend/main.py
"""
)