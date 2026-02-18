from http import HTTPStatus

from fastapi import APIRouter

from joker_task.schemas import ViewPublic, ViewSchema, ViewSoft
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


@views_router.get('/', response_model=list[ViewSoft])
async def list_views(
    user: T_User,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    views_db = await view_srv.list_views(user)

    return [mapper.map_view_soft(view_db) for view_db in views_db]


@views_router.get('/{id}', response_model=ViewPublic)
async def get_view(
    id: int,
    user: T_User,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    view_db = await view_srv.get_view_by_id(user, id)

    return mapper.map_view_public(view_db)
