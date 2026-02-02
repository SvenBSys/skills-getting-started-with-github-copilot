import copy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def _snapshot_activities():
    return copy.deepcopy(activities)


def _restore_activities(snapshot):
    activities.clear()
    activities.update(snapshot)


def test_get_activities_returns_seed_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Soccer Club" in data
    assert "participants" in data["Soccer Club"]


def test_signup_adds_participant():
    snapshot = _snapshot_activities()
    try:
        activity = "Soccer Club"
        email = "new.student@mergington.edu"
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
    finally:
        _restore_activities(snapshot)


def test_signup_duplicate_rejected():
    snapshot = _snapshot_activities()
    try:
        activity = "Soccer Club"
        email = activities[activity]["participants"][0]
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    finally:
        _restore_activities(snapshot)


def test_unregister_removes_participant():
    snapshot = _snapshot_activities()
    try:
        activity = "Soccer Club"
        email = activities[activity]["participants"][0]
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
    finally:
        _restore_activities(snapshot)


def test_unregister_unknown_participant_returns_404():
    snapshot = _snapshot_activities()
    try:
        activity = "Soccer Club"
        email = "unknown@mergington.edu"
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
    finally:
        _restore_activities(snapshot)
