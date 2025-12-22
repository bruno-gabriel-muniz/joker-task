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
