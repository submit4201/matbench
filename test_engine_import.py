import sys
import os
sys.path.append(os.getcwd())

try:
    print("Importing src.engine.enhanced_engine...")
    from src.engine.enhanced_engine import EnhancedGameEngine
    print(f"Class: {EnhancedGameEngine}")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
