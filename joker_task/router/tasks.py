from http import HTTPStatus

from fastapi import APIRouter

from joker_task.db.models import Task
from joker_task.schemas import (
    ResponseTasks,
    TaskPublic,
    TaskSchema,
    TaskUpdate,
)
from joker_task.service.dependencies import (
    T_CollectorTask,
    T_Filter,
    T_Mapper,
    T_Session,
    T_TagController,
    T_User,
    T_WorkbenchController,
)

tasks_router = APIRouter(prefix='/tasks', tags=['tasks'])


@tasks_router.post(
    '/', response_model=TaskPublic, status_code=HTTPStatus.CREATED
)
async def create_task(  # noqa: PLR0913, PLR0917
    task: TaskSchema,
    session: T_Session,
    user: T_User,
    tag_controler: T_TagController,
    workbench_controler: T_WorkbenchController,
    mapper: T_Mapper,
):
    tags_db = await tag_controler.get_or_create_tags(user, task.tags)
    workbenches_db = await workbench_controler.collect_workbenches_by_id(
        user, task.workbenches
    )

    task_db = Task(
        user_email=user.email,
        user=user,
        title=task.title,
        description=task.description,
        done=task.done or False,
        tags=tags_db,
        workbenches=list(workbenches_db),
        reminder=task.reminder,
        repetition=task.repetition,
        state=task.state,
        priority=task.priority,
    )

    session.add(task_db)

    await session.commit()
    await session.refresh(task_db)

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
    task = await collector.collect_task_by_id(user, id_task)
    return mapper.map_task_public(task)


@tasks_router.get('/', response_model=ResponseTasks, status_code=HTTPStatus.OK)
async def get_tasks_by_filters(
    filter: T_Filter,
    user: T_User,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
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
    tag_controler: T_TagController,
    workbench_controler: T_WorkbenchController,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    task_db = await collector.collect_task_by_id(user, id)

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

    await session.delete(task_db)
    await session.commit()
