from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import User, Workbench
from joker_task.interfaces.interfaces import MapperInterface
from joker_task.schemas import WorkbenchPublic, WorkbenchSchema
from joker_task.service.mapper import Mapper
from joker_task.service.security import get_user

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_User = Annotated[User, Depends(get_user)]
T_Mapper = Annotated[MapperInterface, Depends(Mapper)]

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
