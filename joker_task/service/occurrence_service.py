from datetime import date
from http import HTTPStatus
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Task, TaskOccurrence
from joker_task.interfaces.interfaces import OccurrenceServiceInterface

T_Session = Annotated[AsyncSession, Depends(get_session)]


class OccurrenceService(OccurrenceServiceInterface):
    def __init__(self, session: T_Session):
        self.session = session

    async def validate_occurrence_changes(
        self,
        task: Task,
        occurrences_add: dict[date, bool],
        occurrences_update: dict[date, bool],
        occurrences_remove: Sequence[date],
    ) -> None:
        logger.debug(f'validating occurrence changes for task {task.id_task}')
        add_dates = set(occurrences_add)
        update_dates = set(occurrences_update)
        remove_dates = set(occurrences_remove)

        if (
            add_dates & update_dates
            or add_dates & remove_dates
            or update_dates & remove_dates
            or len(occurrences_remove) != len(remove_dates)
        ):
            logger.warning(
                f'occurrence date conflict in request for task {task.id_task}'
            )
            raise HTTPException(
                HTTPStatus.CONFLICT,
                'occurrence dates conflict in request',
            )

        if add_dates:
            existing_date = await self.session.scalar(
                select(TaskOccurrence.occurrence_date).where(
                    TaskOccurrence.id_task == task.id_task,
                    TaskOccurrence.occurrence_date.in_(add_dates),
                )
            )
            if existing_date is not None:
                logger.warning(
                    f'occurrence date already exists for task {task.id_task}'
                )
                raise HTTPException(
                    HTTPStatus.CONFLICT,
                    'occurrence date already exists',
                )

    @staticmethod
    async def create_occurrences_of_task(
        task: Task,
        occurrences: dict[date, bool],
    ) -> Sequence[TaskOccurrence]:
        logger.debug(
            f'creating {len(occurrences)} occurrences for task {task.id_task}'
        )
        return [
            TaskOccurrence(
                task=task,
                id_task=task.id_task,
                occurrence_date=occurrence_date,
                done=done,
            )
            for occurrence_date, done in occurrences.items()
        ]

    async def get_occurrences_of_task(
        self, task: Task
    ) -> Sequence[TaskOccurrence]:
        logger.debug(f'collecting occurrences for task {task.id_task}')
        occurrences = await self.session.scalars(
            select(TaskOccurrence).where(
                TaskOccurrence.id_task == task.id_task
            )
        )
        return occurrences.all()

    async def update_occurrences_of_task(
        self,
        task: Task,
        occurrences: dict[date, bool],
    ) -> None:
        logger.info(
            f'updating {len(occurrences)} occurrences for task {task.id_task}'
        )
        occurrences_db = await self._get_occurrence_of_task_by_date(
            task, list(occurrences.keys())
        )

        for occurrence_db in occurrences_db:
            occurrence_db.done = occurrences[occurrence_db.occurrence_date]
            self.session.add(occurrence_db)

    async def remove_occurrences_of_task(
        self,
        task: Task,
        occurrences: Sequence[date],
    ) -> None:
        logger.info(
            f'removing {len(occurrences)} occurrences for task {task.id_task}'
        )
        occurrences_db = await self._get_occurrence_of_task_by_date(
            task, occurrences
        )

        for occurrence_db in occurrences_db:
            await self.session.delete(occurrence_db)

    async def _get_occurrence_of_task_by_date(
        self, task: Task, occurrences_date: Sequence[date]
    ) -> Sequence[TaskOccurrence]:
        logger.debug(
            f'looking up {len(occurrences_date)} occurrence dates '
            + f'for task {task.id_task}'
        )
        return (
            await self.session.scalars(
                select(TaskOccurrence).where(
                    TaskOccurrence.id_task == task.id_task,
                    TaskOccurrence.occurrence_date.in_(occurrences_date),
                )
            )
        ).all()
