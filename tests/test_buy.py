
import requests
import json

url = "http://localhost:8000/action"
payload = {
    "agent_id": "p1",
    "action_type": "buy_supplies",
    "parameters": {
        "item": "soap",
        "quantity": 10
    }
}

try:
    res = requests.post(url, json=payload)
    data = res.json()
    print("Status:", res.status_code)
    if "new_state" in data:
        print("Inventory:", data["new_state"]["inventory"])
        print("Balance:", data["new_state"]["balance"])
    else:
        print("Response:", json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)
