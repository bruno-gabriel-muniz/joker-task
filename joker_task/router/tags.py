from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Tag, User
from joker_task.interfaces.interfaces import (
    MapperInterface,
    TagControlerInterface,
)
from joker_task.schemas import (
    TagPublic,
    TagsSchema,
)
from joker_task.service.mapper import Mapper
from joker_task.service.security import get_user
from joker_task.service.tags_controler import TagControler

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_User = Annotated[User, Depends(get_user)]
T_TagControler = Annotated[TagControlerInterface, Depends(TagControler)]
T_Mapper = Annotated[MapperInterface, Depends(Mapper)]


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

    return [mapper.map_tag_public(tag_db) for tag_db in tags_db]


@tags_router.get(
    '/', response_model=list[TagPublic], status_code=HTTPStatus.OK
)
async def list_tags(user: T_User, session: T_Session, mapper: T_Mapper):
    tags_db = (
        await session.scalars(select(Tag).where(Tag.user_email == user.email))
    ).all()

    return [mapper.map_tag_public(tag) for tag in tags_db]
