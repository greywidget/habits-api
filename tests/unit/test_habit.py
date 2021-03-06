from fastapi.testclient import TestClient
from sqlmodel import Session

from habits.models import Habit, User


def test_create_habit(client: TestClient, user_1: User):
    response = client.post(
        "/habits/",
        json={"text": "Read quality Python code", "user_id": user_1.id},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["text"] == "Read quality Python code"
    assert data["user_id"] == 1
    assert data["id"] is not None


def test_create_habit_bad_user(client: TestClient):
    response = client.post(
        "/habits/",
        json={"text": "Read quality Python code", "user_id": 0},
    )
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Not a valid user id"


def test_create_habit_duplicate_same_user(client: TestClient, user_1_with_habits: User):
    response = client.post(
        "/habits/",
        json={
            "text": "Read quality Python code",
            "user_id": f"{user_1_with_habits.id}",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == f"Habit already exists for this user id"


def test_create_habit_duplicate_different_user(
    client: TestClient, user_1_with_habits: User, user_2_with_habits: User
):
    response = client.post(
        "/habits/",
        json={
            "text": "Read quality Python code",
            "user_id": f"{user_2_with_habits.id}",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Read quality Python code"
    assert data["user_id"] == user_2_with_habits.id
    assert data["id"] is not None


def test_delete_habit(session: Session, client: TestClient, user_1: User):
    response = client.post(
        "/habits/",
        json={"text": "Solve some PyBites", "user_id": user_1.id},
    )
    data = response.json()

    habit_id = data["id"]
    response = client.delete(f"/habits/{habit_id}")
    assert response.status_code == 200

    habit_in_db = session.get(Habit, habit_id)
    assert habit_in_db is None


def test_read_habit(client: TestClient, user_1_with_habits: User):
    habit = user_1_with_habits.habits[0]
    response = client.get(f"/habits/{habit.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["user_id"] == user_1_with_habits.id
    assert data["id"] == habit.id
    assert data["text"] == habit.text


def test_read_bad_habit(client: TestClient):
    response = client.get("/habits/99")
    data = response.json()
    assert response.status_code == 404


def test_read_all_habits(
    client: TestClient, user_1_with_habits: User, user_2_with_habits: User
):
    passed_habits = sorted(
        [habit.text for habit in user_1_with_habits.habits]
        + [habit.text for habit in user_2_with_habits.habits]
    )

    response = client.get("/habits/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == len(user_1_with_habits.habits) + len(user_2_with_habits.habits)
    retrieved_habits = sorted(item["text"] for item in data)
    assert passed_habits == retrieved_habits


def test_read_habits_for_user(
    client: TestClient, user_1_with_habits: User, user_2_with_habits: User
):
    user1_habits = sorted([habit.text for habit in user_1_with_habits.habits])

    response = client.get("/habits/")
    data = response.json()
    assert response.status_code == 200

    response = client.get(f"/habits/?user_id={user_1_with_habits.id}")
    data = response.json()
    assert response.status_code == 200
    retrieved_habits = sorted(item["text"] for item in data)
    assert user1_habits == retrieved_habits


def test_read_habits_for_bad_user(
    client: TestClient, user_1_with_habits: User, user_2_with_habits: User
):
    response = client.get("/habits/?user_id=99")
    data = response.json()
    assert response.status_code == 404


def test_read_habits_for_keyword(
    client: TestClient, user_1_with_habits: User, user_2_with_habits: User
):
    word = "quality"
    user1_match = [
        habit.text for habit in user_1_with_habits.habits if word in habit.text.lower()
    ]
    user2_match = [
        habit.text for habit in user_2_with_habits.habits if word in habit.text.lower()
    ]

    response = client.get(f"/habits/?contains={word}")
    data = response.json()
    assert response.status_code == 200
    retrieved_habits = sorted(item["text"] for item in data)
    assert sorted(user1_match + user2_match) == retrieved_habits


def test_read_habits_for_user_and_keyword(
    client: TestClient, user_1_with_habits: User, user_2_with_habits: User
):
    word = "quality"
    user1_match = sorted(
        [
            habit.text
            for habit in user_1_with_habits.habits
            if word in habit.text.lower()
        ]
    )

    response = client.get(f"/habits/?user_id={user_1_with_habits.id}&contains={word}")
    data = response.json()
    assert response.status_code == 200
    retrieved_habits = sorted(item["text"] for item in data)
    assert user1_match == retrieved_habits


def test_delete_user_deletes_assoc_habits(client: TestClient, user_1: User):
    habits = (
        "Read Quality Python code",
        "Pogo for 5 minutes",
        "No sticky buns",
    )
    for text in habits:
        client.post("/habits/", json={"text": text, "user_id": user_1.id})
    response = client.get("/habits/")

    data = response.json()
    assert len(data) == 3

    response = client.delete(f"/users/{user_1.id}")
    assert response.status_code == 200

    # cascade: habits of user get deleted as well upon user deletion
    response = client.get("/habits/")
    data = response.json()
    assert len(data) == 0


def test_delete_bad_habit(client: TestClient):
    response = client.delete("/habits/99")
    data = response.json()
    assert response.status_code == 404


def test_read_too_many_habits(client: TestClient):
    response = client.get("/habits/?limit=101")
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["loc"] == ["query", "limit"]
    data["detail"][0]["msg"] == "ensure this value is less than or equal to 100"
