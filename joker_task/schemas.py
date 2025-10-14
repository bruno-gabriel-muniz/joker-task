from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserUpdate(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    email: EmailStr
    username: str


class UserSchema(UserPublic):
    password: str


class Token(BaseModel):
    token: str


class TaskSchema(BaseModel):
    title: str
    description: str | None = None
    done: bool | None = None
    tags: list[str] | None = None
    reminder: datetime | None = None
    repetition: str | None = None
    state: str | None = None
    priority: int | Literal[100] = 100


class TaskPublic(TaskSchema):
    id_task: int
    user_email: EmailStr
    created_at: datetime
    updated_at: datetime
