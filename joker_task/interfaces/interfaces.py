from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy import Select

from joker_task.db.models import Tag, Task, User
from joker_task.schemas import Filter, TaskPublic, UserPublic


class TaskCollectorInterface(ABC):
    @abstractmethod
    async def collect_task_by_id(self, user: User, id_task: int) -> Task:
        pass  # pragma: no cover

    @abstractmethod
    async def collect_task_by_filter(
        self, user: User, filter: Filter
    ) -> list[Task]:
        pass  # pragma: no cover


class StrategyMakeFilterInterface(ABC):
    @abstractmethod
    def make(self, cur_filter: Select, values: Any, campo: str) -> Select:
        pass  # pragma: no cover


class TagControlerInterface(ABC):
    @abstractmethod
    async def get_or_create_tags(
        self, user: User, tag_names: Sequence[str | Tag] | None
    ) -> list[Tag]:
        pass  # pragma: no cover

    @abstractmethod
    async def update_tags_of_task(
        self,
        user: User,
        task: Task,
        tags_add: Sequence[str] | None,
        tags_remove: Sequence[str] | None,
    ) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def _get_or_create_tag(self, user: User, tag_name: str | Tag) -> Tag:
        pass  # pragma: no cover


class MapperInterface(ABC):
    @staticmethod
    @abstractmethod
    def map_user_public(user_db: User) -> UserPublic:
        pass  # pragma: no cover

    @staticmethod
    @abstractmethod
    def map_task_public(task_db: Task) -> TaskPublic:
        pass  # pragma: no cover

    @staticmethod
    @abstractmethod
    def map_tag_str(tag_db: Tag) -> str:
        pass  # pragma: no cover
