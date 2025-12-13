
import sys
import os
import traceback

# Add src to path
sys.path.append(os.getcwd())

try:
    from src.world.laundromat import LaundromatState
    from src.engine.projections.handlers.commerce import apply_buyout_offer_sent, apply_vendor_negotiation_outcome
    from src.engine.projections.handlers.operations import apply_proposal_submitted, apply_customer_service_completed
    from src.engine.projections.handlers.social import apply_investigation_opened, apply_message_sent
    from src.engine.projections.handlers.finance import apply_loan
    from src.models.events.core import GameEvent
    
    # Helper to mock event
    class MockEvent(GameEvent):
        payload: dict = {}
        
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def run_tests():
    print("Starting Stub Verification...")
    
    state = LaundromatState(id="agent1", name="Laundromat 1")
    
    # 1. Finance: Loan
    try:
        print("Test 1: Loan Origination")
        evt = MockEvent(type="LOAN_ORIGINATED", week=1, agent_id=state.id, payload={
            "loan_id": "L1", "principal": 10000.0, "interest_rate": 0.05
        })
        apply_loan(state, evt)
        if len(state.loans) != 1 or state.loans[0].balance != 10000.0:
            raise Exception("Loan not added correctly")
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

    # 2. Commerce: Buyout
    try:
        print("\nTest 2: Buyout Offer")
        evt = MockEvent(type="BUYOUT_OFFER_SENT", week=1, agent_id=state.id, payload={
            "proposal_id": "P1", "target_agent_id": "agent2", "offer_amount": 5000.0
        })
        apply_buyout_offer_sent(state, evt)
        if len(state.agent.proposals) != 1: raise Exception("Proposal not tracked")
        if state.agent.proposals[0]["amount"] != 5000.0: raise Exception("Wrong offer amount")
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

    # 3. Social: Investigation
    try:
        print("\nTest 3: Investigation Opened")
        evt = MockEvent(type="INVESTIGATION_OPENED", week=1, agent_id=state.id, payload={
            "case_id": "CASE-001", "violation_type": "safety"
        })
        apply_investigation_opened(state, evt)
        if len(state.agent.active_investigations) != 1: raise Exception("Investigation not tracked")
        if state.agent.active_investigations[0]["id"] != "CASE-001": raise Exception("Wrong case ID")
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

    # 4. Social: Message
    try:
        print("\nTest 4: Message Sent")
        evt = MockEvent(type="MESSAGE_SENT", week=1, agent_id=state.id, payload={
            "msg_id": "M1", "content": "Hello", "recipients": ["agent2"], "channel": "email", "intent": "chat"
        })
        apply_message_sent(state, evt)
        if len(state.agent.message_history) != 1: raise Exception("Message not logged")
        if state.agent.message_history[0]["content"] != "Hello": raise Exception("Wrong content")
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()
