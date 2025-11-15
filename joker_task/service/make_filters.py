from typing import Any

from sqlalchemy import Select

from joker_task.db.models import Task
from joker_task.interfaces.interfaces import StrategyMakeFilterInterface
from joker_task.schemas import (
    LOGIC_EXACT,
    LOGIC_IN_LIST,
    LOGIC_LIKE,
    LOGIC_LIST_IN_LIST,
    LOGIC_RANGE,
)


def factory_make_filter(type: Any) -> StrategyMakeFilterInterface:
    dict_type_strategy = {
        LOGIC_EXACT: FilterLogicExact,
        LOGIC_IN_LIST: FilterLogicInList,
        LOGIC_LIKE: FilterLogicLike,
        LOGIC_LIST_IN_LIST: FilterLogicListInList,
        LOGIC_RANGE: FilterLogicRange,
    }

    if not isinstance(type, str):
        raise TypeError('the arg type has be a str')

    if type not in dict_type_strategy:
        raise ValueError('value not found in dict_type_strategy')

    return dict_type_strategy[type]()


class FilterLogicExact(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(cur_filter: Select, value: Any, campo: str) -> Select:
        return cur_filter.where(getattr(Task, campo) == value)


class FilterLogicInList(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(cur_filter: Select, values: list[Any], campo: str) -> Select:
        return cur_filter.where(getattr(Task, campo).in_(values))


class FilterLogicLike(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(cur_filter: Select, values: Any, campo: str) -> Select:
        return cur_filter.where(getattr(Task, campo).like(values))


class FilterLogicListInList(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(cur_filter: Select, values: list[Any], campo: str) -> Select:
        for value in values:
            cur_filter = cur_filter.where(
                getattr(Task, campo).contains(value)
            )
        return cur_filter


class FilterLogicRange(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(
        cur_filter: Select, values: tuple[Any, Any, Any], campo: str
    ) -> Select:
        if start := values[0]:
            cur_filter = cur_filter.where(getattr(Task, campo) >= start)
        if end := values[1]:
            cur_filter = cur_filter.where(getattr(Task, campo) <= end)
        return cur_filter
