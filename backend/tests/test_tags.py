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
    auth_client_alice: TestClient, session: AsyncSession, tags
):
    expected_total_tags = len(tags) + 1
    rsp = auth_client_alice.post(
        '/tags',
        json=[
            {'name': 'test1', 'color_hex': '#000000'},
            {'name': tags[0]['name'], 'color_hex': tags[0]['color_hex']},
        ],
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


def test_create_tags_with_duplicate_names(auth_client_alice: TestClient):
    rsp = auth_client_alice.post(
        '/tags',
        json=[
            {'name': 'test1', 'color_hex': '#000000'},
            {'name': 'test1', 'color_hex': '#FFFFFF'},
        ],
    )

    assert rsp.status_code == HTTPStatus.BAD_REQUEST
    assert rsp.json()['detail'] == 'duplicate tag names in request'


def test_create_tag_with_invalid_color(auth_client_bob: TestClient):
    rsp = auth_client_bob.post(
        '/tags',
        json=[{'name': 'test1', 'color_hex': 'invalid_color'}],
    )

    assert rsp.status_code == HTTPStatus.BAD_REQUEST
    assert rsp.json()['detail'] == 'invalid color_hex format'


def test_created_at_tag(auth_client_alice: TestClient):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = auth_client_alice.post(
            '/tags',
            json=[{'name': 'test1', 'color_hex': '#000000'}],
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    expected = time.replace(microsecond=0).isoformat()
    assert expected.startswith(data[0]['updated_at'][0:16])
    assert expected.startswith(data[0]['created_at'][0:16])


def test_list_tags(auth_client_alice: TestClient, tags):
    rsp = auth_client_alice.get(
        '/tags',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    returned = {tag['name']: tag for tag in data}

    assert tags[0]['name'] in returned
    assert tags[1]['name'] in returned

    assert tags[0]['color_hex'] == returned[tags[0]['name']]['color_hex']
    assert tags[1]['color_hex'] == returned[tags[1]['name']]['color_hex']

    assert returned[tags[0]['name']]['id_tag'] == tags[0]['id_tag']
    assert returned[tags[1]['name']]['id_tag'] == tags[1]['id_tag']


@pytest.mark.asyncio
async def test_update_tag(
    auth_client_alice: TestClient, session: AsyncSession, tags
):
    new_name = 'updated_name'
    rsp = auth_client_alice.patch(
        f'/tags/{tags[0]["id_tag"]}',
        json={'name': new_name, 'color_hex': '#FFFFFF'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['id_tag'] == tags[0]['id_tag']
    assert data['name'] == new_name
    assert data['color_hex'] == '#FFFFFF'

    tag_db = await session.scalar(
        select(Tag).where(Tag.id_tag == tags[0]['id_tag'])
    )

    assert tag_db is not None
    assert tag_db.name == new_name
    assert tag_db.color_hex == '#FFFFFF'


@pytest.mark.asyncio
async def test_update_at_tag(
    auth_client_alice: TestClient, session: AsyncSession, tags
):
    time = datetime.now(ZoneInfo('UTC'))
    with freeze_time(time):
        rsp = auth_client_alice.patch(
            f'/tags/{tags[0]["id_tag"]}',
            json={'name': 'test1'},
        )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    expected = time.replace(microsecond=0).isoformat()
    assert expected.startswith(data['updated_at'][0:16])

    tag_db = await session.scalar(
        select(Tag).where(Tag.id_tag == tags[0]['id_tag'])
    )

    assert tag_db is not None
    assert expected.startswith(
        tag_db.updated_at.replace(microsecond=0).isoformat()[0:16]
    )


def test_update_tag_conflict(auth_client_bob: TestClient, tags):
    rsp = auth_client_bob.patch(
        f'/tags/{tags[2]["id_tag"]}',
        json={'name': tags[3]['name']},
    )

    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.json()['detail'] == 'name already in use'


@pytest.mark.asyncio
async def test_delete_tag(
    auth_client_alice: TestClient, session: AsyncSession, tags
):
    id_tag = 1
    rsp = auth_client_alice.delete(
        f'/tags/{id_tag}',
    )

    assert rsp.status_code == HTTPStatus.NO_CONTENT

    tag_db = await session.scalar(select(Tag).where(Tag.id_tag == id_tag))

    assert tag_db is None


@pytest.mark.asyncio
async def test_delete_tag_not_found(auth_client_bob: TestClient, tags):
    id_tag = len(tags) + 1
    rsp = auth_client_bob.delete(
        f'/tags/{id_tag}',
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_tag_not_found_with_incorrect_user(
    auth_client_bob: TestClient, tags
):
    id_tag = 1
    rsp = auth_client_bob.delete(
        f'/tags/{id_tag}',
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND
