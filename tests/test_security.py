from http import HTTPStatus

from joker_task.security.security import get_hash_password, verify_password


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


def test_get_and_verify_password():
    assert verify_password('oi', get_hash_password('oi'))
