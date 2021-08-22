# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/20"
from __future__ import absolute_import

from collections import Iterable

from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.sql.operators import ColumnOperators

__all__ = [
    "make_filter", "AND_FILTER", "EQ_FILTER", "GE_FILTER", "GT_FILTER", "ILIKE_FILTER", "IN_FILTER", "LE_FILTER",
    "LIKE_FILTER", "LT_FILTER", "MATCH_FILTER", "NE_FILTER", "NOT_IN_FILTER", "OR_FILTER", "NOT_FILTER"
]


def make_equal_filter(model, field, value):
    return getattr(model, field) == value


def make_not_equal_filter(model, field, value):
    return getattr(model, field) != value


def make_greater_than_filter(model, field, value):
    return getattr(model, field) > value


def make_less_than_filter(model, field, value):
    return getattr(model, field) < value


def make_greater_than_or_equal_filter(model, field, value):
    return getattr(model, field) >= value


def make_less_than_or_equal_filter(model, field, value):
    return getattr(model, field) <= value


def make_like_filter(model, field, value):
    return getattr(model, field).like("%{}%".format(value))


def make_ilike_filter(model, field, value):
    return getattr(model, field).ilike("%{}%".format(value))


def make_match_filter(model, field, value):
    return getattr(model, field).match(value)


def make_in_filter(model, field, values):
    if isinstance(values, Iterable):
        values = list(values)
    else:
        values = [values]
    return getattr(model, field).in_(values)


def make_not_in_filter(model, field, values):
    if isinstance(values, Iterable):
        values = list(values)
    else:
        values = [values]
    return ~getattr(model, field).in_(values)


EQ_FILTER = "eq"
NE_FILTER = "ne"
GT_FILTER = "gt"
LT_FILTER = "lt"
GE_FILTER = "ge"
LE_FILTER = "le"
LIKE_FILTER = "like"
ILIKE_FILTER = "ilike"
MATCH_FILTER = "match"
IN_FILTER = "in"
NOT_IN_FILTER = "not_in"

AND_FILTER = "and"
OR_FILTER = "or"
NOT_FILTER = "not"


simple_filter_makers = {
    EQ_FILTER: make_equal_filter,
    NE_FILTER: make_not_equal_filter,
    GT_FILTER: make_greater_than_filter,
    LT_FILTER: make_less_than_filter,
    GE_FILTER: make_greater_than_or_equal_filter,
    LE_FILTER: make_less_than_or_equal_filter,
    LIKE_FILTER: make_like_filter,
    ILIKE_FILTER: make_ilike_filter,
    MATCH_FILTER: make_match_filter,
    IN_FILTER: make_in_filter,
    NOT_IN_FILTER: make_not_in_filter
}


def make_and_filter(filters):
    return and_(*tuple(filters)) if len(filters) > 1 else filters[0]


def make_or_filter(filters):
    return or_(*tuple(filters)) if len(filters) > 1 else filters[0]


def make_not_filter(filters):
    return ~make_and_filter(filters)


composite_filter_makers = {
    AND_FILTER: make_and_filter,
    OR_FILTER: make_or_filter,
    NOT_FILTER: make_not_filter
}


def _make_filter_from_expr(model, expr):
    if len(expr) != 2:
        raise ValueError(
            "`expr` can only contain two items: {}".format(str(expr))
        )
    if expr[0] in simple_filter_makers or expr[0] in composite_filter_makers:
        if not isinstance(expr[1], (tuple, list)):
            raise ValueError(
                "the second item of `expr` should be an object "
                "with type in [tuple, list]: {}".format(str(expr))
            )
        if expr[0] not in composite_filter_makers:
            if len(expr[1]) != 2:
                raise ValueError(
                    "the second item of `expr` can only contain "
                    "two items: {}".format(str(expr))
                )
            return simple_filter_makers[expr[0]](model, *tuple(expr[1]))
        else:
            if len(expr[1]) < 1:
                raise ValueError(
                    "the second item of `expr` should contain at least "
                    "one item: {}".format(str(expr))
                )
            filters = [make_filter(model, _repr) for _repr in expr[1]]
            return composite_filter_makers[expr[0]](filters)
    else:
        return make_equal_filter(model, expr[0], expr[1])


def make_filter(model, filter_repr):
    if isinstance(filter_repr, (tuple, list)):
        return _make_filter_from_expr(model, filter_repr)
    elif isinstance(filter_repr, ColumnOperators):
        return filter_repr
    raise TypeError(
        "`filter_repr` should be an object with type in "
        "[tuple, list, ColumnOperators]: {}".format(str(filter_repr))
    )
