from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

from freezegun import freeze_time


def test_create_task(client, users):
    rsp = client.post(
        '/tasks/',
        json={'title': 'testar o JokerTask', 'done': False},
        headers={'Authorization': f'Bearer {users[0]["token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['done'] is False


def test_create_full_task(client, users):
    reminder = datetime.now()
    priority = 10

    rsp = client.post(
        '/tasks/',
        json={
            'title': 'testar o JokerTask',
            'description': 'testando agora',
            'done': False,
            'tags': ['test1', 'test2'],
            'reminder': reminder.isoformat(),
            'repetition': '0111110',
            'state': 'TODO',
            'priority': priority,
        },
        headers={'Authorization': f'Bearer {users[0]["token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['description'] == 'testando agora'
    assert data['done'] is False
    assert data['tags'] == ['test1', 'test2']
    assert data['reminder'] == reminder.isoformat()
    assert data['repetition'] == '0111110'
    assert data['state'] == 'TODO'
    assert data['priority'] == priority


def test_created_at_task(client, users):
    time = datetime.now(ZoneInfo('UTC'))
    time_str = time.isoformat()
    with freeze_time(time):
        rsp = client.post(
            '/tasks/',
            json={
                'title': 'test_created_at',
                'done': False,
            },
            headers={'Authorization': f'Bearer {users[0]["token"]}'},
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert time_str.startswith(data['created_at'])


# TODO: Testar updated_at
