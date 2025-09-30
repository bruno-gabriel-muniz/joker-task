from fastapi import FastAPI

from joker_task.schemas import Message

app = FastAPI()


@app.get('/hello_world', response_model=Message)
def hello_world():
    return {'message': 'hello FastAPI'}
