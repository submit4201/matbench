import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing Imports...")
    from src.models.world import LaundromatState
    from src.models.financial import TransactionCategory
    from src.agents.base_agent import Action
    
    print("✅ Imports successful.")

    print("Testing Instantiation...")
    state = LaundromatState(id="test_p1", name="Test Laundromat")
    print(f"✅ State initialized: {state.name} (Reputation: {state.reputation})")
    
    print("Testing Logic (model_post_init)...")
    if len(state.machines) == 15:
        print("✅ Machines initialized via post_init.")
    else:
        print(f"❌ Machines init failed: {len(state.machines)}")

    print("Testing Serialization...")
    dump = state.model_dump(mode='json')
    if dump['id'] == "test_p1" and isinstance(dump['machines'], list):
         print("✅ Serialization successful.")
    else:
         print(f"❌ Serialization check failed: {dump.keys()}")

    print("Testing Import Proxy...")
    from src.world.laundromat import LaundromatState as ProxyState
    proxy = ProxyState(id="proxy_1", name="Proxy")
    if isinstance(proxy, LaundromatState):
        print("✅ Proxy import works.")
    else:
        print("❌ Proxy import failed identity check.")

except Exception as e:
    print(f"❌ Verification Failed: {e}")
    sys.exit(1)
