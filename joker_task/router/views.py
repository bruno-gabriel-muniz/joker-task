from http import HTTPStatus

from fastapi import APIRouter

from joker_task.schemas import ViewPublic, ViewSchema
from joker_task.service.dependencies import (
    T_Mapper,
    T_Session,
    T_User,
    T_ViewService,
)

views_router = APIRouter(prefix='/views', tags=['views'])


@views_router.post(
    '/', response_model=ViewPublic, status_code=HTTPStatus.CREATED
)
async def create_view(
    view: ViewSchema,
    user: T_User,
    session: T_Session,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    view_db = await view_srv.create_view(user, view)

    await session.commit()
    await session.refresh(view_db, attribute_names=['filters'])

    return mapper.map_view_public(view_db)
