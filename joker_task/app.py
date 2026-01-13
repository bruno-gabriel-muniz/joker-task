import sys
from http import HTTPStatus

from fastapi import FastAPI
from loguru import logger

from joker_task.router.auth import auth_router
from joker_task.router.tags import tags_router
from joker_task.router.tasks import tasks_router
from joker_task.router.workbenches import workbenches_router
from joker_task.schemas import Message

logger.remove()
logger.add(
    sys.stdout,
    level='ERROR',
    format='\n<green>{time}</green> | {level} | {message}',
)
logger.add('app.log', level='DEBUG', rotation='1 MB')


logger.info('starting api...')
app = FastAPI()
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(workbenches_router)


@app.get('/hello_world/', response_model=Message, status_code=HTTPStatus.OK)
def hello_world():
    logger.info('test hello_world!')
    return {'message': 'helloJoker'}
