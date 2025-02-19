import uuid
import datetime
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    id: uuid.UUID | None = Field(primary_key=True, default=None)
    is_done: bool = Field(default=False)
    content: str
    deadline: datetime.datetime | None = Field(default=None)
    remind: datetime.datetime | None = Field(default=None)
    is_trash: bool = Field(index=True, default=False)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key='task.id', ondelete='CASCADE')
    priority: int = Field(default=1)  # 1 - 4
    topic: str | None = Field(default=None)


class Task(TaskBase, table=True):
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.now)
    user_id: uuid.UUID = Field(foreign_key='user.id', ondelete='CASCADE')


class TaskPublic(TaskBase):
    created: datetime.datetime
    updated: datetime.datetime


class TaskCreate(TaskBase):
    user_id: uuid.UUID


class TaskUpdate(TaskBase):
    id: uuid.UUID
    is_done: bool | None = None
    is_trash: bool | None = None
    content: str | None = None
    deadline: datetime.datetime | None = None
    remind: datetime.datetime | None = None
    parent_id: uuid.UUID | None = None
    topic: str | None = None
    priority: int | None = None
