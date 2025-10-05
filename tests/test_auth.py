from http import HTTPStatus

from fastapi.testclient import TestClient
from jwt import decode


def test_create_user(client: TestClient):
    rsp = client.post(
        '/users/',
        json={
            'email': 'alice@example.com',
            'username': 'alice',
            'password': 'secret',
        },
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data == {'email': 'alice@example.com', 'username': 'alice'}


def test_create_user_invalid(client: TestClient):
    rsp = client.post('/users/', json={'None': None})

    assert rsp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user_conflict(client: TestClient, users):
    rsp = client.post(
        '/users/',
        json={
            'email': 'bob@example.com',
            'username': 'bob',
            'password': 'abcdef',
        },
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'email or username already in use'


def test_get_access_token(client: TestClient, users, settings):
    rsp = client.post(
        '/token/',
        data={'username': users[0]['email'], 'password': users[0]['password']},
    )

    assert rsp.status_code == HTTPStatus.OK

    data: dict = decode(
        rsp.json()['token'], settings.SECRET_KEY, settings.ALGORITHM
    )

    assert 'exp' in data
    assert data['sub'] == 'alice@example.com'


def test_get_access_token_unauthorized(client: TestClient, users):
    rsp = client.post(
        '/token/', data={'username': users[1]['email'], 'password': 'wrong'}
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    rsp = client.post(
        '/token/',
        data={'username': 'Bob@example.com', 'password': users[1]['password']},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED

    data = rsp.json()

    assert data['detail'] == 'incorrect email or password'
