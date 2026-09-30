from http import HTTPStatus

from fastapi.testclient import TestClient


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


def test_access_expired_refresh_valid(
    auth_client_alice: TestClient, users, settings
):
    auth_client_alice.cookies.set('access_token', '')

    rsp = auth_client_alice.get('/me')

    assert rsp.status_code == HTTPStatus.OK
    assert rsp.json()['email'] == users[0]['email']


def test_logout(auth_client_alice: TestClient):
    rsp = auth_client_alice.post('/logout/')

    assert rsp.status_code == HTTPStatus.OK
    assert rsp.cookies.get('access_token') is None
    assert rsp.cookies.get('refresh_token') is None


def test_get_me(auth_client_alice: TestClient):
    rsp = auth_client_alice.get('/me/')

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert data['email'] == 'alice@example.com'


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
