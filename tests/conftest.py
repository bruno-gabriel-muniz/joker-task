import pytest
from fastapi.testclient import TestClient

from joker_task.joker_task import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
