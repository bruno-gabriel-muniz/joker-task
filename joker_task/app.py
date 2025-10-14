from http import HTTPStatus

from fastapi import FastAPI

from joker_task.router.auth import auth_router
from joker_task.router.tasks import tasks_router
from joker_task.schemas import Message

app = FastAPI()
app.include_router(auth_router)
app.include_router(tasks_router)


@app.get('/hello_world/', response_model=Message, status_code=HTTPStatus.OK)
def hello_world():
    return {'message': 'helloJoker'}
