from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

LOGIC_LIKE = 'LIKE'
LOGIC_LIST_IN_LIST = 'LIST_IN_LIST'
LOGIC_IN_LIST = 'IN_LIST'
LOGIC_EXACT = 'EXACT'
LOGIC_RANGE = 'RANGE'


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
    access_token: str
    token_type: str = 'bearer'


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


class FilterPage(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


class Filter(FilterPage):
    title: str | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_LIKE}
    )
    description: str | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_LIKE}
    )
    done: bool | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_EXACT}
    )
    tags: list[str] | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_LIST_IN_LIST}
    )
    reminder: tuple[datetime | None, datetime | None] | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_RANGE}
    )
    repetition: str | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_EXACT}
    )
    state: list[str] | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_IN_LIST}
    )
    priority: tuple[int | None, int | None] | None = Field(
        default=None, json_schema_extra={'search_logic': LOGIC_RANGE}
    )


class ResponseTasks(BaseModel):
    responses: list[TaskPublic]
