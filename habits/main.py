from json.encoder import py_encode_basestring_ascii
from typing import Optional

from .db import create_db_and_tables, engine
from .models import (
    User,
    UserCreate,
    UserRead,
    Habit,
    HabitCreate,
    HabitRead,
)

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, default, select

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_session():
    with Session(engine) as session:
        yield session


@app.post("/users/", response_model=UserRead)
def create_user(*, session: Session = Depends(get_session), user: UserCreate):
    db_user = User.from_orm(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[UserRead])
def read_users(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}")
def delete_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@app.post("/habits/", response_model=HabitRead)
def create_habit(*, session: Session = Depends(get_session), habit: HabitCreate):
    db_habit = Habit.from_orm(habit)

    user = session.get(User, habit.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Not a valid user id")

    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)
    return db_habit


@app.get("/habits/", response_model=list[HabitRead])
def read_habits(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    user_id: Optional[int] = None,
    contains: Optional[str] = None
):
    sel = select(Habit)
    if user_id:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        sel = sel.where(Habit.user_id == user_id)

    if contains:
        pass

    habits = session.exec(sel.offset(offset).limit(limit)).all()
    if user_id:
        print(user_id)
    return habits


@app.get("/habits/{habit_id}", response_model=HabitRead)
def read_habit(*, session: Session = Depends(get_session), habit_id: int):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.delete("/habits/{habit_id}")
def delete_habit(*, session: Session = Depends(get_session), habit_id: int):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    session.delete(habit)
    session.commit()
    return {"ok": True}
