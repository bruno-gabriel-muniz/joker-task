from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import Select

from joker_task.db.models import Task, User
from joker_task.schemas import Filter


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
