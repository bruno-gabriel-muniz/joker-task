from loguru import logger

from joker_task.db.models import Task
from joker_task.interfaces.interfaces import TaskServiceInterface


class TaskService(TaskServiceInterface):
    def __init__(self):
        return

    @staticmethod
    async def create_task(user, task, tags_db, workbenches_db) -> Task:
        logger.info('creating task')
        logger.debug(
            f'task includes {len(tags_db)} tags and '
            + f'{len(workbenches_db)} workbenches'
        )
        task_db = Task(
            user_email=user.email,
            user=user,
            title=task.title,
            description=task.description,
            done=task.done or False,
            tags=list(tags_db),
            workbenches=list(workbenches_db),
            reminder=task.reminder,
            repetition=task.repetition,
            state=task.state,
            priority=task.priority,
        )

        logger.debug('created task entity')
        return task_db

    @staticmethod
    async def update_task(task, task_update) -> None:
        task_fields = {
            'title',
            'description',
            'done',
            'reminder',
            'repetition',
            'state',
            'priority',
        }
        changes = task_update.model_dump(
            include=task_fields,
            exclude_unset=True,
            exclude_none=True,
        )
        logger.info(f'updating task {task.id_task}')

        logger.debug(f'updating task {task.id_task} fields: {list(changes)}')
        for key, value in changes.items():
            setattr(task, key, value)
