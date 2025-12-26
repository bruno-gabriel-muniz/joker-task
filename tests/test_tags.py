from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.models import Tag


@pytest.mark.asyncio
async def test_create_tags(
    client: TestClient, session: AsyncSession, tags, users
):
    expected_total_tags = 3
    rsp = client.post(
        '/tags',
        json={'names': ['test1', tags[0]['name']]},
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    returned = {tag['name']: tag for tag in data}

    assert tags[0]['name'] in returned
    assert 'test1' in returned

    assert returned[tags[0]['name']]['id_tag'] == tags[0]['id_tag']
    assert returned['test1']['id_tag'] == expected_total_tags

    tags_db = await session.scalars(select(Tag).order_by(Tag.id_tag))
    tags_db = tags_db.all()

    assert len(tags_db) == expected_total_tags


def test_created_at_tag(client: TestClient, users):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = client.post(
            '/tags',
            json={'names': ['test1']},
            headers={'Authorization': f'bearer {users[0]["access_token"]}'},
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    expected = time.replace(microsecond=0).isoformat()
    assert expected[:-1].startswith(data[0]['updated_at'])
    assert expected[:-1].startswith(data[0]['created_at'])


def test_list_tags(client: TestClient, users, tags):
    rsp = client.get(
        '/tags',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    returned = {tag['name']: tag for tag in data}

    assert tags[0]['name'] in returned
    assert tags[1]['name'] in returned

    assert returned[tags[0]['name']]['id_tag'] == tags[0]['id_tag']
    assert returned[tags[1]['name']]['id_tag'] == tags[1]['id_tag']


@pytest.mark.asyncio
async def test_update_tag(
    client: TestClient, session: AsyncSession, users, tags
):
    new_name = 'updated_name'
    rsp = client.patch(
        f'/tags/{tags[0]["id_tag"]}',
        json={'name': new_name},
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_tag'] == tags[0]['id_tag']
    assert data['name'] == new_name

    tag_db = await session.scalar(
        select(Tag).where(Tag.id_tag == tags[0]['id_tag'])
    )

    assert tag_db is not None
    assert tag_db.name == new_name


def test_update_tag_conflict(client: TestClient, users, tags):
    rsp = client.patch(
        f'/tags/{tags[0]["id_tag"]}',
        json={'name': tags[1]['name']},
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.json()['detail'] == 'name already in use'


def test_update_tag_not_found(client: TestClient, users):
    rsp = client.patch(
        '/tags/9999',
        json={'name': 'updated_name'},
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_tag(
    client: TestClient, session: AsyncSession, users, tags, tasks
):
    id_tag = 1
    rsp = client.delete(
        f'/tags/{id_tag}',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    tag_db = await session.scalar(select(Tag).where(Tag.id_tag == id_tag))

    assert tag_db is None


@pytest.mark.asyncio
async def test_delete_tag_not_found(client: TestClient, users, tags, tasks):
    id_tag = 3
    rsp = client.delete(
        f'/tags/{id_tag}',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_tag_not_found_with_incorrect_user(
    client: TestClient, users, tags, tasks
):
    id_tag = 3
    rsp = client.delete(
        f'/tags/{id_tag}',
        headers={'Authorization': f'bearer {users[1]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND
