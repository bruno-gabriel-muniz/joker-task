from http import HTTPStatus

from fastapi.testclient import TestClient


def test_get_task_by_id_not_found(auth_client_bob: TestClient, tasks):
    rsp = auth_client_bob.get('/tasks/999')

    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.json()['detail'] == 'task not found'


def test_get_task_by_filter_logic_like(auth_client_alice: TestClient, tasks):
    rsp_qnt_elements = 2

    rsp = auth_client_alice.get(
        '/tasks?title=%tes%',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['title'] == tasks[0]['title']
    assert data['responses'][1]['title'] == tasks[1]['title']


def test_get_task_by_filter_logic_exact(auth_client_alice: TestClient, tasks):
    rsp_qnt_elements = 2

    rsp = auth_client_alice.get(
        '/tasks?repetition=0111110',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['repetition'] == tasks[0]['repetition']
    assert data['responses'][1]['repetition'] == tasks[1]['repetition']


def test_get_task_by_filter_logic_in_list(
    auth_client_alice: TestClient, tasks
):
    rsp_qnt_elements = 2

    rsp = auth_client_alice.get(
        '/tasks?state=ToDo&state=InProgress',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['state'] == tasks[0]['state']
    assert data['responses'][1]['state'] == tasks[1]['state']


def test_get_task_by_filter_logic_range(auth_client_alice: TestClient, tasks):
    rsp_qnt_elements = 2

    rsp = auth_client_alice.get('/tasks?priority=40&priority=60')

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    assert data['responses'][0]['priority'] == tasks[0]['priority']
    assert data['responses'][1]['priority'] == tasks[1]['priority']


def test_get_task_by_filter_with_tag(auth_client_alice: TestClient, tasks):
    rsp_qnt_elements = 2

    rsp = auth_client_alice.get(
        '/tasks?tags=test_filters',
    )

    assert rsp.status_code == HTTPStatus.OK

    data = rsp.json()

    assert len(data['responses']) == rsp_qnt_elements
    if data['responses'][0]['id_task'] == tasks[0]['id_task']:
        assert sorted([
            tag['name'] for tag in data['responses'][0]['tags']
        ]) == sorted([tag.name for tag in tasks[0]['tags']])
        assert sorted([
            tag['name'] for tag in data['responses'][1]['tags']
        ]) == sorted([tag.name for tag in tasks[1]['tags']])
    else:
        assert sorted([
            tag['name'] for tag in data['responses'][0]['tags']
        ]) == sorted([tag.name for tag in tasks[1]['tags']])
        assert sorted([
            tag['name'] for tag in data['responses'][1]['tags']
        ]) == sorted([tag.name for tag in tasks[0]['tags']])
