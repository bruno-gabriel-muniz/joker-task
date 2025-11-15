from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from joker_task.service.security import (
    generate_access_token,
    get_hash_password,
    verify_password,
)


def test_get_and_verify_password():
    assert verify_password('oi', get_hash_password('oi'))


def test_get_user_invalid_token(client: TestClient):
    with freeze_time(timedelta(days=1) + datetime.now()):
        rsp = client.put(
            '/update_user/',
            json={'username': 'bob', 'password': 'secret'},
            headers={'Authorization': 'bearer not-valid'},
        )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    data = rsp.json()

    assert data['detail'] == 'could not validate credentials'


def test_get_user_token_expired(client: TestClient, users):
    with freeze_time(timedelta(days=1) + datetime.now()):
        rsp = client.put(
            '/update_user/',
            json={'username': 'bob', 'password': 'secret'},
            headers={'Authorization': f'bearer {users[1]["access_token"]}'},
        )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    data = rsp.json()

    assert data['detail'] == 'could not validate credentials'


def test_get_user_token_without_user(client: TestClient):
    rsp = client.put(
        '/update_user/',
        json={'username': 'bob', 'password': 'secret'},
        headers={'Authorization': f'bearer {generate_access_token({})}'},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    data = rsp.json()

    assert data['detail'] == 'could not validate credentials'


def test_get_user_token_with_fake_user(client: TestClient):
    rsp = client.put(
        '/update_user/',
        json={'username': 'bob', 'password': 'secret'},
        headers={
            'Authorization': f'bearer {
                generate_access_token({"sub": "not-have-data-in-db"})
            }'
        },
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    data = rsp.json()

    assert data['detail'] == 'could not validate credentials'
