import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

def test_auth():
    # 1. Register
    print("--- Registering ---")
    reg_data = {
        "name": "Joao Silva",
        "email": "joao@email.com",
        "password": "123456"
    }
    try:
        resp = requests.post(f"{BASE_URL}/register", json=reg_data)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        if resp.status_code not in [200, 201]:
            print("Register failed (maybe already exists), trying login...")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Login
    print("\n--- Logging in ---")
    login_data = {
        "email": "joao@email.com",
        "password": "123456"
    }
    resp = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    token = data.get("access_token")
    print(f"Token: {token[:20]}...")

    # 3. Me
    print("\n--- Getting Me ---")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    test_auth()
