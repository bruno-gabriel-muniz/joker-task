import re
from http import HTTPStatus
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Tag, Task, User
from joker_task.interfaces.interfaces import TagServiceInterface
from joker_task.schemas import TagSchema

T_Session = Annotated[AsyncSession, Depends(get_session)]


class TagService(TagServiceInterface):
    def __init__(self, session: T_Session):
        self.session = session

    async def get_or_create_tags(
        self, user: User, tags: Sequence[TagSchema] | None
    ) -> list[Tag]:
        logger.info('getting or creating tags')

        if not tags:
            return []

        if len(tags) != len({tag.name for tag in tags}):
            raise HTTPException(
                HTTPStatus.BAD_REQUEST, 'duplicate tag names in request'
            )

        result = [await self._get_or_create_tag(user, tag) for tag in tags]

        logger.info(f'got or created {len(result)} tags')
        return result

    async def collect_tag_by_id(self, user: User, id: int) -> Tag:
        logger.info(f'collecting tag with id = {id}')
        tag = await self.session.scalar(
            select(Tag).where(
                Tag.user_email == user.email,
                Tag.id_tag == id,
            )
        )

        if not tag:
            raise HTTPException(HTTPStatus.NOT_FOUND)

        return tag

    async def collect_tags(self, user: User) -> Sequence[Tag]:
        logger.info('collecting tags')
        tags = (
            await self.session.scalars(
                select(Tag).where(Tag.user_email == user.email)
            )
        ).all()

        return tags

    async def check_tag_name_exists(
        self, user: User, name: str, id: int
    ) -> None:
        logger.info(f'checking tag name conflict for id = {id}')
        have_conflict = await self.session.scalar(
            select(Tag).where(
                Tag.id_tag != id,
                Tag.user_email == user.email,
                Tag.name == name,
            )
        )

        if have_conflict:
            raise HTTPException(HTTPStatus.CONFLICT, 'name already in use')

    async def update_tags_of_task(
        self,
        user: User,
        task: Task,
        tags_add: Sequence[TagSchema] | None,
        tags_remove: Sequence[TagSchema] | None,
    ) -> None:
        logger.info(f'updating tags for task {task.id_task}')
        current_tags = {tag.name: tag.color_hex for tag in task.tags}

        if tags_add:
            current_tags.update({tag.name: tag.color_hex for tag in tags_add})

        if tags_remove:
            for tag in tags_remove:
                current_tags.pop(tag.name, None)

        tags = [
            TagSchema(name=name, color_hex=color)
            for name, color in current_tags.items()
        ]

        task.tags = await self.get_or_create_tags(user, tags)

    async def _get_or_create_tag(self, user: User, tag: TagSchema) -> Tag:
        tag_db = await self.session.scalar(
            select(Tag).where(
                Tag.user_email == user.email, Tag.name == tag.name
            )
        )

        if not tag_db:
            if tag.color_hex and not re.match(
                r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', tag.color_hex
            ):
                raise HTTPException(
                    HTTPStatus.BAD_REQUEST, 'invalid color_hex format'
                )

            tag_db = Tag(tag.name, tag.color_hex, user.email, user)
            logger.debug('creating new tag')
            self.session.add(tag_db)
        else:
            logger.debug('tag already exists')

        return tag_db
