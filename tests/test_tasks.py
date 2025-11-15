from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from freezegun import freeze_time


def test_create_task(client: TestClient, users):
    rsp = client.post(
        '/tasks/',
        json={'title': 'testar o JokerTask', 'done': False},
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert data['id_task'] == 1
    assert data['user_email'] == users[0]['email']
    assert data['title'] == 'testar o JokerTask'
    assert data['done'] is False


def test_create_full_task(client: TestClient, users):
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
        headers={'Authorization': f'Bearer {users[0]["access_token"]}'},
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


def test_created_at_task(client: TestClient, users):
    time = datetime.now(ZoneInfo('UTC'))
    time_str = time.isoformat()
    with freeze_time(time):
        rsp = client.post(
            '/tasks/',
            json={
                'title': 'test_created_at',
                'done': False,
            },
            headers={'Authorization': f'bearer {users[0]["access_token"]}'},
        )

    assert rsp.status_code == HTTPStatus.CREATED

    data = rsp.json()

    assert time_str.startswith(data['created_at'][0:19])


# TODO: Testar updated_at


def test_get_task_by_id(client: TestClient, users, tasks):
    rsp = client.get(
        '/tasks/4',
        headers={'Authorization': f'bearer {users[1]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert tasks[3]['title'] == data['title']
    assert tasks[3]['id_task'] == data['id_task']


def test_get_task_by_id_not_found(client: TestClient, users, tasks):
    rsp = client.get(
        '/tasks/999',
        headers={'Authorization': f'bearer {users[1]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.json()['detail'] == 'task not found'


def test_get_task_by_filter_logic_like(client: TestClient, users, tasks):
    rsp_qnt_elements = 2

    rsp = client.get(
        '/tasks?title=%tes%',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['title'] == tasks[0]['title']
    assert data['responses'][1]['title'] == tasks[1]['title']


def test_get_task_by_filter_logic_exact(client: TestClient, users, tasks):
    rsp_qnt_elements = 2

    rsp = client.get(
        '/tasks?repetition=0111110',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['repetition'] == tasks[0]['repetition']
    assert data['responses'][1]['repetition'] == tasks[1]['repetition']


def test_get_task_by_filter_logic_in_list(client: TestClient, users, tasks):
    rsp_qnt_elements = 2

    rsp = client.get(
        '/tasks?state=ToDo&state=InProgress',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['state'] == tasks[0]['state']
    assert data['responses'][1]['state'] == tasks[1]['state']


def test_get_task_by_filter_logic_range(client: TestClient, users, tasks):
    rsp_qnt_elements = 2

    rsp = client.get(
        '/tasks?priority=40&priority=60',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['priority'] == tasks[0]['priority']
    assert data['responses'][1]['priority'] == tasks[1]['priority']


def test_get_task_by_filter_logic_list_in_list(
    client: TestClient, users, tasks
):
    rsp_qnt_elements = 2

    rsp = client.get(
        '/tasks?tags=test_filters',
        headers={'Authorization': f'bearer {users[0]["access_token"]}'},
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    if data['responses'][0]['id_task'] == tasks[0]['id_task']:
        assert data['responses'][0]['tags'] == tasks[0]['tags']
        assert data['responses'][1]['tags'] == tasks[1]['tags']
    else:
        assert data['responses'][0]['tags'] == tasks[1]['tags']
        assert data['responses'][1]['tags'] == tasks[0]['tags']
