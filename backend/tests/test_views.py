from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from joker_task.db.models import Filter, View


@pytest.mark.asyncio
async def test_post_view_with_full_filter(
    auth_client_alice: TestClient, users: list[dict], session: AsyncSession
):
    reminder_spec = [
        datetime.now().isoformat(),
        (datetime.now() + timedelta(days=1)).isoformat(),
    ]

    rsp = auth_client_alice.post(
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


def test_post_view_without_filter(
    auth_client_alice: TestClient, users: list[dict]
):
    rsp = auth_client_alice.post(
        '/views/',
        json={
            'name': 'Minha View Vazia',
            'filters': [{'title': 'None'}],
        },
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_view'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['name'] == 'Minha View Vazia'
    assert len(data['filters']) == 1

    assert data['filters'][0]['title'] == 'None'


def test_post_view_with_filter_empty(
    auth_client_alice: TestClient, users: list[dict]
):
    rsp = auth_client_alice.post(
        '/views/',
        json={
            'name': 'Minha View Vazia',
            'filters': [{}],
        },
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_view'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['name'] == 'Minha View Vazia'
    assert len(data['filters']) == 1


def test_post_view_with_conflicting_name(
    auth_client_bob: TestClient, views: list[dict]
):
    rsp = auth_client_bob.post(
        '/views/',
        json={
            'name': views[2]['name'],
            'filters': [],
        },
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'view with this name already exists'


def test_get_views(
    auth_client_alice: TestClient, users: list[dict], views: list[dict]
):
    rsp = auth_client_alice.get(
        '/views/',
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


def test_get_view_by_id(auth_client_alice: TestClient, views: list[dict]):
    view = views[0]

    rsp = auth_client_alice.get(f'/views/{view["id_view"]}')

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_view'] == view['id_view']
    assert data['user_email'] == view['user_email']
    assert data['name'] == view['name']


def test_get_view_by_id_not_found(auth_client_bob: TestClient):
    rsp = auth_client_bob.get('/views/999')

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'


def test_get_view_by_id_other_user(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[0]

    rsp = auth_client_bob.get(f'/views/{view["id_view"]}')

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'


def test_get_view_tasks(
    auth_client_alice: TestClient,
    views: list[dict],
    filters: list[dict],
    tasks: list[dict],
):
    view = views[0]

    rsp = auth_client_alice.get(f'/views/{view["id_view"]}/tasks')

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()['result']

    qnt_t_filter_1 = 2
    qnt_t_filter_2 = 1

    assert isinstance(data, dict)
    assert len(data) == len(filters)
    assert len(data['1']) == qnt_t_filter_1
    assert data['1'][0]['id_task'] == 1
    assert data['1'][0]['title'] == 'test'
    assert data['1'][1]['id_task'] == tasks[1]['id_task']
    assert data['1'][1]['title'] == 'a other test'

    assert len(data['2']) == qnt_t_filter_2
    assert data['2'][0]['id_task'] == tasks[2]['id_task']
    assert data['2'][0]['title'] == 'title'


@pytest.mark.asyncio
async def test_update_view(
    auth_client_alice: TestClient,
    session: AsyncSession,
    views: list[dict],
):
    view = views[0]

    rsp = auth_client_alice.put(
        f'/views/{view["id_view"]}',
        json={
            'name': 'Minha View Atualizada',
        },
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_view'] == view['id_view']
    assert data['user_email'] == view['user_email']
    assert data['name'] == 'Minha View Atualizada'

    view_db = await session.scalar(
        select(View).where(View.id_view == view['id_view']),
    )

    assert view_db is not None
    assert view_db.name == 'Minha View Atualizada'


def test_update_view_not_found(auth_client_bob: TestClient):
    rsp = auth_client_bob.put(
        '/views/999',
        json={
            'name': 'Minha View Atualizada',
        },
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'


def test_update_view_other_user(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[0]

    rsp = auth_client_bob.put(
        f'/views/{view["id_view"]}',
        json={
            'name': 'Minha View Atualizada',
        },
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'


def test_update_view_with_conflicting_name(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[2]
    other_view = views[3]

    rsp = auth_client_bob.put(
        f'/views/{view["id_view"]}',
        json={
            'name': other_view['name'],
        },
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'view with this name already exists'


def test_update_view_with_invalid_name(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[2]

    rsp = auth_client_bob.put(
        f'/views/{view["id_view"]}',
        json={
            'name': '',
        },
    )

    assert rsp.status_code == HTTPStatus.BAD_REQUEST

    assert rsp.json()['detail'] == 'name cannot be empty'


@pytest.mark.asyncio
async def test_create_view_filter(
    auth_client_alice: TestClient,
    session: AsyncSession,
    views: list[dict],
    filters: list[dict],
):
    view = views[0]

    rsp = auth_client_alice.post(
        f'/views/{view["id_view"]}/filters',
        json={
            'title': 'Test%',
            'description': '%test%',
            'done': True,
            'tags': ['tag3'],
            'reminder': None,
            'repetition': None,
            'state': ['TODO'],
            'priority': [5, 15],
        },
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()
    id_filter_spec = 3

    assert data['id_filter'] == id_filter_spec
    assert data['title'] == 'Test%'
    assert data['description'] == '%test%'
    assert data['done'] is True
    assert data['tags'] == ['tag3']
    assert data['reminder'] is None
    assert data['repetition'] is None
    assert data['state'] == ['TODO']
    assert data['priority'] == [5, 15]

    view_db = await session.scalar(
        select(View)
        .where(View.id_view == view['id_view'])
        .options(selectinload(View.filters)),
    )

    assert view_db is not None
    assert len(view_db.filters) == len(filters) + 1
    assert view_db.filters[-1].id_filter == id_filter_spec
    assert view_db.filters[-1].title == 'Test%'


@pytest.mark.asyncio
async def test_update_view_filter(
    auth_client_alice: TestClient,
    session: AsyncSession,
    views: list[dict],
    filters: list[dict],
):
    view = views[0]
    filter = filters[0]

    rsp = auth_client_alice.patch(
        f'/views/{view["id_view"]}/filters/{filter["id_filter"]}',
        json={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'done': False,
            'tags': ['tag4'],
            'reminder': None,
            'repetition': None,
            'state': ['IN_PROGRESS'],
            'priority': [1, 10],
        },
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_filter'] == filter['id_filter']
    assert data['title'] == 'Updated Title'
    assert data['description'] == 'Updated Description'
    assert data['done'] is False
    assert data['tags'] == ['tag4']
    assert data['reminder'] is None
    assert data['repetition'] is None
    assert data['state'] == ['IN_PROGRESS']
    assert data['priority'] == [1, 10]

    filter_db = await session.scalar(
        select(Filter).where(
            (Filter.id_view == view['id_view']),
            (Filter.id_filter == filter['id_filter']),
        )
    )

    assert filter_db is not None
    assert filter_db.id_filter == filter['id_filter']
    assert filter_db.title == 'Updated Title'
    assert filter_db.description == 'Updated Description'
    assert filter_db.done is False
    assert filter_db.tags == ['tag4']
    assert filter_db.reminder is None
    assert filter_db.repetition is None
    assert filter_db.state == ['IN_PROGRESS']
    assert filter_db.priority == [1, 10]


def test_update_view_filter_not_found(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[2]

    rsp = auth_client_bob.patch(
        f'/views/{view["id_view"]}/filters/999',
        json={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'done': False,
            'tags': ['tag4'],
            'reminder': None,
            'repetition': None,
            'state': ['IN_PROGRESS'],
            'priority': [1, 10],
        },
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'filter not found'


@pytest.mark.asyncio
async def test_delete_view_filter(
    auth_client_alice: TestClient,
    session: AsyncSession,
    views: list[dict],
    filters: list[dict],
):
    view = views[0]
    filter = filters[0]

    rsp = auth_client_alice.delete(
        f'/views/{view["id_view"]}/filters/{filter["id_filter"]}',
    )

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    view_db = await session.scalar(
        select(View)
        .where(View.id_view == view['id_view'])
        .options(selectinload(View.filters)),
    )

    assert view_db is not None
    assert len(view_db.filters) == len(filters) - 1


def test_delete_view_filter_not_found(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[2]

    rsp = auth_client_bob.delete(
        f'/views/{view["id_view"]}/filters/999',
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'filter not found'


@pytest.mark.asyncio
async def test_delete_view(
    auth_client_alice: TestClient,
    session: AsyncSession,
    views: list[dict],
    filters: list[dict],
):
    view = views[0]

    rsp = auth_client_alice.delete(f'/views/{view["id_view"]}')

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    view_db = await session.scalar(
        select(View).where(View.id_view == view['id_view']),
    )

    assert view_db is None

    filters_db = await session.scalar(
        select(Filter).where(Filter.id_view == view['id_view'])
    )

    assert filters_db is None


def test_delete_view_not_found(auth_client_bob: TestClient):
    rsp = auth_client_bob.delete('/views/999')

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'


def test_delete_view_other_user(
    auth_client_bob: TestClient, views: list[dict]
):
    view = views[0]

    rsp = auth_client_bob.delete(f'/views/{view["id_view"]}')

    assert rsp.status_code == HTTPStatus.NOT_FOUND

    data = rsp.json()

    assert data['detail'] == 'view not found'
