import uuid
import datetime
from sqlmodel import SQLModel, Field, Relationship

from .task import Task, TaskPublic


class UserBase(SQLModel):
    first_name: str | None = Field(default=None)
    second_name: str | None = Field(default=None)
    birthday: datetime.date | None = Field(default=None)
    login: str = Field(index=True)
    email: str = Field(index=True)
    password: str


class User(UserBase, table=True):
    id: uuid.UUID | None = Field(primary_key=True, default=None)
    registration: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tasks: list[Task] = Relationship(back_populates=None)


class UserPublic(SQLModel):
    id: uuid.UUID
    first_name: str | None
    second_name: str | None
    login: str
    email: str
    birthday: datetime.date | None
    tasks: list[TaskPublic]


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    id: uuid.UUID
    first_name: str | None = None
    second_name: str | None = None
    birthday: datetime.date | None = None
    login: str | None = None
    email: str | None = None
    password: str | None = None
