from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.models import Workbench


@pytest.mark.asyncio
async def test_create_workbench(
    client: TestClient, session: AsyncSession, users
):
    rsp = client.post(
        '/workbenches/',
        json={
            'name': 'workbench3',
            'columns': ['To Do', 'In Progress', 'Done'],
        },
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_workbench'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['name'] == 'workbench3'
    assert data['columns'] == ['To Do', 'In Progress', 'Done']

    workbench_db = await session.scalar(
        select(Workbench).where(Workbench.id_workbench == data['id_workbench'])
    )

    assert workbench_db is not None
    assert workbench_db.name == data['name']


def test_create_workbench_conflict(client: TestClient, users, workbenches):
    rsp = client.post(
        '/workbenches/',
        json={'name': 'workbench3', 'columns': []},
        headers={'Authorization': f'Bearer {users[1]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'workbench name already in use'


def test_created_at_workbench(client: TestClient, users):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = client.post(
            '/workbenches/',
            json={'name': 'Time Workbench', 'columns': []},
            headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    expected = time.replace(microsecond=0).isoformat()
    assert expected.startswith(data['created_at'][0:16])
    assert expected.startswith(data['updated_at'][0:16])


def test_not_found_workbench(client: TestClient, users, workbenches):
    rsp = client.post(
        '/tasks/',
        json={
            'title': 'test workbench',
            'workbenches': [3],
        },
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'workbench with id: 3, not found'
