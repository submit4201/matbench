from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

def test_read_root():
    """Verify server root endpoint matches expectation (404 for root, or specific endpoint)"""
    # Assuming root might not be defined, but health/docs might be. 
    # Let's check a non-existent endpoint to see app is running and returns 404 (std fastapi)
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_server_logging(capture_logs):
    """Verify that hitting an endpoint logs the request"""
    response = client.get("/nonexistent-endpoint")
    # Middleware log expected
    assert any("REQUEST: GET" in record.message for record in capture_logs.records)
    assert any("RESPONSE: 404" in record.message for record in capture_logs.records)
