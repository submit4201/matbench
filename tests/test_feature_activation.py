from fastapi.testclient import TestClient
from src.server import app, game
from src.engine.finance.models import CreditReport
import pytest
from unittest.mock import MagicMock

client = TestClient(app)

def test_credit_endpoint():
    # Mock engine response
    game.engine = MagicMock()
    game.engine.get_credit_report.return_value = {
        "credit_score": 720,
        "rating": "good",
        "active_loans": [],
        "payment_history": [],
        "total_debt": 0.0
    }
    
    response = client.get("/credit/p1")
    assert response.status_code == 200
    data = response.json()
    assert "credit" in data
    assert data["credit"]["credit_score"] == 720

def test_calendar_endpoint():
    game.engine = MagicMock()
    # Mock calendar with get_statistics and get_week_schedule
    mock_cal = MagicMock()
    mock_cal.get_statistics.return_value = {"total_scheduled": 5}
    mock_cal.get_week_schedule.return_value = {}
    
    game.engine.get_calendar.return_value = mock_cal
    game.engine.time_system.current_week = 1
    
    response = client.get("/calendar/p1")
    assert response.status_code == 200
    assert "statistics" in response.json()

def test_zone_endpoint():
    game.engine = MagicMock()
    game.engine.get_zone_info.return_value = {
        "zone_id": "zone_1",
        "zone_name": "Downtown",
        "base_foot_traffic": 100
    }
    
    response = client.get("/zone/p1")
    assert response.status_code == 200
    assert response.json()["zone"]["zone_name"] == "Downtown"
