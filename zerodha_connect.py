from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")

kite = KiteConnect(api_key=api_key)
print("Login URL:", kite.login_url())
print("\nAfter logging in, copy the request_token from the URL and paste it below as:")
print('request_token = "PASTE_YOUR_NEW_TOKEN_HERE"')

# Uncomment and use the following lines after pasting your request_token:
# request_token = "YOUR_NEW_TOKEN"
# data = kite.generate_session(request_token, api_secret=api_secret)
# kite.set_access_token(data["access_token"])
#
# # Fetch and print portfolio holdings
# holdings = kite.holdings()
# for holding in holdings:
#     print(holding)
