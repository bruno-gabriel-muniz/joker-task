from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Task, User
from joker_task.interfaces.interfaces import TaskCollectorInterface
from joker_task.schemas import Filter, ResponseTasks, TaskPublic, TaskSchema
from joker_task.service.security import get_user
from joker_task.service.task_collector import TaskCollector

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_User = Annotated[User, Depends(get_user)]
T_CollectorTask = Annotated[TaskCollectorInterface, Depends(TaskCollector)]
T_Filter = Annotated[Filter, Query()]

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


@tasks_router.get(
    '/{id_task}', response_model=TaskPublic, status_code=HTTPStatus.OK
)
async def get_task_by_id(
    id_task: int,
    user: T_User,
    collector: T_CollectorTask,
):
    logger.info('collecting tasks by id')
    task = await collector.collect_task_by_id(user, id_task)
    return task


@tasks_router.get('/', response_model=ResponseTasks, status_code=HTTPStatus.OK)
async def get_tasks_by_filters(
    filter: T_Filter,
    user: T_User,
    collector: T_CollectorTask,
):
    logger.info('collecting task by filters')

    tasks = await collector.collect_task_by_filter(user, filter)

    return {'responses': tasks}


@tasks_router.patch(
    '/{id}', response_model=TaskPublic, status_code=HTTPStatus.OK
)
async def update_task(
    id: int,
    task: TaskSchema,
    user: T_User,
    session: T_Session,
    collector: T_CollectorTask,
):
    task_db = await collector.collect_task_by_id(user, id)

    for key, value in task.model_dump().items():
        setattr(task_db, key, value)
    session.add(task_db)

    await session.commit()
    await session.refresh(task_db)

    return task_db


@tasks_router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_task(
    id: int, user: T_User, session: T_Session, collector: T_CollectorTask
):
    task_db = await collector.collect_task_by_id(user, id)

    await session.delete(task_db)
    await session.commit()
