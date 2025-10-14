from http import HTTPStatus


def test_create_task(client, users):
    rsp = client.post(
        '/tasks/',
        json={'title': 'testar o JokerTask', 'done': False},
        headers={'Authorization': f'bearer {users[0]["token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['done'] is False


# TODO: Testar a criação das tarefas com os outros campos.
# TODO: Testar created_at updated_at
