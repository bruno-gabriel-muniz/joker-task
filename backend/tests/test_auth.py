from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time


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


def test_login(client: TestClient, users):
    rsp = client.post(
        '/login/',
        data={'username': users[0]['email'], 'password': users[0]['password']},
    )

    assert rsp.status_code == HTTPStatus.OK
    assert rsp.cookies.get('access_token') is not None
    assert rsp.cookies.get('refresh_token') is not None


def test_login_unauthorized(client: TestClient, users):
    rsp = client.post(
        '/login/',
        data={'username': users[0]['email'], 'password': 'wrong_password'},
    )

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'invalid email or password'


def test_refresh(auth_client_alice: TestClient):
    token_before = auth_client_alice.cookies.get('access_token')

    with freeze_time(datetime.now() + timedelta(minutes=20)):
        rsp = auth_client_alice.post(
            '/refresh/',
            cookies={
                'refresh_token': auth_client_alice.cookies['refresh_token']
            },
        )

    assert rsp.status_code == HTTPStatus.OK
    assert rsp.cookies.get('access_token') is not None
    assert rsp.cookies.get('access_token') != token_before


def test_refresh_invalid(client: TestClient):
    rsp = client.post('/refresh/')

    assert rsp.status_code == HTTPStatus.UNAUTHORIZED
    assert rsp.json()['detail'] == 'missing refresh token'


def test_logout(auth_client_alice: TestClient):
    rsp = auth_client_alice.post('/logout/')

    assert rsp.status_code == HTTPStatus.OK
    assert rsp.cookies.get('access_token') is None
    assert rsp.cookies.get('refresh_token') is None


def test_update_user(auth_client_alice: TestClient):
    rsp = auth_client_alice.put(
        '/update_user/',
        json={'username': 'alice2', 'password': 'secret'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['username'] == 'alice2'
    assert 'password' not in data


def test_update_user_conflict(auth_client_bob: TestClient):
    rsp = auth_client_bob.put(
        '/update_user/',
        json={'username': 'alice', 'password': 'euSouOBob'},
    )

    assert rsp.status_code == HTTPStatus.CONFLICT

    data = rsp.json()

    assert data['detail'] == 'username is already in use'
