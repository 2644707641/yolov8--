# -*- coding: utf-8 -*-
"""Comprehensive Supabase DB connection test"""
import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "detection-files")
MODEL_WEIGHTS_BUCKET = os.getenv("MODEL_WEIGHTS_BUCKET", "model-weights")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[FAIL] No Supabase config found (SUPABASE_URL / SUPABASE_KEY)")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("Supabase DB Comprehensive Connection Test")
print("URL: " + SUPABASE_URL)
print("=" * 60)

# --- 1. Client init ---
print("\n[1] Client initialization...")
try:
    print("[OK] Client created successfully")
except Exception as e:
    print("[FAIL] Client creation failed: " + str(e))
    sys.exit(1)

# --- 2. Storage buckets ---
print("\n[2] Storage buckets...")
try:
    buckets = supabase.storage.list_buckets()
    bucket_names = []
    for b in buckets:
        name = b.get("name") if isinstance(b, dict) else b.name
        bucket_names.append(name)
    print("    Found %d bucket(s):" % len(buckets))
    for name in bucket_names:
        print("    - " + name)
except Exception as e:
    print("    [FAIL] Cannot list buckets: " + str(e))
    bucket_names = []

for bucket_name in [SUPABASE_BUCKET, MODEL_WEIGHTS_BUCKET]:
    if bucket_name in bucket_names:
        print("    [OK] Bucket '%s' exists" % bucket_name)
        try:
            files = supabase.storage.from_(bucket_name).list()
            print("        Files: %d" % len(files))
        except Exception as e:
            print("        [WARN] Cannot list files: " + str(e))
    else:
        print("    [WARN] Bucket '%s' does NOT exist!" % bucket_name)

# --- 3. Database tables ---
print("\n[3] Database tables...")
tables_to_check = [
    "detection_history",
    "detection_history_archive",
    "model_weights",
    "model_weights_archive",
]

for table_name in tables_to_check:
    try:
        result = supabase.table(table_name).select("*", count="exact").limit(1).execute()
        count = result.count if hasattr(result, 'count') else (len(result.data) if result.data else 0)
        print("    [OK] table '%s' - queryable (sample: %d)" % (table_name, count))
        try:
            count_result = supabase.table(table_name).select("*", count="exact").limit(0).execute()
            total = count_result.count if hasattr(count_result, 'count') else "?"
            print("        Total rows: %s" % str(total))
        except:
            pass
    except Exception as e:
        err_msg = str(e)
        if "does not exist" in err_msg.lower() or "404" in err_msg:
            print("    [FAIL] table '%s' does NOT exist!" % table_name)
        elif "42P01" in err_msg:
            print("    [FAIL] table '%s' does NOT exist (PostgreSQL error)!" % table_name)
        else:
            print("    [WARN] table '%s' - %s" % (table_name, err_msg[:150]))

# --- 4. RLS / permissions ---
print("\n[4] RLS / permissions check...")
try:
    result = supabase.table("detection_history").select("*", count="exact").limit(0).execute()
    print("    [OK] service_role can access detection_history (count: %d)" % result.count)
except Exception as e:
    print("    [FAIL] service_role cannot access detection_history: " + str(e))

try:
    result = supabase.table("model_weights").select("*", count="exact").limit(0).execute()
    print("    [OK] service_role can access model_weights (count: %d)" % result.count)
except Exception as e:
    print("    [FAIL] service_role cannot access model_weights: " + str(e))

# --- 5. Auth ---
print("\n[5] Auth check...")
try:
    import requests
    auth_url = SUPABASE_URL + "/auth/v1/admin/users"
    headers = {
        "Authorization": "Bearer " + SUPABASE_KEY,
        "apikey": SUPABASE_KEY,
    }
    resp = requests.get(auth_url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            users = data
        else:
            users = data.get("users", [])
        print("    [OK] Admin API available, total users: %d" % len(users))
        for u in users[:5]:
            print("        User: %s | ID: %s..." % (u.get('email', '?'), u.get('id', '?')[:20]))
    else:
        print("    [FAIL] Admin API returned: %d" % resp.status_code)
except Exception as e:
    print("    [FAIL] Auth check failed: " + str(e))

# --- 6. Storage file operations (read/write test) ---
print("\n[6] Storage read/write test...")
test_bucket = SUPABASE_BUCKET
test_path = "__test_connection__.txt"
test_content = b"connection test - safe to delete"
try:
    supabase.storage.from_(test_bucket).upload(
        test_path,
        test_content,
        {"upsert": "true"}
    )
    print("    [OK] Uploaded test file to '%s/%s'" % (test_bucket, test_path))
    # Now delete it
    supabase.storage.from_(test_bucket).remove([test_path])
    print("    [OK] Removed test file")
except Exception as e:
    print("    [WARN] Storage read/write test: " + str(e)[:150])

# --- 7. DB write test (soft) ---
print("\n[7] DB write test (insert then delete)...")
try:
    insert_data = {
        "user_id": "test-connection-check",
        "name": "__test__",
        "file_path": "__test__",
        "file_size": 0,
    }
    result = supabase.table("model_weights").insert(insert_data).execute()
    if result.data:
        test_id = result.data[0].get("id") or result.data[0].get("weight_id")
        print("    [OK] Inserted test row into model_weights (id: %s)" % str(test_id))
        # Clean up
        supabase.table("model_weights").delete().eq("id", test_id).execute()
        print("    [OK] Deleted test row")
    else:
        print("    [WARN] Insert returned no data")
except Exception as e:
    print("    [WARN] DB write test: " + str(e)[:150])

# --- Summary ---
print("\n" + "=" * 60)
print("[DONE] Database connection comprehensive test completed")
print("=" * 60)
