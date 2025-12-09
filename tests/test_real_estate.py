
import pytest
from src.engine.commerce.real_estate import RealEstateManager, Building
from src.world.laundromat import LaundromatState
from src.engine.game_engine import GameEngine

def test_real_estate_manager_listings():
    manager = RealEstateManager()
    listings = manager.get_listings()
    assert len(listings) > 0
    assert isinstance(listings[0], Building)

def test_purchase_logic():
    manager = RealEstateManager()
    initial_count = len(manager.get_listings())
    listing = manager.get_listings()[0]
    
    # Buy it
    bought_building = manager.process_purchase(listing.id)
    assert bought_building is not None
    assert bought_building.id == listing.id
    
    # Verify removed from market
    assert len(manager.get_listings()) == initial_count - 1
    assert manager.get_listing(listing.id) is None

def test_game_engine_integration():
    # Setup
    engine = GameEngine(["p1"])
    state = engine.states["p1"]
    
    # Give generic generic money
    state.ledger.add(1000000.0, "capital", "Seed", 0)
    
    # Get a listing
    listing = engine.real_estate_manager.get_listings()[0]
    initial_balance = state.balance
    
    # Action
    action = {
        "type": "BUY_BUILDING",
        "listing_id": listing.id
    }
    
    engine._apply_action(state, action)
    
    # Verification
    assert len(state.buildings) >= 2 # HQ + new one
    assert state.buildings[-1].id == listing.id
    assert state.locations[-1] == listing.id
    assert state.balance < initial_balance
    # Approximate check due to float math
    assert abs(state.balance - (initial_balance - listing.price)) < 0.01

def test_insufficient_funds():
    engine = GameEngine(["p1"])
    state = engine.states["p1"]
    
    # Ensure low balance
    # We can't easily set balance directly because it's a property based on ledger.
    # But we start with 2500, listing is usually >30k.
    
    listing = engine.real_estate_manager.get_listings()[0]
    initial_buildings_count = len(state.buildings)
    
    # Action
    action = {
        "type": "BUY_BUILDING",
        "listing_id": listing.id
    }
    
    engine._apply_action(state, action)
    
    # Should fail
    assert len(state.buildings) == initial_buildings_count
