from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from joker_task.db.models import View


@pytest.mark.asyncio
async def test_post_view_with_full_filter(
    client: TestClient, users: list[dict], session: AsyncSession
):
    reminder_spec = [
        datetime.now().isoformat(),
        (datetime.now() + timedelta(days=1)).isoformat(),
    ]

    rsp = client.post(
        '/views/',
        json={
            'name': 'Minha View',
            'filters': [
                {
                    'title': 'Tarefa 1',
                    'description': 'Descrição da tarefa 1',
                    'done': False,
                    'tags': ['tag1', 'tag2'],
                    'reminder': reminder_spec,
                    'repetition': None,
                    'state': ['DONE'],
                    'priority': [10, 20],
                },
            ],
        },
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_view'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['name'] == 'Minha View'
    assert len(data['filters']) == 1

    filter_data = data['filters'][0]

    assert filter_data['title'] == 'Tarefa 1'
    assert filter_data['description'] == 'Descrição da tarefa 1'
    assert filter_data['done'] is False
    assert filter_data['tags'] == ['tag1', 'tag2']
    assert filter_data['reminder'] == reminder_spec
    assert filter_data['repetition'] is None
    assert filter_data['state'] == ['DONE']
    assert filter_data['priority'] == [10, 20]

    view_db = await session.scalar(
        select(View)
        .where(View.id_view == data['id_view'])
        .options(selectinload(View.filters)),
    )

    assert view_db is not None
    assert view_db.name == 'Minha View'
    assert view_db.user_email == users[0]['email']
    assert len(view_db.filters) == 1

    filter_db = view_db.filters[0]

    assert filter_db.title == 'Tarefa 1'
    assert filter_db.description == 'Descrição da tarefa 1'
    assert filter_db.done is False
    assert filter_db.tags == ['tag1', 'tag2']
    assert filter_db.reminder == reminder_spec
    assert filter_db.repetition is None
    assert filter_db.state == ['DONE']
    assert filter_db.priority == [10, 20]


def test_post_view_with_filter_empty(client: TestClient, users: list[dict]):
    rsp = client.post(
        '/views/',
        json={
            'name': 'Minha View Vazia',
            'filters': [{'title': 'None'}],
        },
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_view'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['name'] == 'Minha View Vazia'
    assert len(data['filters']) == 1

    assert data['filters'][0]['title'] == 'None'


def test_post_view_with_conflicting_name(
    client: TestClient, users: list[dict], views: list[dict]
):
    rsp = client.post(
        '/views/',
        json={
            'name': views[0]['name'],
            'filters': [],
        },
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'view with this name already exists'


def test_get_views(client: TestClient, users: list[dict], views: list[dict]):
    rsp = client.get(
        '/views/',
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()
    views_alice = [
        view for view in views if view['user_email'] == users[0]['email']
    ]

    assert len(data) == len(views_alice)
    assert data[0]['id_view'] == views_alice[0]['id_view']
    assert data[1]['id_view'] == views_alice[1]['id_view']

    assert data[0]['name'] == views_alice[0]['name']
    assert data[1]['name'] == views_alice[1]['name']

    assert data[0]['user_email'] == views_alice[0]['user_email']
    assert data[1]['user_email'] == views_alice[1]['user_email']


def test_get_view_by_id(
    client: TestClient, users: list[dict], views: list[dict]
):
    view = views[0]

    rsp = client.get(
        f'/views/{view["id_view"]}',
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_view'] == view['id_view']
    assert data['user_email'] == view['user_email']
    assert data['name'] == view['name']


def test_get_view_by_id_not_found(client: TestClient, users: list[dict]):
    rsp = client.get(
        '/views/999',
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'


def test_get_view_by_id_other_user(
    client: TestClient, users: list[dict], views: list[dict]
):
    view = views[0]

    rsp = client.get(
        f'/views/{view["id_view"]}',
        headers={'Authorization': f'Bearer {users[1]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'
