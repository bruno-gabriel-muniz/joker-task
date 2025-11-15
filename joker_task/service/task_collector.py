from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Task, User
from joker_task.interfaces.interfaces import TaskCollectorInterface
from joker_task.schemas import Filter
from joker_task.service.make_filters import factory_make_filter


class TaskCollector(TaskCollectorInterface):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def collect_task_by_id(self, user: User, id_task: int) -> Task:
        task = await self.session.scalar(
            select(Task).where(
                Task.user_email == user.email, Task.id_task == id_task
            )
        )
        if not task:
            raise HTTPException(HTTPStatus.NOT_FOUND, 'task not found')
        return task

    async def collect_task_by_filter(
        self, user: User, filter: Filter
    ) -> list[Task]:
        filter_sql = select(Task).where(Task.user_email == user.email)

        for campo in filter.model_fields:
            filter_sql = self._make_filter(campo, filter, filter_sql)

        result: list[Task] = list(
            (await self.session.scalars(filter_sql)).all()
        )

        return result

    @staticmethod
    def _make_filter(campo: str, filter: Filter, filter_sql: Select) -> Select:
        field_info = filter.__class__.model_fields.get(campo)

        if not getattr(filter, campo) or not (
            field_info and field_info.json_schema_extra
        ):
            return filter_sql

        make_filter = factory_make_filter(
            field_info.json_schema_extra.get('search_logic')
        )

        return make_filter.make(filter_sql, getattr(filter, campo), campo)
