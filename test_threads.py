import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.environ.get("THREADS_ACCESS_TOKEN")
print("Token:", access_token[:15], "...")

url = "https://graph.threads.net/v1.0/threads_search"
params = {
    "q": "sekolah",
    "access_token": access_token,
    "search_type": "TOP", 
    "limit": 5
}

try:
    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Exception:", e)
