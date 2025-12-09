import sys
import os
sys.path.append(os.getcwd())

try:
    print("Importing src.engine.core.calendar...")
    import src.engine.core.calendar
    print(f"Module: {src.engine.core.calendar}")
    print(f"File: {src.engine.core.calendar.__file__}")
    
    print("Importing CalendarManager...")
    from src.engine.core.calendar import CalendarManager
    print(f"Class: {CalendarManager}")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
