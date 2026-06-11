import os
import sys
from fastapi.testclient import TestClient

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

client = TestClient(app)

# Test Status endpoint
print("Testing /api/status...")
res = client.get("/api/status")
print(res.status_code, res.json())
assert res.status_code == 200

# Test Track endpoint
print("\nTesting /api/track...")
track_payload = {
    "event_name": "page_view",
    "url": "http://localhost:8000/",
    "referrer": "google.com",
    "utm_source": "test_suite",
    "utm_medium": "email",
    "utm_campaign": "launch",
    "metadata": {"session_id": "test_sess_123"}
}
res = client.post("/api/track", json=track_payload)
print(res.status_code, res.json())
assert res.status_code == 200

# Test Analytics dashboard
print("\nTesting /analytics...")
res = client.get("/analytics")
print(res.status_code)
assert res.status_code == 200
assert "total_sessions" not in res.text # Check that replacements worked and template keys were filled
print("Analytics HTML length:", len(res.text))

print("\nAll verification tests passed successfully!")
