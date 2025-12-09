from fastapi.testclient import TestClient
from urllib.parse import quote
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should return a dict with known activities
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure email is not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    participants_before = data[activity]["participants"].copy()
    assert email not in participants_before

    # Signup
    path = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    resp = client.post(path)
    assert resp.status_code == 200
    resp_json = resp.json()
    assert "Signed up" in resp_json.get("message", "")

    # Verify participant added
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

    # Duplicate signup should return 400
    resp = client.post(path)
    assert resp.status_code == 400

    # Unregister
    del_path = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    resp = client.delete(del_path)
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_unregister_nonexistent_participant():
    activity = "Programming Class"
    email = "nonexistent@example.com"
    del_path = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    resp = client.delete(del_path)
    assert resp.status_code == 404

