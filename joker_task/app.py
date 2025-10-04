from http import HTTPStatus

from fastapi import FastAPI

from joker_task.router.auth import auth
from joker_task.schemas import Message

app = FastAPI()
app.include_router(auth)


@app.get('/hello_world/', response_model=Message, status_code=HTTPStatus.OK)
def hello_world():
    return {'message': 'helloJoker'}
