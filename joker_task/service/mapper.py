from loguru import logger

from joker_task.db.models import Tag, Task, User, Workbench
from joker_task.interfaces.interfaces import MapperInterface
from joker_task.schemas import (
    TagPublic,
    TaskPublic,
    UserPublic,
    WorkbenchPublic,
)


class Mapper(MapperInterface):
    def __init__(self):
        return

    @staticmethod
    def map_user_public(user_db: User) -> UserPublic:
        logger.info(f'Mapping user {user_db.email} to UserPublic schema')

        user_rsp = UserPublic(
            email=user_db.email,
            username=user_db.username,
        )

        return user_rsp

    @staticmethod
    def map_task_public(task_db: Task) -> TaskPublic:
        logger.info(f'Mapping task {task_db.id_task} to TaskPublic schema')

        task_rsp = TaskPublic(
            title=task_db.title,
            description=task_db.description,
            done=task_db.done,
            tags=[Mapper.map_tag_str(tag) for tag in task_db.tags],
            reminder=task_db.reminder,
            repetition=task_db.repetition,
            state=task_db.state,
            priority=task_db.priority,
            id_task=task_db.id_task,
            user_email=task_db.user_email,
            created_at=task_db.created_at,
            updated_at=task_db.updated_at,
        )

        return task_rsp

    @staticmethod
    def map_tag_str(tag_db: Tag) -> str:
        return tag_db.name

    @staticmethod
    def map_tag_public(tag_db: Tag) -> TagPublic:
        tag_rsp = TagPublic(
            name=tag_db.name,
            id_tag=tag_db.id_tag,
            user_email=tag_db.user_email,
            created_at=tag_db.created_at,
            updated_at=tag_db.updated_at,
        )

        return tag_rsp

    @staticmethod
    def map_workbench_public(workbench_db: Workbench) -> WorkbenchPublic:
        return WorkbenchPublic(
            name=workbench_db.name,
            columns=workbench_db.columns,
            id_workbench=workbench_db.id_workbench,
            user_email=workbench_db.user_email,
            created_at=workbench_db.created_at,
            updated_at=workbench_db.updated_at,
        )
