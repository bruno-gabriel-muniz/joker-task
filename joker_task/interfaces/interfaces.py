from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy import Select

from joker_task.db.models import Tag, Task, User, Workbench
from joker_task.schemas import (
    Filter,
    TagPublic,
    TaskPublic,
    UserPublic,
    WorkbenchPublic,
)


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


class WorkbenchControlerInterface(ABC):
    @abstractmethod
    async def collect_workbench_by_id(
        self, user: User, id_workbench: int
    ) -> Workbench:
        pass  # pragma: no cover

    @abstractmethod
    async def collect_workbenches_by_id(
        self, user: User, id_workbenches: Sequence[int]
    ) -> Sequence[Workbench]:
        pass  # pragma: no cover

    @abstractmethod
    async def collect_workbenches(self, user: User) -> Sequence[Workbench]:
        pass  # pragma: no cover

    @abstractmethod
    async def check_workbench_name_exists(self, user: User, name: str) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def update_workbenches_of_task(
        self,
        user: User,
        task: Task,
        workbenches_add: Sequence[int] | None,
        workbenches_remove: Sequence[int] | None,
    ) -> None:
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

    @staticmethod
    @abstractmethod
    def map_tag_public(tag_db: Tag) -> TagPublic:
        pass  # pragma: no cover

    @staticmethod
    @abstractmethod
    def map_workbench_public(workbench_db: Workbench) -> WorkbenchPublic:
        pass  # pragma: no cover
