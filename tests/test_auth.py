from http import HTTPStatus


def test_create_user(client):
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


def test_create_user_invalid(client):
    rsp = client.post('/users/', json={'None': None})

    assert rsp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_user_conflict(client, users):
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
