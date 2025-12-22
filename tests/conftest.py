from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from joker_task.app import app
from joker_task.db.database import get_session
from joker_task.db.models import Tag, Task, User, table_registry
from joker_task.service.security import (
    generate_access_token,
    get_hash_password,
)
from joker_task.settings import Settings


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def users(session) -> list[dict[str, str]]:
    users = [
        {
            'email': 'alice@example.com',
            'username': 'alice',
            'password': 'secret',
            'access_token': generate_access_token({
                'sub': 'alice@example.com'
            }),
        },
        {
            'email': 'bob@example.com',
            'username': 'bob',
            'password': 'secret',
            'access_token': generate_access_token({'sub': 'bob@example.com'}),
        },
    ]

    user0 = User(
        users[0]['email'],
        users[0]['username'],
        get_hash_password(users[0]['password']),
    )
    user1 = User(
        users[1]['email'],
        users[1]['username'],
        get_hash_password(users[1]['password']),
    )

    session.add(user0)
    session.add(user1)
    await session.commit()

    return users


@pytest_asyncio.fixture
async def tags(session: AsyncSession, users) -> list[dict[str, Any]]:
    users_in_db = (
        await session.scalars(select(User).order_by(User.email))
    ).all()

    tag_test_filters = Tag('test_filters', users[0]['email'], users_in_db[0])

    tag_test_none = Tag('test_none', users[0]['email'], users_in_db[0])

    session.add(tag_test_filters)
    session.add(tag_test_none)

    out = [
        {'name': 'test_filters', 'user_email': users[0]['email'], 'id_tag': 1},
        {'name': 'test_none', 'user_email': users[0]['email'], 'id_tag': 2},
    ]

    return out


@pytest_asyncio.fixture
async def tasks(session: AsyncSession, users, tags) -> list[dict[str, Any]]:
    users_in_db = (
        await session.scalars(select(User).order_by(User.email))
    ).all()

    tag_test_filters, tag_test_none = await session.scalars(
        select(Tag).order_by(Tag.id_tag)
    )

    list_task = [
        {
            'id_task': 1,
            'user_email': users[0]['email'],
            'title': 'test',
            'description': 'this is a test',
            'done': 0,
            'tags': [tag_test_filters, tag_test_none],
            'repetition': '0111110',
            'state': 'InProgress',
            'priority': 50,
        },
        {
            'id_task': 2,
            'user_email': users[0]['email'],
            'title': 'a other test',
            'done': 0,
            'tags': [tag_test_filters],
            'repetition': '0111110',
            'state': 'ToDo',
            'priority': 60,
        },
        {
            'id_task': 3,
            'user_email': users[0]['email'],
            'title': 'title',
            'done': 0,
            'tags': [tag_test_none],
            'repetition': '1000001',
            'state': 'Done',
            'priority': 100,
        },
        {
            'id_task': 4,
            'user_email': users[1]['email'],
            'title': 'test',
            'done': 1,
            'state': 'Done',
            'priority': 55,
        },
    ]

    task1 = Task(
        user_email=list_task[0]['user_email'],
        user=users_in_db[0],
        title=list_task[0]['title'],
        description=list_task[0]['description'],
        done=list_task[0]['done'],
        tags=list_task[0]['tags'],
        repetition=list_task[0]['repetition'],
        state=list_task[0]['state'],
        priority=list_task[0]['priority'],
        reminder=None,
    )
    task2 = Task(
        user_email=list_task[1]['user_email'],
        user=users_in_db[0],
        title=list_task[1]['title'],
        done=list_task[1]['done'],
        tags=list_task[1]['tags'],
        repetition=list_task[1]['repetition'],
        state=list_task[1]['state'],
        priority=list_task[1]['priority'],
        reminder=None,
        description=None,
    )
    task3 = Task(
        user_email=list_task[2]['user_email'],
        user=users_in_db[0],
        title=list_task[2]['title'],
        done=list_task[2]['done'],
        tags=list_task[2]['tags'],
        repetition=list_task[2]['repetition'],
        state=list_task[2]['state'],
        priority=list_task[2]['priority'],
        reminder=None,
        description=None,
    )
    task4 = Task(
        user_email=list_task[3]['user_email'],
        user=users_in_db[1],
        title=list_task[3]['title'],
        done=list_task[3]['done'],
        state=list_task[3]['state'],
        priority=list_task[3]['priority'],
        reminder=None,
        repetition=None,
        tags=[],
        description=None,
    )

    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.add(task4)
    await session.commit()
    return list_task


@pytest.fixture
def settings() -> Settings:
    return Settings()  # type: ignore
