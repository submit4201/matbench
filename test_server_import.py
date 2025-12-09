import sys
import os
sys.path.append(os.getcwd())

try:
    print("Attempting to import src.server...")
    from src.server import app
    print("Import successful")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
