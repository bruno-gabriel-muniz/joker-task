from joker_task.hello_world import hello_world


def test_hello_world():
    assert hello_world() == 'Hello Joker'


def test_hello_world_fastAPI(client):
    assert client.get('/hello_world').json() == {'message': 'hello FastAPI'}
