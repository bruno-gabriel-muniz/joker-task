from http import HTTPStatus

from fastapi import APIRouter

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
    T_OccurrenceService,
    T_Session,
    T_TagService,
    T_TaskService,
    T_User,
    T_WorkbenchService,
)

tasks_router = APIRouter(prefix='/tasks', tags=['tasks'])


@tasks_router.post(
    '/', response_model=TaskPublic, status_code=HTTPStatus.CREATED
)
async def create_task(  # noqa: PLR0913, PLR0917
    task: TaskSchema,
    session: T_Session,
    user: T_User,
    tag_srv: T_TagService,
    task_srv: T_TaskService,
    occurrence_srv: T_OccurrenceService,
    workbench_srv: T_WorkbenchService,
    mapper: T_Mapper,
):
    tags_db = await tag_srv.get_or_create_tags(user, task.tags)
    workbenches_db = await workbench_srv.collect_workbenches_by_id(
        user, task.workbenches
    )

    task_db = await task_srv.create_task(user, task, tags_db, workbenches_db)

    occurrences = await occurrence_srv.create_occurrences_of_task(
        task_db, task.occurrences
    )

    session.add_all(occurrences)
    session.add(task_db)

    await session.commit()
    await session.refresh(task_db)
    occurrences = await occurrence_srv.get_occurrences_of_task(task_db)

    return mapper.map_task_public(task_db, occurrences)


@tasks_router.get(
    '/{id_task}', response_model=TaskPublic, status_code=HTTPStatus.OK
)
async def get_task_by_id(
    id_task: int,
    user: T_User,
    occurrence_srv: T_OccurrenceService,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    task = await collector.collect_task_by_id(user, id_task)
    occurrences = await occurrence_srv.get_occurrences_of_task(task)
    return mapper.map_task_public(task, occurrences or [])


@tasks_router.get('/', response_model=ResponseTasks, status_code=HTTPStatus.OK)
async def get_tasks_by_filters(
    filter: T_Filter,
    user: T_User,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    tasks = await collector.collect_task_by_filter(user, filter)
    tasks_rsp = [
        mapper.map_task_public(task, task.occurrences) for task in tasks
    ]

    return {'responses': tasks_rsp}


@tasks_router.patch(
    '/{id}', response_model=TaskPublic, status_code=HTTPStatus.OK
)
async def update_task(  # noqa: PLR0913, PLR0917
    id: int,
    task: TaskUpdate,
    user: T_User,
    session: T_Session,
    tag_srv: T_TagService,
    task_srv: T_TaskService,
    occurrence_srv: T_OccurrenceService,
    workbench_srv: T_WorkbenchService,
    collector: T_CollectorTask,
    mapper: T_Mapper,
):
    task_db = await collector.collect_task_by_id(user, id)

    await occurrence_srv.validate_occurrence_changes(
        task_db,
        task.occurrences_add,
        task.occurrences_update,
        task.occurrences_remove,
    )

    await tag_srv.update_tags_of_task(
        user, task_db, task.tags_add, task.tags_remove
    )
    task.tags_add = task.tags_remove = None

    await workbench_srv.update_workbenches_of_task(
        user, task_db, task.workbenches_add, task.workbenches_remove
    )
    task.workbenches_add = task.workbenches_remove = None

    new_occurrences = await occurrence_srv.create_occurrences_of_task(
        task_db, task.occurrences_add
    )

    await occurrence_srv.update_occurrences_of_task(
        task_db, task.occurrences_update
    )

    await occurrence_srv.remove_occurrences_of_task(
        task_db, task.occurrences_remove
    )

    await task_srv.update_task(task_db, task)

    occurrences = await occurrence_srv.get_occurrences_of_task(task_db)

    session.add(task_db)
    session.add_all(new_occurrences)
    session.add_all(occurrences)

    await session.commit()
    await session.refresh(task_db)
    occurrences = await occurrence_srv.get_occurrences_of_task(task_db)

    return mapper.map_task_public(task_db, occurrences or [])


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
