from src.agents.base_agent import Action, ActionType
from src.world.laundromat import LaundromatState
from src.server import _apply_action
import pytest
from unittest.mock import MagicMock

# Mocking game global
import src.server
src.server.game = MagicMock()

def test_set_price_bug_reproduction():
    # Setup state
    state = LaundromatState(id="test_p1", name="Test Mat")
    state.price = 3.0
    
    # 1. Simulate INCORRECT frontend payload (Current Bug)
    # Frontend sends { "new_price": 5.0 }
    action_bad = Action(type=ActionType.SET_PRICE, parameters={"new_price": 5.0})
    
    _apply_action(state, action_bad)
    
    # Assert price did NOT change (it defaults to existing price if key missing)
    assert state.price == 3.0, "Price should not change with wrong key"
    
def test_set_price_fix_verification():
    # Setup state
    state = LaundromatState(id="test_p1", name="Test Mat")
    state.price = 3.0
    
    # 2. Simulate CORRECTED frontend payload
    # Frontend SHOULD send { "price": 5.0 }
    action_good = Action(type=ActionType.SET_PRICE, parameters={"price": 5.0})
    
    _apply_action(state, action_good)
    
    # Assert price UPDATED
    assert state.price == 5.0, "Price should update with correct key"
