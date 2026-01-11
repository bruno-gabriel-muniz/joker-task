from http import HTTPStatus
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from joker_task.db.database import get_session
from joker_task.db.models import Task, User, Workbench
from joker_task.interfaces.interfaces import WorkbenchControllerInterface

T_Session = Annotated[AsyncSession, Depends(get_session)]


class WorkbenchController(WorkbenchControllerInterface):
    def __init__(self, session: T_Session):
        self.session = session

    async def collect_workbench_by_id(
        self, user: User, id_workbench: int
    ) -> Workbench:
        logger.info(f'collecting workbenches with id: {id_workbench}')
        workbench_db = await self.session.scalar(
            select(Workbench).where(
                Workbench.user_email == user.email,
                Workbench.id_workbench == id_workbench,
            )
        )

        if not workbench_db:
            raise HTTPException(HTTPStatus.NOT_FOUND, 'workbench not found')

        return workbench_db

    async def collect_workbenches_by_id(
        self, user: User, id_workbenches: Sequence[int]
    ) -> Sequence[Workbench]:
        logger.info(f'collecting workbenches by id: {id_workbenches}')

        result = await self.session.execute(
            select(Workbench).where(
                Workbench.user_email == user.email,
                Workbench.id_workbench.in_(id_workbenches),
            )
        )

        workbenches_db = result.scalars().all()

        if len(workbenches_db) != len(id_workbenches):
            id_workbenches_db = {
                workbench.id_workbench for workbench in workbenches_db
            }
            for id_workbench in id_workbenches:
                if id_workbench not in id_workbenches_db:
                    raise HTTPException(
                        HTTPStatus.NOT_FOUND,
                        f'workbench with id: {id_workbench}, not found',
                    )
            logger.error(
                'workbenches count mismatch after query'
            )  # pragma: no cover

            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                'internal error collecting workbenches',
            )  # pragma: no cover

        return workbenches_db

    async def collect_workbenches(self, user: User) -> Sequence[Workbench]:
        logger.info(f'collecting workbenches of user: {user.email}')

        result = await self.session.execute(
            select(Workbench).where(
                Workbench.user_email == user.email,
            )
        )

        return result.scalars().all()

    async def check_workbench_name_exists(self, user: User, name: str) -> None:
        logger.info(f'checking workbench name conflict: {name}')
        have_conflict = await self.session.scalar(
            select(Workbench).where(
                Workbench.name == name,
                Workbench.user_email == user.email,
            )
        )
        if have_conflict:
            raise HTTPException(
                HTTPStatus.CONFLICT, detail='workbench name already in use'
            )

    async def update_workbenches_of_task(
        self,
        user: User,
        task: Task,
        workbenches_add: Sequence[int] | None,
        workbenches_remove: Sequence[int] | None,
    ) -> None:
        logger.info(f'updating workbenches of task id: {task.id_task}')
        current_workbenches = {
            workbench.id_workbench for workbench in task.workbenches
        }

        if workbenches_add:
            current_workbenches.update(workbenches_add)
        if workbenches_remove:
            current_workbenches.difference_update(workbenches_remove)

        task.workbenches = list(
            await self.collect_workbenches_by_id(
                user, list(current_workbenches)
            )
        )
