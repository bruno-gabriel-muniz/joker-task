from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from loguru import logger
from sqlalchemy import select

from joker_task.db.models import Tag
from joker_task.schemas import (
    TagPublic,
    TagsSchema,
    TagUpdate,
)
from joker_task.service.dependencies import (
    T_Mapper,
    T_Session,
    T_TagControler,
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
    tag_ctrl: T_TagControler,
    mapper: T_Mapper,
):
    logger.info(f'Creating tags for user {user.email}')
    tags_db = await tag_ctrl.get_or_create_tags(user, tags.names)

    await session.commit()

    for tag in tags_db:
        await session.refresh(tag)

    logger.info(f'Mapping response for {user.email}')
    return [mapper.map_tag_public(tag_db) for tag_db in tags_db]


@tags_router.get(
    '/', response_model=list[TagPublic], status_code=HTTPStatus.OK
)
async def list_tags(user: T_User, session: T_Session, mapper: T_Mapper):
    tags_db = (
        await session.scalars(select(Tag).where(Tag.user_email == user.email))
    ).all()

    logger.info(f'Listing tags for user {user.email}')
    return [mapper.map_tag_public(tag) for tag in tags_db]


@tags_router.patch(
    '/{id}', response_model=TagPublic, status_code=HTTPStatus.OK
)
async def update_tag(
    id: int,
    data: TagUpdate,
    user: T_User,
    session: T_Session,
    mapper: T_Mapper,
):
    logger.info(f'Updating tag {id} for user {user.email}')
    have_conflict = await session.scalar(
        select(Tag).where(
            Tag.id_tag != id,
            Tag.user_email == user.email,
            Tag.name == data.name,
        )
    )
    if have_conflict:
        logger.info(f'Conflict when updating tag {id} for user {user.email}')
        raise HTTPException(HTTPStatus.CONFLICT, 'name already in use')

    tag_db = await session.scalar(
        select(Tag).where(Tag.id_tag == id, Tag.user_email == user.email)
    )
    if not tag_db:
        logger.info(f'Tag {id} not found for user {user.email}')
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
        )

    tag_db.name = data.name

    session.add(tag_db)

    await session.commit()
    await session.refresh(tag_db)

    logger.info(f'Tag {id} updated for user {user.email}')
    return mapper.map_tag_public(tag_db)


@tags_router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_tag(
    id: int,
    user: T_User,
    session: T_Session,
):
    tag_db = await session.scalar(
        select(Tag).where(Tag.user_email == user.email, Tag.id_tag == id)
    )

    if not tag_db:
        raise HTTPException(HTTPStatus.NOT_FOUND)

    await session.delete(tag_db)
    await session.commit()
