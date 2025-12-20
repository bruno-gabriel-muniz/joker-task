from loguru import logger

from joker_task.db.models import Tag, Task, User
from joker_task.interfaces.interfaces import MapperInterface
from joker_task.schemas import TaskPublic, UserPublic


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
        logger.info(f'Mapping tag {tag_db.name} to string')

        return tag_db.name
