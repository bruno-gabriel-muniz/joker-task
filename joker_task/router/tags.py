from http import HTTPStatus

from fastapi import APIRouter

from joker_task.schemas import (
    TagPublic,
    TagsSchema,
    TagUpdate,
)
from joker_task.service.dependencies import (
    T_Mapper,
    T_Session,
    T_TagService,
    T_User,
)

tags_router = APIRouter(prefix='/tags', tags=['tags'])


@tags_router.post(
    '/', response_model=list[TagPublic], status_code=HTTPStatus.CREATED
)
async def create_tag(
    tags: TagsSchema,
    user: T_User,
    session: T_Session,
    tags_srv: T_TagService,
    mapper: T_Mapper,
):
    tags_db = await tags_srv.get_or_create_tags(user, tags.names)

    await session.commit()

    for tag in tags_db:
        await session.refresh(tag)

    return [mapper.map_tag_public(tag_db) for tag_db in tags_db]


@tags_router.get(
    '/', response_model=list[TagPublic], status_code=HTTPStatus.OK
)
async def list_tags(user: T_User, tags_srv: T_TagService, mapper: T_Mapper):
    tags_db = await tags_srv.collect_tags(user)

    return [mapper.map_tag_public(tag) for tag in tags_db]


@tags_router.patch(
    '/{id}', response_model=TagPublic, status_code=HTTPStatus.OK
)
async def update_tag(  # noqa: PLR0913, PLR0917
    id: int,
    data: TagUpdate,
    user: T_User,
    session: T_Session,
    tags_srv: T_TagService,
    mapper: T_Mapper,
):
    await tags_srv.check_tag_name_exists(user, data.name, id)

    tag_db = await tags_srv.collect_tag_by_id(user, id)

    tag_db.name = data.name

    session.add(tag_db)

    await session.commit()
    await session.refresh(tag_db)

    return mapper.map_tag_public(tag_db)


@tags_router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_tag(
    id: int,
    user: T_User,
    tags_srv: T_TagService,
    session: T_Session,
):
    tag_db = await tags_srv.collect_tag_by_id(user, id)

    await session.delete(tag_db)
    await session.commit()
