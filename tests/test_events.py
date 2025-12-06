import pytest
from src.engine.events import EventManager, EventType
from src.engine.time import Season

def test_seasonal_events():
    manager = EventManager()
    
    # Test Summer Heatwave
    # We force random to trigger it by running many times or mocking random
    # For simplicity, we'll just run it many times and check if we get at least one
    
    heatwave_triggered = False
    for _ in range(100):
        events = manager.generate_random_events(week=10, agent_ids=[], season=Season.SUMMER)
        for e in events:
            if e.type == EventType.GLOBAL_HEATWAVE:
                heatwave_triggered = True
                break
        if heatwave_triggered: break
        
    # Note: 15% chance * 100 tries = almost certain
    assert heatwave_triggered, "Heatwave should trigger in Summer"

    # Test Winter Cold Snap
    cold_snap_triggered = False
    for _ in range(100):
        events = manager.generate_random_events(week=20, agent_ids=[], season=Season.WINTER)
        for e in events:
            if e.type == EventType.SEASONAL_SPIKE and "cold snap" in e.description:
                cold_snap_triggered = True
                break
        if cold_snap_triggered: break
        
    assert cold_snap_triggered, "Cold snap should trigger in Winter"

if __name__ == "__main__":
    test_seasonal_events()
    print("All event tests passed!")
