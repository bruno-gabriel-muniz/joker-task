import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from joker_task.database import get_session
from joker_task.joker_task import app
from joker_task.models.models import User, table_registry
from joker_task.security.security import get_hash_password


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
        },
        {
            'email': 'bob@example.com',
            'username': 'bob',
            'password': 'secret'
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
