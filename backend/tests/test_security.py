from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time
from jwt import encode

from joker_task.service.security import (
    get_hash_password,
    verify_password,
)


def test_get_and_verify_password():
    assert verify_password('oi', get_hash_password('oi'))


def test_access_token_without_user(client: TestClient, settings):
    token = encode(
        {'exp': datetime.now() + timedelta(days=1), 'type': 'access'},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )
    rsp = client.put(
        '/update_user/',
        json={'username': 'bob', 'password': 'secret'},
        cookies={'access_token': token},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid access token'


def test_access_token_fake_user(client: TestClient, settings):
    token = encode(
        {
            'exp': datetime.now() + timedelta(days=1),
            'sub': 'fake_user',
            'type': 'access',
        },
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )
    rsp = client.put(
        '/update_user/',
        json={'username': 'bob', 'password': 'secret'},
        cookies={'access_token': token},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid access token'


def test_access_token_invalid_token(client: TestClient):
    with freeze_time(timedelta(days=1) + datetime.now()):
        rsp = client.put(
            '/update_user/',
            json={'username': 'bob', 'password': 'secret'},
            cookies={'access_token': 'fake_token'},
        )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid access token'


def test_access_token_with_wrong_type(client: TestClient, settings):
    token = encode(
        payload={
            'exp': datetime.now() + timedelta(days=1),
            'sub': 'bob',
            'type': 'refresh',
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    rsp = client.put(
        '/update_user/',
        json={'username': 'bob', 'password': 'secret'},
        cookies={'access_token': token},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid access token'


def test_refresh_token_without_user(client: TestClient, settings):
    token = encode(
        {'exp': datetime.now() + timedelta(days=1), 'type': 'refresh'},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    rsp = client.post('/refresh/', cookies={'refresh_token': token})

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid refresh token'


def test_refresh_token_fake_user(client: TestClient, settings):
    token = encode(
        {
            'exp': datetime.now() + timedelta(days=1),
            'sub': 'fake_user',
            'type': 'refresh',
        },
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    rsp = client.post(
        '/refresh/',
        cookies={'refresh_token': token},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid refresh token'


def test_refrsh_token_invalid_token(client: TestClient):
    rsp = client.post('/refresh/', cookies={'refresh_token': 'fake_token'})

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid refresh token'


def test_refresh_token_with_wrong_type(client: TestClient, settings):
    token = encode(
        payload={
            'exp': datetime.now() + timedelta(days=1),
            'sub': 'bob',
            'type': 'access',
        },
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    rsp = client.post(
        '/refresh/',
        cookies={'refresh_token': token},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid refresh token'


def test_refresh_token_expired(client: TestClient, users):
    with freeze_time(datetime.now()):
        cookie = client.post(
            '/login/',
            data={
                'username': users[1]['email'],
                'password': users[1]['password'],
            },
        ).cookies
    with freeze_time(timedelta(hours=16) + datetime.now()):
        rsp = client.put(
            '/update_user/',
            json={'username': 'bob', 'password': 'secret'},
            cookies=cookie,
        )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    data = rsp.json()

    assert data['detail'] == 'not authenticated'
