from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Tag, User
from joker_task.interfaces.interfaces import TagControlerInterface

T_Session = Annotated[AsyncSession, Depends(get_session)]


class TagControler(TagControlerInterface):
    def __init__(self, session: T_Session):
        self.session = session

    async def get_or_create_tags(
        self, user: User, tag_names: Sequence[str | Tag] | None
    ) -> list[Tag]:
        if not tag_names:
            return []

        tag_names = list(set(tag_names))

        result = [
            await self._get_or_create_tag(user, tag_name)
            for tag_name in tag_names
        ]

        return result

    async def _get_or_create_tag(self, user: User, tag_name: str | Tag) -> Tag:
        if isinstance(tag_name, Tag):
            return tag_name  # pragma: no cover

        tag = await self.session.scalar(
            select(Tag).where(
                Tag.user_email == user.email, Tag.name == tag_name
            )
        )

        if not tag:
            tag = Tag(name=tag_name, user_email=user.email, user=user)
            self.session.add(tag)

        return tag
