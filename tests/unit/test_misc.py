from fastapi.testclient import TestClient
from sqlmodel import Session

from habits.payloads import HELP


def test_read_help(session: Session, client: TestClient):
    response = client.get("/help/")
    data = response.json()

    assert response.status_code == 200
    assert data["cue"] == HELP["cue"]
    assert data["craving"] == HELP["craving"]
    assert data["response"] == HELP["response"]
    assert data["reward"] == HELP["reward"]
