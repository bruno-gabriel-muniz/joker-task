from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from joker_task.db.models import Workbench
from joker_task.schemas import WorkbenchPublic, WorkbenchSchema
from joker_task.service.dependencies import T_Mapper, T_Session, T_User

workbenches_router = APIRouter(prefix='/workbenches', tags=['workbenches'])


@workbenches_router.post(
    '/', response_model=WorkbenchPublic, status_code=HTTPStatus.CREATED
)
async def create_workbench(
    workbench: WorkbenchSchema,
    user: T_User,
    session: T_Session,
    mapper: T_Mapper,
):
    have_conflict = await session.scalar(
        select(Workbench).where(
            Workbench.name == workbench.name,
            Workbench.user_email == user.email,
        )
    )
    if have_conflict:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='workbench name already in use'
        )

    workbench_db = Workbench(
        user_email=user.email,
        user=user,
        name=workbench.name,
        columns=workbench.columns,
    )
    session.add(workbench_db)
    await session.commit()
    await session.refresh(workbench_db)

    return mapper.map_workbench_public(workbench_db)


@workbenches_router.get(
    '/', response_model=list[WorkbenchPublic], status_code=HTTPStatus.OK
)
async def list_workbenches(user: T_User, session: T_Session, mapper: T_Mapper):
    workbenches_db = (
        await session.scalars(
            select(Workbench).where(Workbench.user_email == user.email)
        )
    ).all()

    return [
        mapper.map_workbench_public(workbench) for workbench in workbenches_db
    ]
