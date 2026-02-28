from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from joker_task.db.database import get_session
from joker_task.db.models import Filter, Task, User, View
from joker_task.interfaces.interfaces import (
    MapperInterface,
    TaskCollectorInterface,
    ViewServiceInterface,
)
from joker_task.schemas import FilterSchema, ViewSchema, ViewUpdate
from joker_task.service.mapper import Mapper
from joker_task.service.task_collector import TaskCollector

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CollectorTask = Annotated[TaskCollectorInterface, Depends(TaskCollector)]
T_Mapper = Annotated[MapperInterface, Depends(Mapper)]


class ViewService(ViewServiceInterface):
    def __init__(
        self, session: T_Session, collector: T_CollectorTask, mapper: T_Mapper
    ):
        self.session = session
        self.collector = collector
        self.mapper = mapper

    async def create_view(self, user: User, view: ViewSchema) -> View:
        logger.debug(
            f'Creating view for user {user.email} with name {view.name}'
        )
        await self._find_conflicting(user, view.name)
        view_db = View(
            user_email=user.email,
            user=user,
            name=view.name,
        )
        self.session.add(view_db)

        filters_db = [
            self._make_filter_db(view_db, filter) for filter in view.filters
        ]

        for filter_db in filters_db:
            self.session.add(filter_db)

        return view_db

    async def list_views(self, user: User) -> Sequence[View]:
        logger.debug(f'Listing views for user {user.email}')

        result = await self.session.scalars(
            select(View)
            .where(View.user_email == user.email)
            .order_by(View.id_view)
        )

        return result.all()

    async def get_view_by_id(self, user: User, id_view: int) -> View:
        logger.debug(f'Getting view {id_view} for user {user.email}')

        view_db = await self.session.scalar(
            select(View)
            .where(View.id_view == id_view, View.user_email == user.email)
            .options(selectinload(View.filters))
        )

        if not view_db:
            raise HTTPException(HTTPStatus.NOT_FOUND, 'view not found')

        return view_db

    async def apply_view(
        self,
        user: User,
        id_view: int,
    ) -> dict[int, list[Task]]:
        logger.debug(f'Applying view {id_view} for user {user.email}')

        view = await self.get_view_by_id(user, id_view)

        result: dict[int, list[Task]] = {}

        for filter in view.filters:
            result[
                filter.id_filter
            ] = await self.collector.collect_task_by_filter(
                user, self.mapper.map_filter_public(filter)
            )

        return result

    async def update_view(
        self, user: User, id_view: int, view: ViewUpdate
    ) -> View:
        logger.debug(f'Updating view {id_view} for user {user.email}')

        view_db = await self.get_view_by_id(user, id_view)

        if not view.name:  # empty name is not allowed
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='name cannot be empty',
            )
        elif view_db.name != view.name:
            await self._find_conflicting(user, view.name)

        view_db.name = view.name
        self.session.add(view_db)

        return view_db

    async def create_view_filter(
        self, user: User, id_view: int, filter_schema: FilterSchema
    ) -> Filter:
        logger.debug(
            f'Creating filter for view {id_view} for user {user.email}'
        )

        view_db = await self.get_view_by_id(user, id_view)

        filter_db = self._make_filter_db(view_db, filter_schema)
        self.session.add(filter_db)

        return filter_db

    async def update_view_filter(
        self,
        user: User,
        id_view: int,
        id_filter: int,
        filter_schema: FilterSchema,
    ) -> Filter:
        logger.debug(
            f'Updating filter {id_filter} '
            + f'for view {id_view} for user {user.email}'
        )

        view_db = await self.get_view_by_id(user, id_view)

        filter_db = next(
            (
                filter
                for filter in view_db.filters
                if filter.id_filter == id_filter
            ),
            None,
        )

        if not filter_db:
            raise HTTPException(HTTPStatus.NOT_FOUND, 'filter not found')

        filter_db.title = filter_schema.title
        filter_db.description = filter_schema.description
        filter_db.done = filter_schema.done
        filter_db.tags = filter_schema.tags or None
        filter_db.reminder = self._serialize_reminder(filter_schema.reminder)
        filter_db.repetition = filter_schema.repetition
        filter_db.state = filter_schema.state or []
        filter_db.priority = filter_schema.priority or (None, None)
        filter_db.limit = filter_schema.limit
        filter_db.offset = filter_schema.offset
        self.session.add(filter_db)

        return filter_db

    async def delete_view_filter(
        self, user: User, id_view: int, id_filter: int
    ) -> None:
        logger.debug(
            f'Deleting filter {id_filter} '
            + f'for view {id_view} for user {user.email}'
        )

        view_db = await self.get_view_by_id(user, id_view)

        filter_db = next(
            (
                filter
                for filter in view_db.filters
                if filter.id_filter == id_filter
            ),
            None,
        )

        if not filter_db:
            raise HTTPException(HTTPStatus.NOT_FOUND, 'filter not found')

        await self.session.delete(filter_db)

    @staticmethod
    def _make_filter_db(view_db: View, filter_schema: FilterSchema) -> Filter:
        return Filter(
            id_view=view_db.id_view,
            view=view_db,
            title=filter_schema.title,
            description=filter_schema.description,
            done=filter_schema.done,
            tags=filter_schema.tags or [],
            reminder=ViewService._serialize_reminder(filter_schema.reminder),
            repetition=filter_schema.repetition,
            state=filter_schema.state or [],
            priority=filter_schema.priority or (None, None),
            limit=filter_schema.limit,
            offset=filter_schema.offset,
        )

    @staticmethod
    def _serialize_reminder(
        reminder: tuple[datetime | None, datetime | None] | None,
    ) -> tuple[str | None, str | None] | None:
        if reminder is None:
            return None

        start, end = reminder
        return (
            start.isoformat() if start else None,
            end.isoformat() if end else None,
        )

    async def _find_conflicting(self, user: User, name: str) -> None:
        have_conflict = await self.session.scalar(
            select(View).where(
                View.user_email == user.email, View.name == name
            )
        )

        if have_conflict is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='view with this name already exists',
            )
