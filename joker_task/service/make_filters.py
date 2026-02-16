from typing import Any

from loguru import logger
from sqlalchemy import Select, func

from joker_task.db.models import Tag, Task, task_tag
from joker_task.interfaces.interfaces import StrategyMakeFilterInterface
from joker_task.schemas import (
    LOGIC_EXACT,
    LOGIC_IN_LIST,
    LOGIC_LIKE,
    LOGIC_RANGE,
    LOGIC_WITH_TAGS,
)


def factory_make_filter(type: Any) -> StrategyMakeFilterInterface:
    dict_type_strategy = {
        LOGIC_EXACT: FilterLogicExact,
        LOGIC_IN_LIST: FilterLogicInList,
        LOGIC_LIKE: FilterLogicLike,
        LOGIC_RANGE: FilterLogicRange,
        LOGIC_WITH_TAGS: FilterWithTags,
    }

    if not isinstance(type, str):
        logger.warning(f"type isn't str: {type}")
        raise TypeError('the arg type has be a str')

    if type not in dict_type_strategy:
        logger.warning(f'type unknown: {type}')
        raise ValueError('value not found in dict_type_strategy')

    logger.debug(f'factory_make_filter type: {type}')
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


class FilterWithTags(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(cur_filter: Select, values: list[Any], campo: str = '') -> Select:
        return (
            cur_filter.join(task_tag, task_tag.c.id_task == Task.id_task)
            .join(Tag, Tag.id_tag == task_tag.c.id_tag)
            .where(Tag.name.in_(values))
            .group_by(Task.id_task)
            .having(func.count(func.distinct(Tag.name)) == len(values))
        )


class FilterLogicRange(StrategyMakeFilterInterface):
    def __init__(self):
        pass

    @staticmethod
    def make(
        cur_filter: Select, values: tuple[Any, Any], campo: str
    ) -> Select:
        if start := values[0]:
            cur_filter = cur_filter.where(getattr(Task, campo) >= start)
        if end := values[1]:
            cur_filter = cur_filter.where(getattr(Task, campo) <= end)
        return cur_filter
