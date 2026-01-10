from http import HTTPStatus
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Tag, Task, User
from joker_task.interfaces.interfaces import TagControllerInterface

T_Session = Annotated[AsyncSession, Depends(get_session)]


class TagController(TagControllerInterface):
    def __init__(self, session: T_Session):
        self.session = session

    async def get_or_create_tags(
        self, user: User, tag_names: Sequence[str | Tag] | None
    ) -> list[Tag]:
        logger.info('getting or creating tags')

        if not tag_names:
            return []

        tag_names = list(set(tag_names))

        result = [
            await self._get_or_create_tag(user, tag_name)
            for tag_name in tag_names
        ]

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
        logger.info(f'collecting tags for user {user.email}')
        tags = (
            await self.session.scalars(
                select(Tag).where(Tag.user_email == user.email)
            )
        ).all()

        return tags

    async def check_tag_name_exists(
        self, user: User, name: str, id: int
    ) -> None:
        logger.info(
            f'checking if tag name "{name}" exists for user {user.email}'
        )
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
        tags_add: Sequence[str] | None,
        tags_remove: Sequence[str] | None,
    ) -> None:
        logger.info('updating tags of task with id = {task.id_task}')
        current_tags = {tag.name for tag in task.tags}

        if tags_add:
            current_tags.update(tags_add)

        if tags_remove:
            current_tags.difference_update(tags_remove)

        task.tags = await self.get_or_create_tags(user, list(current_tags))

    async def _get_or_create_tag(self, user: User, tag_name: str | Tag) -> Tag:
        if isinstance(tag_name, Tag):
            return tag_name  # pragma: no cover

        tag = await self.session.scalar(
            select(Tag).where(
                Tag.user_email == user.email, Tag.name == tag_name
            )
        )

        if not tag:
            tag = Tag(tag_name, user.email, user)
            logger.info(f'creating new tag: {tag_name}')
            self.session.add(tag)
        else:
            logger.info(f'tag found: {tag_name}')

        return tag
