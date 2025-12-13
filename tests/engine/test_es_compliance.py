
import pytest
from src.world.laundromat import LaundromatState
from src.engine.actions.handlers import handle_hire_staff, handle_pay_bill, handle_resolve_dilemma
from src.engine.projections.handlers.social import apply_dilemma_resolved
from src.engine.finance import Bill
from src.models.events.core import GameEvent
from src.models.events.social import DilemmaResolved

def test_hire_staff_purity():
    """Test that hire staff implementation is pure and emits correct events."""
    state = LaundromatState(id="agent1", name="Laundromat 1")
    state.balance = 1000.0
    payload = {"role": "cleaner"}
    
    events = handle_hire_staff(state, payload, week=1, context={})
    
    assert len(events) == 2
    assert events[1].type == "STAFF_HIRED"
    assert events[1].role == "cleaner"
    # Ensure wage is set (logic check)
    assert events[1].wage > 0

def test_pay_bill_validation():
    """Test that pay bill validates against state."""
    state = LaundromatState(id="agent1", name="Laundromat 1")
    state.balance = 1000.0
    
    # 1. Add Bill
    bill = Bill(id="b1", name="Rent", amount=500.0, due_week=2, category="rent", recipient_id="landlord", generated_week=1)
    state.bills.append(bill)
    
    # 2. Pay valid bill
    events = handle_pay_bill(state, {"bill_id": "b1"}, week=1, context={})
    assert len(events) == 2
    assert events[1].type == "BILL_PAID"
    assert events[1].amount_paid == 500.0
    
    # 3. Pay invalid bill (wrong ID)
    events_fail = handle_pay_bill(state, {"bill_id": "bad_id"}, week=1, context={})
    assert len(events_fail) == 0
    
    # 4. Pay already paid bill
    bill.is_paid = True
    events_paid = handle_pay_bill(state, {"bill_id": "b1"}, week=1, context={})
    assert len(events_paid) == 0

def test_resolve_dilemma_effects():
    """Test that dilemma resolution captures effects and projection applies them."""
    state = LaundromatState(id="agent1", name="Laundromat 1")
    state.balance = 1000.0
    state.agent.social_score.community_standing = 50.0
    
    # 1. Action
    effects = {"money": -100.0, "reputation": 5.0, "marketing": 0.1}
    payload = {
        "dilemma_id": "d1", 
        "choice_id": "c1", 
        "effects": effects
    }
    
    events = handle_resolve_dilemma(state, payload, week=1, context={})
    assert len(events) == 1
    assert isinstance(events[0], DilemmaResolved)
    assert events[0].effects == effects
    
    # 2. Projection
    apply_dilemma_resolved(state, events[0])
    
    # Balance should decrease by 100
    assert state.balance == 900.0
    # Reputation should increase by 5
    assert state.agent.social_score.community_standing == 55.0
    # Marketing boost checks
    assert state.primary_location.marketing_boost == 0.1
