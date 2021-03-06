from fastapi.testclient import TestClient
from sqlmodel import Session

from habits.models import User


def test_create_user(client: TestClient):
    response = client.post("/users/", json={"name": "craig", "handle": "greywidget"})
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "craig"
    assert data["handle"] == "greywidget"
    assert data["id"] is not None


def test_create_user_incomplete(client: TestClient):
    # No handle
    response = client.post("/users/", json={"name": "craig"})
    assert response.status_code == 422


def test_create_user_invalid(client: TestClient):
    # handle has an invalid type
    response = client.post("/users/", json={"name": "craig", "moose": []})
    assert response.status_code == 422


def test_create_user_duplicate(client: TestClient, user_1: User):
    response = client.post("/users/", json={"name": "grey", "handle": "greywidget"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_read_users(session: Session, client: TestClient, user_1: User):
    user_2 = User(name="roger", handle="fleam")
    session.add(user_2)
    session.commit()

    response = client.get("/users/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["name"] == user_1.name
    assert data[0]["handle"] == user_1.handle
    assert data[0]["id"] == user_1.id
    assert data[1]["name"] == user_2.name
    assert data[1]["handle"] == user_2.handle
    assert data[1]["id"] == user_2.id


def test_read_user(client: TestClient, user_1: User):
    response = client.get(f"/users/{user_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == user_1.name
    assert data["handle"] == user_1.handle
    assert data["id"] == user_1.id


def test_read_bad_user(client: TestClient):
    response = client.get("/users/99")
    data = response.json()
    assert response.status_code == 404


def test_delete_user(session: Session, client: TestClient, user_1: User):
    response = client.delete(f"/users/{user_1.id}")
    user_in_db = session.get(User, user_1.id)

    assert response.status_code == 200
    assert user_in_db is None


def test_delete_bad_user(client: TestClient):
    response = client.delete(f"/users/99")
    data = response.json()
    assert response.status_code == 404
