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
    auth_client_alice: TestClient, session: AsyncSession, users
):
    rsp = auth_client_alice.post(
        '/workbenches/',
        json={
            'name': 'workbench3',
            'columns': ['To Do', 'In Progress', 'Done'],
        },
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_workbench'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['name'] == 'workbench3'
    assert data['columns'] == sorted(['To Do', 'In Progress', 'Done'])

    workbench_db = await session.scalar(
        select(Workbench).where(Workbench.id_workbench == data['id_workbench'])
    )

    assert workbench_db is not None
    assert workbench_db.name == data['name']


def test_create_workbench_conflict(auth_client_bob: TestClient, workbenches):
    rsp = auth_client_bob.post(
        '/workbenches/', json={'name': 'workbench3', 'columns': []}
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'workbench name already in use'


def test_created_at_workbench(auth_client_alice: TestClient):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = auth_client_alice.post(
            '/workbenches/', json={'name': 'Time Workbench', 'columns': []}
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    expected = time.replace(microsecond=0).isoformat()
    assert expected.startswith(data['created_at'][0:16])
    assert expected.startswith(data['updated_at'][0:16])


def test_not_found_workbench_in_update_task(
    auth_client_bob: TestClient, workbenches
):
    fake_workbench_id = len(workbenches) + 1
    rsp = auth_client_bob.post(
        '/tasks/',
        json={
            'title': 'test workbench',
            'workbenches': [fake_workbench_id],
        },
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'workbench with id: 4, not found'


def test_list_workbenches(auth_client_alice: TestClient, workbenches):
    rsp = auth_client_alice.get(
        '/workbenches/',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = {workbench['id_workbench']: workbench for workbench in rsp.json()}

    workbench_spec = 2
    assert len(data) == workbench_spec
    assert data[1]['name'] == 'workbench1'
    assert data[2]['name'] == 'workbench2'


def test_get_workbench_by_id(
    auth_client_alice: TestClient, tasks, workbenches
):
    rsp = auth_client_alice.get(
        '/workbenches/1',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    workbench, tasks_rsp = data['workbench'], data['tasks']

    assert workbench['id_workbench'] == 1
    assert workbench['name'] == 'workbench1'

    tasks_rsp = {task['id_task']: task for task in tasks_rsp}
    qnt_task = 2

    assert len(tasks_rsp) == qnt_task
    assert tasks_rsp[2]['title'] == 'a other test'
    assert tasks_rsp[3]['title'] == 'title'


def test_get_workbench_by_id_not_found(auth_client_bob: TestClient):
    rsp = auth_client_bob.get('/workbenches/999')

    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_workbench_by_id_forbidden(
    auth_client_bob: TestClient, workbenches
):
    rsp = auth_client_bob.get('/workbenches/1')

    assert rsp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_workbench_name(
    auth_client_alice: TestClient, session: AsyncSession, workbenches
):
    rsp = auth_client_alice.patch(
        '/workbenches/1', json={'name': 'Updated Workbench'}
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_workbench'] == 1
    assert data['name'] == 'Updated Workbench'

    workbench_db = await session.scalar(
        select(Workbench).where(Workbench.id_workbench == data['id_workbench'])
    )

    assert workbench_db is not None
    assert workbench_db.name == 'Updated Workbench'


@pytest.mark.asyncio
async def test_update_workbench_columns(
    auth_client_alice: TestClient, session: AsyncSession, workbenches
):
    rsp = auth_client_alice.patch(
        '/workbenches/2',
        json={
            'columns_add': ['Backlog', 'Completed'],
            'columns_remove': ['To Do', 'Done'],
        },
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    id_workbench = 2
    assert data['id_workbench'] == id_workbench
    assert data['columns'] == sorted(['Backlog', 'In Progress', 'Completed'])

    workbench_db = await session.scalar(
        select(Workbench).where(Workbench.id_workbench == data['id_workbench'])
    )

    assert workbench_db is not None
    assert (workbench_db.columns) == sorted([
        'Backlog',
        'In Progress',
        'Completed',
    ])


@pytest.mark.asyncio
async def test_updated_at_workbench(
    auth_client_alice: TestClient, session: AsyncSession, workbenches
):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = auth_client_alice.patch(
            '/workbenches/1',
            json={'name': 'Time Updated Workbench'},
        )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    expected = time.replace(microsecond=0).isoformat()
    assert expected.startswith(data['updated_at'][0:16])

    workbench_db = await session.scalar(
        select(Workbench).where(Workbench.id_workbench == data['id_workbench'])
    )

    assert workbench_db is not None
    assert expected.startswith(workbench_db.updated_at.isoformat()[0:16])


@pytest.mark.asyncio
async def test_delete_workbench(
    auth_client_alice: TestClient, session: AsyncSession, workbenches
):
    rsp = auth_client_alice.delete(
        '/workbenches/1',
    )

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    workbench_db = await session.scalar(
        select(Workbench).where(Workbench.id_workbench == 1)
    )

    assert workbench_db is None
