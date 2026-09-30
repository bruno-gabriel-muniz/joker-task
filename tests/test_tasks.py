from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from joker_task.db.models import Task


@pytest.mark.asyncio
async def test_create_task(
    auth_client_alice: TestClient, session: AsyncSession, users
):
    rsp = auth_client_alice.post(
        '/tasks/',
        json={'title': 'testar o JokerTask', 'done': False},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['done'] is False

    task_db = await session.scalar(
        select(Task).where(Task.id_task == data['id_task'])
    )

    assert task_db is not None
    assert task_db.title == data['title']


def test_create_full_task(auth_client_alice: TestClient, users, workbenches):
    reminder = datetime.now()
    priority = 10

    rsp = auth_client_alice.post(
        '/tasks/',
        json={
            'title': 'testar o JokerTask',
            'description': 'testando agora',
            'done': False,
            'tags': [
                {'name': 'test1', 'color_hex': '#888888'},
                {'name': 'test2'},
            ],
            'workbenches': [1, 2],
            'reminder': reminder.isoformat(),
            'repetition': '0111110',
            'state': 'TODO',
            'priority': priority,
        },
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['description'] == 'testando agora'
    assert data['done'] is False
    assert data['tags'] is not None
    if data['tags'][0]['name'] == 'test1':
        assert data['tags'][0]['color_hex'] == '#888888'
        assert data['tags'][1]['name'] == 'test2'
        assert data['tags'][1]['color_hex'] is None
    else:
        assert data['tags'][1]['color_hex'] == '#888888'
        assert data['tags'][1]['name'] == 'test1'
        assert data['tags'][0]['color_hex'] is None
        assert data['tags'][0]['name'] == 'test2'
    assert sorted(data['workbenches']) == [1, 2]
    assert data['reminder'] == reminder.isoformat()
    assert data['repetition'] == '0111110'
    assert data['state'] == 'TODO'
    assert data['priority'] == priority


def test_created_at_task(auth_client_alice: TestClient):
    time = datetime.now(ZoneInfo('UTC'))
    time_str = time.isoformat()
    with freeze_time(time):
        rsp = auth_client_alice.post(
            '/tasks/',
            json={
                'title': 'test_created_at',
                'done': False,
            },
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert time_str.startswith(data['created_at'][0:16])


def test_updated_at_task(auth_client_alice: TestClient, tasks):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = auth_client_alice.patch(
            '/tasks/1',
            json={'title': 'Tarefa 1 atualizada'},
        )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['updated_at'] is not None
    assert data['updated_at'].startswith(time.isoformat()[0:17])


def test_get_task_by_id(auth_client_alice: TestClient, tasks):
    rsp = auth_client_alice.get(
        '/tasks/1',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert tasks[0]['title'] == data['title']
    assert tasks[0]['id_task'] == data['id_task']


@pytest.mark.asyncio
async def test_update_task(
    auth_client_alice: TestClient, tasks, session: AsyncSession
):
    id_test = 1
    new_data = {
        'title': f'Tarefa {id_test} atualizada',
        'description': 'Descrição atualizada',
        'done': True,
        'tags_add': [{'name': 'atualizada1'}, {'name': 'atualizada2'}],
        'tags_remove': [{'name': 'test_none'}],
        'workbenches_add': [1],
        'workbenches_remove': [2],
        'workbenches': [1],
        'repetition': '',
        'priority': 75,
    }

    rsp = auth_client_alice.patch(
        f'/tasks/{id_test}',
        json=new_data,
    )
    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()
    data.pop('updated_at')
    data.pop('created_at')
    data.pop('id_task')
    data.pop('user_email')
    rsp_tags = data.pop('tags')

    espec_tags = [
        {'name': 'atualizada1'},
        {'name': 'atualizada2'},
        {'name': 'test_filters', 'color_hex': '#000000'},
    ]

    assert data['state'] == 'InProgress'  # value preserved from before
    assert data['reminder'] is None  # value preserved from before

    data.pop('state')
    data.pop('reminder')

    new_data.pop('tags_add')
    new_data.pop('tags_remove')
    new_data.pop('workbenches_add')
    new_data.pop('workbenches_remove')

    assert data == new_data

    assert rsp_tags is not None
    assert len(rsp_tags) == len(espec_tags)
    assert sorted(tag['name'] for tag in rsp_tags) == sorted([
        tag['name'] for tag in espec_tags
    ])

    task_assert = await session.scalar(
        select(Task)
        .options(selectinload(Task.tags))
        .where(Task.id_task == id_test)
    )
    assert task_assert

    assert task_assert.title == new_data['title']
    assert task_assert.description == new_data['description']
    assert task_assert.done is True
    assert sorted(tag.name for tag in task_assert.tags) == sorted(
        tag['name'] for tag in espec_tags
    )
    assert task_assert.state == 'InProgress'  # value preserved from before
    assert task_assert.priority == new_data['priority']


@pytest.mark.asyncio
async def test_delete_task(
    auth_client_alice: TestClient, session: AsyncSession, tasks
):
    rsp = auth_client_alice.delete('/tasks/1')

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    is_none = await session.scalar(select(Task).where(Task.id_task == 1))

    assert is_none is None
