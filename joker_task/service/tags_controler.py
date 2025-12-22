from typing import Annotated, Sequence

from fastapi import Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Tag, Task, User
from joker_task.interfaces.interfaces import TagControlerInterface

T_Session = Annotated[AsyncSession, Depends(get_session)]


class TagControler(TagControlerInterface):
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
