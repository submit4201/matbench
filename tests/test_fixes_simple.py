"""Simple tests for server fixes - no LLM required"""

def test_pending_actions_init():
    """Test that pending_actions is initialized"""
    import sys
    sys.path.insert(0, 't:/PYTHONPROJECTS2025/matbench')
    
    from src.server import GameState
    game = GameState()
    
    assert hasattr(game, 'pending_actions'), "FAIL: pending_actions not initialized"
    assert isinstance(game.pending_actions, dict), "FAIL: pending_actions should be dict"
    print("✓ pending_actions initialized correctly")

def test_serialization():
    """Test that serialization includes all required fields"""
    import sys
    sys.path.insert(0, 't:/PYTHONPROJECTS2025/matbench')
    
    from src.server import _serialize_state
    from src.world.laundromat import LaundromatState
    
    state = LaundromatState(id="test", name="Test", social_score=75.0)
    serialized = _serialize_state(state)
    
    required = ['id', 'name', 'balance', 'reputation', 'social_score', 'price', 'machines', 'inventory', 'tickets']
    for field in required:
        assert field in serialized, f"FAIL: Missing field {field}"
    
    print("✓ Serialization includes all required fields")
    print(f"✓ Both reputation ({serialized['reputation']}) and social_score ({serialized['social_score']}) available")

def test_marketing_logic():
    """Test marketing boost decay doesn't penalize social score"""
    import sys
    sys.path.insert(0, 't:/PYTHONPROJECTS2025/matbench')
    
    from src.world.laundromat import LaundromatState
    
    state = LaundromatState(id="test", name="Test", social_score=50.0, balance=200.0)
    initial_score = state.social_score
    
    state.marketing_boost = 20.0
    state.process_week(revenue=100.0, expenses=50.0)
    
    assert state.marketing_boost == 15.0, f"FAIL: Marketing boost should decay to 15, got {state.marketing_boost}"
    assert state.social_score == initial_score, f"FAIL: Social score should not change, was {initial_score}, now {state.social_score}"
    
    print("✓ Marketing boost decays without penalizing social score")

if __name__ == "__main__":
    print("="*60)
    print("Running Backend Integration Tests")
    print("="*60 + "\n")
    
    test_pending_actions_init()
    test_serialization()
    test_marketing_logic()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)
