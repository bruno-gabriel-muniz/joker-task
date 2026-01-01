from datetime import datetime
from typing import Sequence

from pydantic import BaseModel, EmailStr, Field

from joker_task.db.models import Tag

LOGIC_LIKE = 'LIKE'
LOGIC_WITH_TAGS = 'WITH_TAGS'
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


class TagsSchema(BaseModel):
    names: Sequence[str]


class TagUpdate(BaseModel):
    name: str


class TagPublic(BaseModel):
    name: str
    id_tag: int
    user_email: EmailStr
    created_at: datetime
    updated_at: datetime


class WorkbenchSchema(BaseModel):
    name: str
    columns: list[str] = Field(default_factory=list)


class WorkbenchPublic(WorkbenchSchema):
    id_workbench: int
    user_email: EmailStr
    created_at: datetime
    updated_at: datetime


class TaskSchema(BaseModel):
    title: str
    description: str | None = None
    done: bool | None = None
    tags: Sequence[str | Tag] | None = []
    reminder: datetime | None = None
    repetition: str | None = None
    state: str | None = None
    priority: int = 100


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None
    tags_add: Sequence[str] | None = None
    tags_remove: Sequence[str] | None = None
    reminder: datetime | None = None
    repetition: str | None = None
    state: str | None = None
    priority: int = 100


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
        default=None, json_schema_extra={'search_logic': LOGIC_WITH_TAGS}
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
