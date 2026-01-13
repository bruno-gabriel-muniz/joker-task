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
        logger.debug(f'mapping user {user_db.email} to UserPublic')

        return UserPublic(
            email=user_db.email,
            username=user_db.username,
        )

    @staticmethod
    def map_task_public(task_db: Task) -> TaskPublic:
        logger.debug(f'mapping task {task_db.id_task} to TaskPublic')

        return TaskPublic(
            title=task_db.title,
            description=task_db.description,
            done=task_db.done,
            tags=[Mapper.map_tag_str(tag) for tag in task_db.tags],
            workbenches=[
                workbench.id_workbench for workbench in task_db.workbenches
            ],
            reminder=task_db.reminder,
            repetition=task_db.repetition,
            state=task_db.state,
            priority=task_db.priority,
            id_task=task_db.id_task,
            user_email=task_db.user_email,
            created_at=task_db.created_at,
            updated_at=task_db.updated_at,
        )

    @staticmethod
    def map_tag_str(tag_db: Tag) -> str:
        logger.debug(f'mapping tag {tag_db.id_tag} to str')
        return tag_db.name

    @staticmethod
    def map_tag_public(tag_db: Tag) -> TagPublic:
        logger.debug(f'mapping tag {tag_db.id_tag} to TagPublic')

        return TagPublic(
            name=tag_db.name,
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
