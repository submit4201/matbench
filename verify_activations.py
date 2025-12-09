import sys
import os
sys.path.append(os.getcwd())

try:
    print("Attempting to import src.server...")
    from src.server import app, game
    from fastapi.testclient import TestClient
    from unittest.mock import MagicMock

    print("Import successful")

    client = TestClient(app)

    # Mock engine parts if not fully initialized or to isolate tests
    # But checking if game.engine exists first
    if not hasattr(game, "engine"):
        print("Game engine not initialized on game object")
    else:
        # We need to mock the methods on the engine instance
        # If the engine is already instantiated (which it is in server.py likely), we mock the method on it.
        # But server.py might be initializing EnhancedGameEngine which *has* these methods?
        # Let's see if we need to mock or if we can rely on real implementation if mocked dependencies.
        # For 'Activate Dead Features', we added methods to EnhancedGameEngine that delegate to sub-systems.
        
        # We mock the sub-methods to verify the ROUTING is correct.
        game.engine.get_credit_report = MagicMock(return_value={"credit_score": 750, "rating": "excellent", "active_loans": []})
        game.engine.get_calendar = MagicMock()
        mock_cal = MagicMock()
        mock_cal.get_statistics.return_value = {"upcoming": 2}
        mock_cal.get_week_schedule.return_value = {}
        game.engine.get_calendar.return_value = mock_cal
        
        game.engine.get_zone_info = MagicMock(return_value={"zone_name": "Test Zone"})
        
        print("Mocks applied. Testing endpoints...")

        # Test Credit
        res = client.get("/credit/p1")
        print(f"GET /credit/p1: {res.status_code} {res.json()}")
        assert res.status_code == 200
        assert res.json()["credit"]["credit_score"] == 750

        # Test Calendar
        res = client.get("/calendar/p1")
        print(f"GET /calendar/p1: {res.status_code}")
        assert res.status_code == 200
        
        # Test Zone
        res = client.get("/zone/p1")
        print(f"GET /zone/p1: {res.status_code} {res.json()}")
        assert res.status_code == 200
        
        print("ALL VERIFICATIONS PASSED")

except Exception as e:
    print(f"Verification ERROR: {e}")
    import traceback
    traceback.print_exc()
