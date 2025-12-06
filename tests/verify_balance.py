import requests
import time
import subprocess
import sys

def verify_balance():
    # Start server in background on port 8001
    server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.server:app", "--port", "8001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Server started on 8001...")
    time.sleep(5) # Wait for startup

    try:
        res = requests.get("http://localhost:8001/state")
        if res.status_code == 200:
            data = res.json()
            balance = data["laundromats"]["p1"]["balance"]
            print(f"Initial Balance: {balance}")
            if balance == 100.0:
                print("PASS: Balance is 100.0")
            else:
                print(f"FAIL: Balance is {balance}, expected 100.0")
        else:
            print(f"FAIL: Server returned {res.status_code}")
    except Exception as e:
        print(f"FAIL: {e}")
    finally:
        server_process.terminate()
        print("Server stopped.")

if __name__ == "__main__":
    verify_balance()
