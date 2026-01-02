from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Task, User
from joker_task.interfaces.interfaces import (
    MapperInterface,
    TagControlerInterface,
    TaskCollectorInterface,
    WorkbenchControlerInterface,
)
from joker_task.schemas import (
    Filter,
    ResponseTasks,
    TaskPublic,
    TaskSchema,
    TaskUpdate,
)
from joker_task.service.mapper import Mapper
from joker_task.service.security import get_user
from joker_task.service.tags_controler import TagControler
from joker_task.service.task_collector import TaskCollector
from joker_task.service.workbench_controler import WorkbenchControler

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_User = Annotated[User, Depends(get_user)]
T_Filter = Annotated[Filter, Query()]
T_CollectorTask = Annotated[TaskCollectorInterface, Depends(TaskCollector)]
T_TagControler = Annotated[TagControlerInterface, Depends(TagControler)]
T_WorkbenchControler = Annotated[
    WorkbenchControlerInterface, Depends(WorkbenchControler)
]
T_Mapper = Annotated[MapperInterface, Depends(Mapper)]

tasks_router = APIRouter(prefix='/tasks', tags=['tasks'])


@tasks_router.post(
    '/', response_model=TaskPublic, status_code=HTTPStatus.CREATED
)
async def create_task(  # noqa: PLR0913, PLR0917
    task: TaskSchema,
    session: T_Session,
    user: T_User,
    tag_controler: T_TagControler,
    workbench_controler: T_WorkbenchControler,
    mapper: T_Mapper,
):
    task.tags = await tag_controler.get_or_create_tags(user, task.tags)
    workbenches_db = await workbench_controler.collect_workbenches_by_id(
        user, task.workbenches
    )

    logger.info('creating the new task')
    task_db = Task(
        user_email=user.email,
        user=user,
        title=task.title,
        description=task.description,
        done=task.done or False,
        tags=task.tags,
        reminder=task.reminder,
        repetition=task.repetition,
        state=task.state,
        priority=task.priority,
        workbenches=list(workbenches_db),
    )

    logger.info('saving the task to the db')
    session.add(task_db)

    await session.commit()
    await session.refresh(task_db)

    logger.info('returning the task')
    return mapper.map_task_public(task_db)


@tasks_router.get(
    '/{id_task}', response_model=TaskPublic, status_code=HTTPStatus.OK
)
async def get_task_by_id(
    id_task: int,
    user: T_User,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    logger.info('collecting tasks by id')
    task = await collector.collect_task_by_id(user, id_task)
    return mapper.map_task_public(task)


@tasks_router.get('/', response_model=ResponseTasks, status_code=HTTPStatus.OK)
async def get_tasks_by_filters(
    filter: T_Filter,
    user: T_User,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    logger.info('collecting task by filters')

    tasks = await collector.collect_task_by_filter(user, filter)

    tasks_rsp = [mapper.map_task_public(task) for task in tasks]

    return {'responses': tasks_rsp}


@tasks_router.patch(
    '/{id}', response_model=TaskPublic, status_code=HTTPStatus.OK
)
async def update_task(  # noqa: PLR0913, PLR0917
    id: int,
    task: TaskUpdate,
    user: T_User,
    session: T_Session,
    tag_controler: T_TagControler,
    workbench_controler: T_WorkbenchControler,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    task_db = await collector.collect_task_by_id(user, id)

    logger.info(f'updating task with id = {id}')

    await tag_controler.update_tags_of_task(
        user, task_db, task.tags_add, task.tags_remove
    )
    task.tags_add = task.tags_remove = None

    await workbench_controler.update_workbenches_of_task(
        user, task_db, task.workbenches_add, task.workbenches_remove
    )
    task.workbenches_add = task.workbenches_remove = None

    for key, value in task.model_dump(
        exclude_unset=True, exclude_none=True
    ).items():
        setattr(task_db, key, value)

    logger.info('updating db')
    session.add(task_db)

    await session.commit()
    await session.refresh(task_db)

    return mapper.map_task_public(task_db)


@tasks_router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_task(
    id: int,
    user: T_User,
    session: T_Session,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    task_db = await collector.collect_task_by_id(user, id)

    logger.info(f'deleting task with id  = {id}')
    await session.delete(task_db)
    await session.commit()
