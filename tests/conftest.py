import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from habits.main import app, get_session
from habits.models import Habit, User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="user_1")
def user_1_fixture(session: Session):
    user = User(name="craig", handle="greywidget")
    session.add(user)
    session.commit()
    yield user
    session.delete(user)


@pytest.fixture(name="user_2")
def user_2_fixture(session: Session):
    user = User(name="roger", handle="fleam")
    session.add(user)
    session.commit()
    yield user
    session.delete(user)


@pytest.fixture(name="user_1_with_habits")
def user_1_habits_fixture(session: Session, user_1: User):
    habit1 = Habit(text="Read quality Python code", user=user_1)
    habit2 = Habit(text="Practice Python by doing PyBites", user=user_1)
    session.add(habit1)
    session.add(habit2)
    session.commit()
    yield user_1
    session.delete(habit1)
    session.delete(habit2)


@pytest.fixture(name="user_2_with_habits")
def user_2_habits_fixture(session: Session, user_2: User):
    habit1 = Habit(text="Practice Juggling 5 ball flash", user=user_2)
    habit2 = Habit(text="No eating Quality Street chocolates", user=user_2)
    session.add(habit1)
    session.add(habit2)
    session.commit()
    yield user_2
    session.delete(habit1)
    session.delete(habit2)
