import requests

BASE_URL = "http://localhost:8001/api"

print("测试系统设置API...")

response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
print(f"✅ 登录状态: {response.status_code}")
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("\n1. 测试获取公开设置:")
response = requests.get(f"{BASE_URL}/settings/public")
print(f"   状态: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   系统名称: {data['system_name']}")
    print(f"   系统简介: {data['system_intro']}")
    print(f"   Logo: {data['system_logo']}")
    print(f"   背景: {data['login_background']}")
    print(f"   版权: {data['copyright']}")

print("\n2. 测试获取所有设置(需要管理员权限):")
response = requests.get(f"{BASE_URL}/settings/all", headers=headers)
print(f"   状态: {response.status_code}")
if response.status_code == 200:
    settings = response.json()
    print(f"   设置数量: {len(settings)}")
    for s in settings:
        print(f"   - {s['setting_key']}: {s['setting_value']}")

print("\n✅ 系统设置API测试完成!")
