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


def test_create_task(client: TestClient, users):
    rsp = client.post(
        '/tasks/',
        json={'title': 'testar o JokerTask', 'done': False},
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['done'] is False


def test_create_full_task(client: TestClient, users):
    reminder = datetime.now()
    priority = 10

    rsp = client.post(
        '/tasks/',
        json={
            'title': 'testar o JokerTask',
            'description': 'testando agora',
            'done': False,
            'tags': ['test1', 'test2'],
            'reminder': reminder.isoformat(),
            'repetition': '0111110',
            'state': 'TODO',
            'priority': priority,
        },
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['description'] == 'testando agora'
    assert data['done'] is False
    assert sorted(data['tags']) == sorted(['test1', 'test2'])
    assert data['reminder'] == reminder.isoformat()
    assert data['repetition'] == '0111110'
    assert data['state'] == 'TODO'
    assert data['priority'] == priority


def test_created_at_task(client: TestClient, users):
    time = datetime.now(ZoneInfo('UTC'))
    time_str = time.isoformat()
    with freeze_time(time):
        rsp = client.post(
            '/tasks/',
            json={
                'title': 'test_created_at',
                'done': False,
            },
            headers={'Authorization': f'bearer {users[0]["access_token"]}'},
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert time_str.startswith(data['created_at'][0:16])


def test_updated_at_task(client: TestClient, users, tasks):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = client.patch(
            '/tasks/4',
            json={'title': 'Tarefa 4 atualizada'},
            headers={'Authorization': f'bearer {users[1]["access_token"]}'},
        )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['updated_at'] is not None
    assert data['updated_at'].startswith(time.isoformat()[0:17])


def test_get_task_by_id(client: TestClient, users, tasks):
    rsp = client.get(
        '/tasks/4',
        headers={'Authorization': f'bearer {users[1]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert tasks[3]['title'] == data['title']
    assert tasks[3]['id_task'] == data['id_task']


@pytest.mark.asyncio
async def test_update_task(
    client: TestClient, users, tasks, session: AsyncSession
):
    id_test = 1
    new_data = {
        'title': f'Tarefa {id_test} atualizada',
        'description': 'Descrição atualizada',
        'done': True,
        'tags_add': ['atualizada1', 'atualizada2'],
        'tags_remove': ['test_none'],
        'tags': ['atualizada1', 'atualizada2', 'test_filters'],
        'repetition': '',
        'priority': 75,
    }

    rsp = client.patch(
        f'/tasks/{id_test}',
        json=new_data,
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )
    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()
    data.pop('updated_at')
    data.pop('created_at')
    data.pop('id_task')
    data.pop('user_email')
    data['tags'] = sorted(data['tags'])

    assert data['state'] == 'InProgress'  # value preserved from before
    assert data['reminder'] is None  # value preserved from before

    data.pop('state')
    data.pop('reminder')

    new_data.pop('tags_add')
    new_data.pop('tags_remove')

    assert data == new_data

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
        new_data['tags']
    )
    assert task_assert.state == 'InProgress'  # value preserved from before
    assert task_assert.priority == new_data['priority']


@pytest.mark.asyncio
async def test_delete_task(
    client: TestClient, session: AsyncSession, users, tasks
):
    rsp = client.delete(
        '/tasks/1',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    is_none = await session.scalar(select(Task).where(Task.id_task == 1))

    assert is_none is None
