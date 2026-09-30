def test_hello_world(client):
    rsp = client.get('/hello_world')

    assert rsp.json() == {'message': 'helloJoker'}
