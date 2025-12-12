import sys
import os
sys.path.append(os.getcwd())

from src.models.hierarchy import WorldState, AgentState, LocationState
from src.models.world import LaundromatState
from src.engine.game_engine import GameEngine
import logging

from src.engine.actions.registry import ActionRegistry

def verify_actions():
    # Force GameEngine logs to stdout
    engine_logger = logging.getLogger("GameEngine")
    engine_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    engine_logger.addHandler(handler)
    
    print(f"DEBUG: Registry Keys: {list(ActionRegistry._handlers.keys())}")
    
    # Setup
    p1 = LaundromatState(id="p1", name="Test Laundromat", price=5.0)
    print(f"DEBUG: Initial Machines: {len(p1.machines)}")
    p1.balance = 5000.0 # Seed money
    
    states = {"p1": p1}
    engine = GameEngine(["p1"])
    engine.states = states

    # Manual Test
    handler = ActionRegistry.get_handler("SET_PRICE")
    print(f"DEBUG: Handler for SET_PRICE: {handler}")
    if handler:
         print("DEBUG: Calling handler manually...")
         handler(p1, {"amount": 8.0}, 1)
         
    print("Verifying Phase 2 Actions...")
    
    # 1. Test SET_PRICE
    print("\n--- Testing SET_PRICE ---")
    action_price = {"type": "SET_PRICE", "amount": 7.5}
    # Direct apply for verification
    success = engine._apply_action(p1, action_price)
    
    if success and p1.price == 7.5:
        print("✓ SET_PRICE Success: State updated to 7.5")
    else:
        print(f"✗ SET_PRICE Failed: Price is {p1.price}, expected 7.5")
        
    events = engine.event_repo.get_history("p1")
    if any(isinstance(e, PriceSetEvent) for e in events):
        print("✓ PriceSetEvent found in repo.")
    else:
        print("✗ PriceSetEvent NOT found.")

    # 2. Test BUY_SUPPLIES
    print("\n--- Testing BUY_SUPPLIES ---")
    # Buy 10 soap @ $2.0 = $20
    action_buy = {"type": "BUY_SUPPLIES", "item": "detergent", "quantity": 10, "cost": 20.0}
    initial_inv = p1.inventory.get("detergent", 0)
    initial_bal = p1.balance
    
    success = engine._apply_action(p1, action_buy)
    
    expected_bal = initial_bal - 20.0
    expected_inv = initial_inv + 10
    
    if success and abs(p1.balance - expected_bal) < 0.01 and p1.inventory["detergent"] == expected_inv:
        print(f"✓ BUY_SUPPLIES Success: Bal {p1.balance}, Inv {p1.inventory['detergent']}")
    else:
        print(f"✗ BUY_SUPPLIES Failed: Bal {p1.balance} (exp {expected_bal}), Inv {p1.inventory.get('detergent')} (exp {expected_inv})")

    # 3. Test UPGRADE_MACHINE
    print("\n--- Testing UPGRADE_MACHINE ---")
    action_upgrade = {"type": "UPGRADE_MACHINE"}
    initial_machines = len(p1.machines)
    
    success = engine._apply_action(p1, action_upgrade)
    
    if success and len(p1.machines) == initial_machines + 1:
        print("✓ UPGRADE_MACHINE Success: Machine count increased.")
        print(f"  New Machine: {p1.machines[-1]}")
    else:
        print(f"✗ UPGRADE_MACHINE Failed: Count {len(p1.machines)}")

    # 4. Test MARKETING_CAMPAIGN
    print("\n--- Testing MARKETING_CAMPAIGN ---")
    action_marketing = {"type": "MARKETING_CAMPAIGN", "cost": 100.0}
    initial_boost = p1.marketing_boost
    initial_bal = p1.balance
    
    success = engine._apply_action(p1, action_marketing)
    
    expected_bal = initial_bal - 100.0
    expected_boost = initial_boost + 1.0 # 100/100
    
    if success and abs(p1.balance - expected_bal) < 0.01 and abs(p1.marketing_boost - expected_boost) < 0.01:
        print(f"✓ MARKETING_CAMPAIGN Success: Bal {p1.balance}, Boost {p1.marketing_boost}")
    else:
        print(f"✗ MARKETING_CAMPAIGN Failed: Bal {p1.balance} (exp {expected_bal}), Boost {p1.marketing_boost} (exp {expected_boost})")

if __name__ == "__main__":
    verify_actions()
