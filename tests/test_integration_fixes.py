"""Integration tests for server fixes"""
import sys
sys.path.insert(0, 't:/PYTHONPROJECTS2025/matbench')

from src.server import GameState, _serialize_state
from src.world.laundromat import LaundromatState


def test_game_state_initialization():
    """Ensure GameState initializes all required fields including pending_actions"""
    game = GameState()
    
    # Check all expected attributes exist
    assert hasattr(game, 'time_system'), "Missing time_system"
    assert hasattr(game, 'event_manager'), "Missing event_manager"
    assert hasattr(game, 'vendor'), "Missing vendor"
    assert hasattr(game, 'laundromats'), "Missing laundromats"
    assert hasattr(game, 'agents'), "Missing agents"
    assert hasattr(game, 'customers'), "Missing customers"
    assert hasattr(game, 'message_queue'), "Missing message_queue"
    assert hasattr(game, 'weekly_visits'), "Missing weekly_visits"
    assert hasattr(game, 'weekly_revenue'), "Missing weekly_revenue"
    assert hasattr(game, 'pending_actions'), "Missing pending_actions (CRITICAL BUG)"
    
    # Check pending_actions is properly initialized
    assert isinstance(game.pending_actions, dict), "pending_actions should be a dict"
    assert game.pending_actions == {}, "pending_actions should start empty"
    
    print("✓ GameState initialization test passed")


def test_laundromat_serialization():
    """Ensure _serialize_state includes all frontend-required fields"""
    state = LaundromatState(id="test", name="Test Laundromat", price=5.0, social_score=75.0)
    serialized = _serialize_state(state)
    
    # Frontend expects these fields (from types.ts)
    required_fields = [
        'id', 'name', 'balance', 'reputation', 'social_score', 
        'price', 'machines', 'broken_machines', 'inventory', 'tickets'
    ]
    
    for field in required_fields:
        assert field in serialized, f"Missing required field: {field}"
    
    # Verify both reputation and social_score are aliased
    assert serialized['reputation'] == serialized['social_score'], \
        "reputation and social_score should be aliased"
    
    # Verify id is explicitly included
    assert serialized['id'] == 'test', "id field should be included"
    
    print("✓ State serialization test passed")


def test_marketing_logic():
    """Ensure marketing boost decays properly without penalizing base social score"""
    laundromat = LaundromatState(
        id="test", 
        name="Test", 
        social_score=50.0,
        balance=200.0
    )
    
    initial_score = laundromat.social_score
    
    # Apply marketing boost
    laundromat.marketing_boost = 20.0
    laundromat.social_score += 20.0  # Manually boost for this test
    
    # Process a week
    laundromat.process_week(revenue=100.0, expenses=50.0)
    
    # Check that marketing_boost decreased but social_score didn't go negative
    assert laundromat.marketing_boost == 15.0, f"Marketing boost should decay by 5, got {laundromat.marketing_boost}"
    
    # The key fix: social_score should NOT be penalized
    # It should remain at the boosted level (or only decay naturally, not by -2.0)
    assert laundromat.social_score >= initial_score, \
        "Social score should not be penalized below initial value"
    
    print("✓ Marketing logic test passed")


def test_data_structure_consistency():
    """Verify backend data matches frontend TypeScript types"""
    game = GameState()
    
    # Get serialized state
    p1_state = _serialize_state(game.laundromats['p1'])
    
    # Check types match what frontend expects
    assert isinstance(p1_state['balance'], (int, float)), "balance should be numeric"
    assert isinstance(p1_state['reputation'], (int, float)), "reputation should be numeric"
    assert isinstance(p1_state['social_score'], (int, float)), "social_score should be numeric"
    assert isinstance(p1_state['price'], (int, float)), "price should be numeric"
    assert isinstance(p1_state['machines'], int), "machines should be int"
    assert isinstance(p1_state['broken_machines'], int), "broken_machines should be int"
    assert isinstance(p1_state['inventory'], dict), "inventory should be dict"
    assert isinstance(p1_state['tickets'], list), "tickets should be list"
    
    print("✓ Data structure consistency test passed")


if __name__ == "__main__":
    print("Running integration tests for server fixes...\n")
    
    try:
        test_game_state_initialization()
        test_laundromat_serialization()
        test_marketing_logic()
        test_data_structure_consistency()
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✓")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
