from http import HTTPStatus

from fastapi import APIRouter

from joker_task.schemas import (
    FilterPublic,
    FilterSchema,
    ViewPublic,
    ViewResult,
    ViewSchema,
    ViewSoft,
    ViewUpdate,
)
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


@views_router.get('/{id_view}', response_model=ViewPublic)
async def get_view(
    id_view: int,
    user: T_User,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    view_db = await view_srv.get_view_by_id(user, id_view)

    return mapper.map_view_public(view_db)


@views_router.get('/{id_view}/tasks', response_model=ViewResult)
async def apply_view(
    id_view: int, user: T_User, view_srv: T_ViewService, mapper: T_Mapper
):
    view_result = await view_srv.apply_view(user, id_view)

    return mapper.map_view_result(view_result)


@views_router.put(
    '/{id_view}', status_code=HTTPStatus.OK, response_model=ViewSoft
)
async def update_view(  # noqa: PLR0913, PLR0917
    id_view: int,
    view: ViewUpdate,
    user: T_User,
    session: T_Session,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    updated_view_db = await view_srv.update_view(user, id_view, view)

    await session.commit()
    await session.refresh(updated_view_db)

    return mapper.map_view_soft(updated_view_db)


@views_router.post(
    '/{id_view}/filters',
    status_code=HTTPStatus.CREATED,
    response_model=FilterPublic,
)
async def post_view_filter(  # noqa: PLR0913, PLR0917
    id_view: int,
    filter_schema: FilterSchema,
    user: T_User,
    session: T_Session,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    filter_db = await view_srv.create_view_filter(user, id_view, filter_schema)

    await session.commit()
    await session.refresh(filter_db)

    return mapper.map_filter_public(filter_db)


@views_router.patch(
    '/{id_view}/filters/{id_filter}',
    status_code=HTTPStatus.OK,
    response_model=FilterPublic,
)
async def update_view_filter(  # noqa: PLR0913, PLR0917
    id_view: int,
    id_filter: int,
    filter_schema: FilterSchema,
    user: T_User,
    session: T_Session,
    view_srv: T_ViewService,
    mapper: T_Mapper,
):
    filter_db = await view_srv.update_view_filter(
        user, id_view, id_filter, filter_schema
    )

    await session.commit()
    await session.refresh(filter_db)

    return mapper.map_filter_public(filter_db)


@views_router.delete(
    '/{id_view}/filters/{id_filter}', status_code=HTTPStatus.NO_CONTENT
)
async def delete_view_filter(
    id_view: int,
    id_filter: int,
    user: T_User,
    session: T_Session,
    view_srv: T_ViewService,
):
    await view_srv.delete_view_filter(user, id_view, id_filter)

    await session.commit()


@views_router.delete('/{id_view}', status_code=HTTPStatus.NO_CONTENT)
async def delete_view(
    id_view: int, user: T_User, session: T_Session, view_srv: T_ViewService
):
    await view_srv.delete_view(user, id_view)
    await session.commit()
