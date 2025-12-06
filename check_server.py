import requests
import json

try:
    response = requests.get("http://localhost:8000/state")
    if response.status_code == 200:
        data = response.json()
        print("Server is UP.")
        print(f"Week: {data.get('week')}")
        print(f"Season: {data.get('season')}")
        print(f"Alliances: {data.get('alliances')}")
        print(f"Events: {data.get('events')}")
    else:
        print(f"Server returned {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Connection failed: {e}")
