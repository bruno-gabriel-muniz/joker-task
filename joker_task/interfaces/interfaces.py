from abc import ABC, abstractmethod
from typing import Any, Sequence

from sqlalchemy import Select

from joker_task.db.models import Tag, Task, User, View, Workbench
from joker_task.schemas import (
    FilterSchema,
    TagPublic,
    TaskPublic,
    UserPublic,
    ViewPublic,
    ViewSchema,
    WorkbenchPublic,
)


class TaskCollectorInterface(ABC):
    @abstractmethod
    async def collect_task_by_id(self, user: User, id_task: int) -> Task:
        pass  # pragma: no cover

    @abstractmethod
    async def collect_task_by_filter(
        self, user: User, filter: FilterSchema
    ) -> list[Task]:
        pass  # pragma: no cover


class StrategyMakeFilterInterface(ABC):
    @abstractmethod
    def make(self, cur_filter: Select, values: Any, campo: str) -> Select:
        pass  # pragma: no cover


class TagServiceInterface(ABC):
    @abstractmethod
    async def get_or_create_tags(
        self, user: User, tag_names: Sequence[str] | None
    ) -> list[Tag]:
        pass  # pragma: no cover

    @abstractmethod
    async def collect_tag_by_id(self, user: User, id: int) -> Tag:
        pass  # pragma: no cover

    @abstractmethod
    async def collect_tags(self, user: User) -> Sequence[Tag]:
        pass  # pragma: no cover

    @abstractmethod
    async def check_tag_name_exists(
        self, user: User, name: str, id: int
    ) -> None:
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


class WorkbenchServiceInterface(ABC):
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


class ViewServiceInterface(ABC):
    @abstractmethod
    async def create_view(self, user: User, view_schema: ViewSchema) -> View:
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

    @staticmethod
    @abstractmethod
    def map_view_public(view_db: View) -> ViewPublic:
        pass  # pragma: no cover
