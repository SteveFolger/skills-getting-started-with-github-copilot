import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_participants = {
        activity_name: list(activity["participants"])
        for activity_name, activity in activities.items()
    }

    with TestClient(app) as test_client:
        yield test_client

    for activity_name, participants in original_participants.items():
        activities[activity_name]["participants"][:] = participants


def test_get_activities_returns_activity_details(client):
    activity_name = "Chess Club"
    expected_activity = {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    }

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()[activity_name] == expected_activity


def test_signup_adds_participant(client):
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"
    expected_response = {"message": f"Signed up {email} for {activity_name}"}

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == expected_response
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    expected_error = {"detail": "Student already signed up for this activity"}

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json() == expected_error


def test_signup_rejects_unknown_activity(client):
    activity_name = "Unknown Club"
    email = "new-student@mergington.edu"
    expected_error = {"detail": "Activity not found"}

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json() == expected_error


def test_unregister_removes_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    expected_response = {"message": f"Unregistered {email} from {activity_name}"}

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == expected_response
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_nonparticipant(client):
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"
    expected_error = {"detail": "Student is not signed up for this activity"}

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json() == expected_error


def test_unregister_rejects_unknown_activity(client):
    activity_name = "Unknown Club"
    email = "new-student@mergington.edu"
    expected_error = {"detail": "Activity not found"}

    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json() == expected_error