from datetime import datetime
from typing import Sequence

from loguru import logger

from joker_task.db.models import (
    Filter,
    Tag,
    Task,
    TaskOccurrence,
    User,
    View,
    Workbench,
)
from joker_task.interfaces.interfaces import MapperInterface
from joker_task.schemas import (
    FilterPublic,
    TagPublic,
    TaskPublic,
    UserPublic,
    ViewPublic,
    ViewResult,
    ViewSoft,
    WorkbenchPublic,
)


class Mapper(MapperInterface):
    def __init__(self):
        return

    @staticmethod
    def map_user_public(user_db: User) -> UserPublic:
        logger.debug('mapping user to UserPublic')

        return UserPublic(
            email=user_db.email,
            username=user_db.username,
        )

    @staticmethod
    def map_task_public(
        task_db: Task, occurrences: Sequence[TaskOccurrence] | None = None
    ) -> TaskPublic:
        logger.debug(f'mapping task {task_db.id_task} to TaskPublic')
        if occurrences is None:
            occurrences = []

        return TaskPublic(
            title=task_db.title,
            description=task_db.description,
            done=task_db.done,
            tags=[Mapper.map_tag_public(tag) for tag in task_db.tags],
            workbenches=[
                workbench.id_workbench for workbench in task_db.workbenches
            ],
            reminder=task_db.reminder,
            repetition=task_db.repetition,
            occurrences={
                occurrence.occurrence_date: occurrence.done
                for occurrence in occurrences
            },
            state=task_db.state,
            priority=task_db.priority,
            id_task=task_db.id_task,
            user_email=task_db.user_email,
            created_at=task_db.created_at,
            updated_at=task_db.updated_at,
        )

    @staticmethod
    def map_tag_public(tag_db: Tag) -> TagPublic:
        logger.debug(f'mapping tag {tag_db.id_tag} to TagPublic')

        return TagPublic(
            name=tag_db.name,
            color_hex=tag_db.color_hex,
            id_tag=tag_db.id_tag,
            user_email=tag_db.user_email,
            created_at=tag_db.created_at,
            updated_at=tag_db.updated_at,
        )

    @staticmethod
    def map_workbench_public(workbench_db: Workbench) -> WorkbenchPublic:
        logger.debug(
            f'mapping workbench {workbench_db.id_workbench} to WorkbenchPublic'
        )
        return WorkbenchPublic(
            name=workbench_db.name,
            columns=workbench_db.columns,
            id_workbench=workbench_db.id_workbench,
            user_email=workbench_db.user_email,
            created_at=workbench_db.created_at,
            updated_at=workbench_db.updated_at,
        )

    @staticmethod
    def map_view_public(view_db: View) -> ViewPublic:
        logger.debug(f'mapping view {view_db.id_view} to ViewPublic')
        return ViewPublic(
            name=view_db.name,
            filters=[
                Mapper.map_filter_public(filter_db)
                for filter_db in view_db.filters
            ],
            id_view=view_db.id_view,
            user_email=view_db.user_email,
            created_at=view_db.created_at,
            updated_at=view_db.updated_at,
        )

    @staticmethod
    def map_view_soft(view_db: View) -> ViewSoft:
        logger.debug(f'mapping view {view_db.id_view} to ViewSoft')
        return ViewSoft(
            name=view_db.name,
            id_view=view_db.id_view,
            user_email=view_db.user_email,
            created_at=view_db.created_at,
            updated_at=view_db.updated_at,
        )

    @staticmethod
    def map_view_result(result: dict[int, list[Task]]) -> ViewResult:
        logger.debug(f'mapping results for {len(result)} view filters')
        result_mapped = {
            id: [
                Mapper.map_task_public(task, task.occurrences)
                for task in tasks
            ]
            for id, tasks in result.items()
        }

        return ViewResult(result=result_mapped)

    @staticmethod
    def map_filter_public(filter_db: Filter) -> FilterPublic:
        logger.debug(f'mapping filter {filter_db.id_filter} to FilterPublic')
        return FilterPublic(
            id_filter=filter_db.id_filter,
            created_at=filter_db.created_at,
            updated_at=filter_db.updated_at,
            offset=filter_db.offset,
            limit=filter_db.limit,
            title=filter_db.title,
            description=filter_db.description,
            done=filter_db.done,
            tags=filter_db.tags,
            reminder=Mapper._deserialize_reminder(filter_db.reminder),
            repetition=filter_db.repetition,
            state=filter_db.state,
            priority=filter_db.priority,
        )

    @staticmethod
    def _deserialize_reminder(
        reminder: tuple[str | None, str | None] | Sequence[str | None] | None,
    ) -> tuple[datetime | None, datetime | None] | None:
        if reminder is None:
            return None

        start_raw, end_raw = reminder

        return (
            datetime.fromisoformat(start_raw) if start_raw else None,
            datetime.fromisoformat(end_raw) if end_raw else None,
        )
