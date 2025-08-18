from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

def get_access_token():
    load_dotenv()
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    kite = KiteConnect(api_key=api_key)
    print("Login URL:", kite.login_url())
    print("\nAfter logging in, copy the request_token from the URL and paste it below as:")
    print('request_token = "PASTE_YOUR_NEW_TOKEN_HERE"')
    request_token = input("Paste your request_token here: ").strip()
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    print(f"\nYour new access_token is: {access_token}")
    # Optionally, update .env automatically
    update_env_file('KITE_ACCESS_TOKEN', access_token)
    print(".env file updated with new access token.")
    return access_token

def update_env_file(key, value):
    env_path = '.env'
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith(key + '='):
                    lines.append(f'{key}={value}\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'{key}={value}\n')
    with open(env_path, 'w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    get_access_token()
