from unittest.mock import MagicMock
from src.engine.actions.handlers import handle_negotiate
from src.engine.reactions.commerce import CommerceReactions
from src.models.events.commerce import NegotiationRequested, VendorNegotiationOutcome
from src.engine.core.event_bus import EventBus
from src.engine.projections.handlers.finance import apply_tax_assessed

def test_handle_negotiate_purity():
    """Test that handle_negotiate is pure and returns NegotiationRequested."""
    state = MagicMock() # Relaxed spec
    state.id = "agent_1"
    state.reputation = 50.0
    state.social_score.total_score = 55.0

    payload = {"vendor_id": "v1", "item": "soap"}
    events = handle_negotiate(state, payload, 10, {})

    assert len(events) == 1
    evt = events[0]
    assert isinstance(evt, NegotiationRequested)
    assert evt.vendor_id == "v1"
    assert evt.social_score_snapshot == 55.0

def test_commerce_reaction_flow():
    """Test that CommerceReactions listens to Request and emits Outcome."""
    # Mock Manager and Vendor
    mock_vendor = MagicMock()
    mock_vendor.negotiate_price.return_value = {
        "success": True, 
        "discount_multiplier": 0.9, 
        "message": "OK"
    }
    mock_manager = MagicMock()
    mock_manager.get_vendor.return_value = mock_vendor
    
    # Setup Reaction and Bus
    reaction = CommerceReactions(mock_manager)
    bus = MagicMock(spec=EventBus)
    reaction.register(bus)
    
    # Trigger Event
    req_evt = NegotiationRequested(
        week=10, 
        agent_id="agent_1", 
        negotiation_id="neg_1", 
        vendor_id="v1", 
        item_type="soap",
        social_score_snapshot=50.0
    )
    
    reaction.on_negotiation_requested(req_evt)
    
    # Verify Publishing
    assert bus.publish.call_count == 3 # Attempt, Outcome, Message
    
    # Check Outcome Event
    calls = bus.publish.call_args_list
    outcome_evt = next(c[0][0] for c in calls if isinstance(c[0][0], VendorNegotiationOutcome))
    assert outcome_evt.success == True
    assert outcome_evt.new_price_multiplier == 0.9

def test_ghost_projection_fix():
    """Test tax assessment projection."""
    state = MagicMock() # Relaxed spec
    state.agent.tax_info = {}

    class MockEvent:
        week = 5
        payload = {"tax_amount": 100.0, "quarter": 1}
        
    apply_tax_assessed(state, MockEvent())
    
    assert state.agent.tax_info["last_tax_amount"] == 100.0
    assert state.agent.tax_info["fiscal_standing"] == "assessed"
