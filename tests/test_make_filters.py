import pytest

from joker_task.service.make_filters import factory_make_filter


def test_factory_make_filters_type_error():
    with pytest.raises(TypeError, match='the arg type has be a str'):
        factory_make_filter(123)


def test_factory_make_filters_value_error():
    with pytest.raises(
        ValueError, match='value not found in dict_type_strategy'
    ):
        factory_make_filter('unknown_type')
