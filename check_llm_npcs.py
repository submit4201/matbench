
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from tests.test_llm_npcs import test_llm_customer, test_llm_vendor, test_llm_event_manager

def main():
    print("Running manual checks...")
    try:
        if test_llm_customer():
            print("Customer test passed")
        else:
            print("Customer test failed")
    except Exception as e:
        print(f"Customer test raised exception: {e}")
        import traceback
        traceback.print_exc()

    try:
        if test_llm_vendor():
            print("Vendor test passed")
        else:
            print("Vendor test failed")
    except Exception as e:
        print(f"Vendor test raised exception: {e}")
        import traceback
        traceback.print_exc()

    try:
        if test_llm_event_manager():
            print("Event Manager test passed")
        else:
            print("Event Manager test failed")
    except Exception as e:
        print(f"Event Manager test raised exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
