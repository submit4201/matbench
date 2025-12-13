
import sys
import os
import traceback

# Add src to path
sys.path.append(os.getcwd())

try:
    from src.world.laundromat import LaundromatState
    from src.engine.actions.handlers import handle_hire_staff, handle_pay_bill, handle_resolve_dilemma
    from src.engine.projections.handlers.social import apply_dilemma_resolved
    from src.engine.finance import Bill
    from src.models.events.social import DilemmaResolved
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def run_tests():
    print("Starting Tests...")
    
    try:
        print("Test 1: Hire Staff Purity")
        test_hire_staff_purity()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

    try:
        print("\nTest 2: Pay Bill Validation")
        test_pay_bill_validation()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

    try:
        print("\nTest 3: Resolve Dilemma Effects")
        test_resolve_dilemma_effects()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

def test_hire_staff_purity():
    state = LaundromatState(id="agent1", name="Laundromat 1")
    state.balance = 1000.0
    payload = {"role": "cleaner"}
    
    events = handle_hire_staff(state, payload, week=1, context={})
    
    if len(events) != 2: raise Exception(f"Expected 2 events, got {len(events)}")
    if events[1].type != "STAFF_HIRED": raise Exception(f"Expected STAFF_HIRED, got {events[1].type}")
    if events[1].role != "cleaner": raise Exception(f"Expected cleaner, got {events[1].role}")
    if events[1].wage <= 0: raise Exception("Wage not set")

def test_pay_bill_validation():
    state = LaundromatState(id="agent1", name="Laundromat 1")
    state.balance = 1000.0
    
    bill = Bill(id="b1", name="Rent", amount=500.0, due_week=2, category="rent", recipient_id="landlord", generated_week=1)
    state.bills.append(bill)
    
    events = handle_pay_bill(state, {"bill_id": "b1"}, week=1, context={})
    if len(events) != 2: raise Exception(f"Expected 2 events, got {len(events)}")
    if events[1].type != "BILL_PAID": raise Exception(f"Expected BILL_PAID, got {events[1].type}")
    if events[1].amount_paid != 500.0: raise Exception(f"Expected 500.0, got {events[1].amount_paid}")
    
    events_fail = handle_pay_bill(state, {"bill_id": "bad_id"}, week=1, context={})
    if len(events_fail) != 0: raise Exception("Expected failure for bad ID")
    
    bill.is_paid = True
    events_paid = handle_pay_bill(state, {"bill_id": "b1"}, week=1, context={})
    if len(events_paid) != 0: raise Exception("Expected failure for paid bill")

def test_resolve_dilemma_effects():
    state = LaundromatState(id="agent1", name="Laundromat 1")
    state.balance = 1000.0
    state.agent.social_score.community_standing = 50.0
    
    effects = {"money": -100.0, "reputation": 5.0, "marketing": 0.1}
    payload = {
        "dilemma_id": "d1", 
        "choice_id": "c1", 
        "effects": effects
    }
    
    events = handle_resolve_dilemma(state, payload, week=1, context={})
    if len(events) != 1: raise Exception(f"Expected 1 event, got {len(events)}")
    
    apply_dilemma_resolved(state, events[0])
    
    if state.balance != 900.0: raise Exception(f"Expected balance 900.0, got {state.balance}")
    if state.agent.social_score.community_standing != 55.0: raise Exception(f"Expected rep 55.0, got {state.agent.social_score.community_standing}")
    if state.primary_location.marketing_boost != 0.1: raise Exception(f"Expected marketing 0.1, got {state.primary_location.marketing_boost}")

if __name__ == "__main__":
    run_tests()
