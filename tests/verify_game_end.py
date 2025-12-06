import requests
import time
import subprocess
import sys

def verify_game_end():
    # Start server in background on port 8002
    server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.server:app", "--port", "8002"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Server started on 8002...")
    time.sleep(5) # Wait for startup

    try:
        # Fast forward to week 24
        print("Fast forwarding to week 24...")
        for _ in range(24):
            requests.post("http://localhost:8002/next_turn")
        
        res = requests.get("http://localhost:8002/state")
        if res.status_code == 200:
            data = res.json()
            week = data["week"]
            print(f"Current Week: {week}")
            if week >= 24:
                print("PASS: Week reached 24")
            else:
                print(f"FAIL: Week is {week}, expected >= 24")
        else:
            print(f"FAIL: Server returned {res.status_code}")
    except Exception as e:
        print(f"FAIL: {e}")
    finally:
        server_process.terminate()
        print("Server stopped.")

if __name__ == "__main__":
    verify_game_end()
