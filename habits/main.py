from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.sql.operators import ilike_op
from sqlmodel import Session, select

from .db import create_db_and_tables, engine
from .models import Habit, HabitCreate, HabitRead, User, UserCreate, UserRead
from .payloads import HELP

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_session():
    with Session(engine) as session:
        yield session


@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
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
    limit: int = Query(default=100, le=100),
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}", response_model=UserRead)
def read_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.delete("/users/{user_id}")
def delete_user(*, session: Session = Depends(get_session), user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}


@app.post("/habits/", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(*, session: Session = Depends(get_session), habit: HabitCreate):
    db_habit = Habit.from_orm(habit)

    user = session.get(User, habit.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not a valid user id"
        )

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
    contains: Optional[str] = None,
):
    sel = select(Habit)
    if user_id:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        sel = sel.where(Habit.user_id == user_id)

    if contains:
        sel = sel.where(ilike_op(Habit.text, f"%{contains.lower()}%"))

    habits = session.exec(sel.offset(offset).limit(limit)).all()
    return habits


@app.get("/habits/{habit_id}", response_model=HabitRead)
def read_habit(*, session: Session = Depends(get_session), habit_id: int):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )
    return habit


@app.delete("/habits/{habit_id}")
def delete_habit(*, session: Session = Depends(get_session), habit_id: int):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )
    session.delete(habit)
    session.commit()
    return {"ok": True}


@app.get("/help/")
def help():
    return HELP
