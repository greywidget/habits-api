from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    name: str
    handle: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    habits: List["Habit"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all,delete"}
    )


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


class HabitBase(SQLModel):
    text: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Habit(HabitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="habits")


class HabitCreate(HabitBase):
    pass


class HabitRead(HabitBase):
    id: int
