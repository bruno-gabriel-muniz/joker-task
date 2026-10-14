from datetime import date, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient


def test_update_task_occurrences_rejects_invalid_date(
    auth_client_alice: TestClient, tasks
):
    response = auth_client_alice.patch(
        '/tasks/1',
        json={'occurrences_add': {'not-a-date': True}},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_task_occurrences_rejects_date_collision_in_request(
    auth_client_alice: TestClient, tasks
):
    collision_date = (date.today() + timedelta(days=1)).isoformat()
    response = auth_client_alice.patch(
        '/tasks/1',
        json={
            'occurrences_add': {collision_date: True},
            'occurrences_update': {collision_date: False},
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'occurrence dates conflict in request'


def test_update_task_occurrences_rejects_date_already_in_database(
    auth_client_alice: TestClient, tasks, occurrences
):
    existing_date = occurrences[0]['occurrence_date'].isoformat()
    response = auth_client_alice.patch(
        '/tasks/1',
        json={'occurrences_add': {existing_date: False}},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'occurrence date already exists'


def test_user_cannot_update_another_users_task_occurrences(
    auth_client_bob: TestClient, tasks, occurrences
):
    existing_date = occurrences[0]['occurrence_date'].isoformat()
    response = auth_client_bob.patch(
        '/tasks/1',
        json={'occurrences_update': {existing_date: False}},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'task not found'
