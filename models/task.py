import uuid
import datetime
from sqlmodel import SQLModel, Field, Relationship


class SubtaskBase(SQLModel):
    id: uuid.UUID | None = Field(primary_key=True, default=None)
    is_done: bool = Field(default=False)
    content: str
    deadline: datetime.datetime | None = Field(default=None)


class Subtask(SubtaskBase, table=True):
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.now)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key='task.id', ondelete='CASCADE')
    parent: 'Task' = Relationship(back_populates='subtasks')


class SubtaskPublic(SubtaskBase):
    id: uuid.UUID
    created: datetime.datetime
    updated: datetime.datetime


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskUpdate(SubtaskBase):
    id: uuid.UUID
    is_done: bool | None = None
    content: str | None = None
    deadline: datetime.datetime | None = None
    parent_id: uuid.UUID | None = None


class TaskBase(SubtaskBase):
    is_trash: bool = Field(index=True, default=False)


class Task(TaskBase, table=True):
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated: datetime.datetime = Field(default_factory=datetime.datetime.now)
    subtasks: list[Subtask] = Relationship(back_populates='parent')
    user_id: uuid.UUID = Field(foreign_key='user.id', ondelete='CASCADE')


class TaskPublic(TaskBase):
    created: datetime.datetime
    updated: datetime.datetime
    subtasks: list[SubtaskPublic]


class TaskCreate(TaskBase):
    user_id: uuid.UUID


class TaskUpdate(TaskBase):
    id: uuid.UUID
    is_done: bool | None = None
    is_trash: bool | None = None
    content: str | None = None
    deadline: datetime.datetime | None = None
