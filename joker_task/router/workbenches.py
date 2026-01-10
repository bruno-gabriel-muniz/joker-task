from http import HTTPStatus

from fastapi import APIRouter

from joker_task.db.models import Workbench
from joker_task.schemas import (
    WorkbenchPublic,
    WorkbenchSchema,
    WorkbenchUpdate,
    WorkbenchWithTasks,
)
from joker_task.service.dependencies import (
    T_Mapper,
    T_Session,
    T_User,
    T_WorkbenchControler,
)

workbenches_router = APIRouter(prefix='/workbenches', tags=['workbenches'])


@workbenches_router.post(
    '/', response_model=WorkbenchPublic, status_code=HTTPStatus.CREATED
)
async def create_workbench(
    workbench: WorkbenchSchema,
    user: T_User,
    workbench_ctrl: T_WorkbenchControler,
    session: T_Session,
    mapper: T_Mapper,
):
    await workbench_ctrl.check_workbench_name_exists(user, workbench.name)

    workbench_db = Workbench(
        user_email=user.email,
        user=user,
        name=workbench.name,
        columns=sorted(workbench.columns),
    )
    session.add(workbench_db)
    await session.commit()
    await session.refresh(workbench_db)

    return mapper.map_workbench_public(workbench_db)


@workbenches_router.get(
    '/', response_model=list[WorkbenchPublic], status_code=HTTPStatus.OK
)
async def list_workbenches(
    user: T_User, workbench_ctrl: T_WorkbenchControler, mapper: T_Mapper
):
    workbenches_db = await workbench_ctrl.collect_workbenches(user)

    return [
        mapper.map_workbench_public(workbench) for workbench in workbenches_db
    ]


@workbenches_router.get(
    '/{id}',
    response_model=WorkbenchWithTasks,
    status_code=HTTPStatus.OK,
)
async def get_workbench(
    id: int,
    user: T_User,
    workbench_ctrl: T_WorkbenchControler,
    mapper: T_Mapper,
):
    workbench_db = await workbench_ctrl.collect_workbench_by_id(user, id)

    return {
        'workbench': mapper.map_workbench_public(workbench_db),
        'tasks': [mapper.map_task_public(task) for task in workbench_db.tasks],
    }


@workbenches_router.patch(
    '/{id}', response_model=WorkbenchPublic, status_code=HTTPStatus.OK
)
async def update_workbench(  # noqa: PLR0913, PLR0917
    id: int,
    workbench: WorkbenchUpdate,
    user: T_User,
    session: T_Session,
    workbench_ctrl: T_WorkbenchControler,
    mapper: T_Mapper,
):
    workbench_db = await workbench_ctrl.collect_workbench_by_id(user, id)

    updated_columns = {column for column in workbench_db.columns}
    if workbench.columns_add:
        updated_columns.update(workbench.columns_add)
    if workbench.columns_remove:
        updated_columns.difference_update(workbench.columns_remove)
    workbench_db.columns = sorted(list(updated_columns))

    if workbench.name and workbench.name != workbench_db.name:
        await workbench_ctrl.check_workbench_name_exists(user, workbench.name)
        workbench_db.name = workbench.name

    session.add(workbench_db)
    await session.commit()
    await session.refresh(workbench_db)

    return mapper.map_workbench_public(workbench_db)


@workbenches_router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_workbench(
    id: int,
    user: T_User,
    session: T_Session,
    workbench_ctrl: T_WorkbenchControler,
):
    workbench_db = await workbench_ctrl.collect_workbench_by_id(user, id)

    await session.delete(workbench_db)
    await session.commit()
