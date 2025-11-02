from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Task, User
from joker_task.schemas import TaskPublic, TaskSchema
from joker_task.service.security import get_user

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_User = Annotated[User, Depends(get_user)]

tasks_router = APIRouter(prefix='/tasks', tags=['tasks'])


@tasks_router.post(
    '/', response_model=TaskPublic, status_code=HTTPStatus.CREATED
)
async def create_task(task: TaskSchema, session: T_Session, user: T_User):
    logger.info('creating the new task')
    task_db = Task(
        user_email=user.email,
        user=user,
        title=task.title,
        description=task.description,
        done=task.done,
        tags=task.tags,
        reminder=task.reminder,
        repetition=task.repetition,
        state=task.state,
        priority=task.priority,
    )

    logger.info('saving the task to the db')
    session.add(task_db)
    await session.commit()
    await session.refresh(task_db)

    logger.info('returning the task')
    return task_db
