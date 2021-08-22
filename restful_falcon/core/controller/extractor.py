# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/25"
from __future__ import absolute_import

import sys

from functools import partial

from restful_falcon.core.db.filter import AND_FILTER
from restful_falcon.core.db.filter import EQ_FILTER
from restful_falcon.core.db.filter import GE_FILTER
from restful_falcon.core.db.filter import GT_FILTER
from restful_falcon.core.db.filter import ILIKE_FILTER
from restful_falcon.core.db.filter import IN_FILTER
from restful_falcon.core.db.filter import LE_FILTER
from restful_falcon.core.db.filter import LIKE_FILTER
from restful_falcon.core.db.filter import LT_FILTER
from restful_falcon.core.db.filter import MATCH_FILTER
from restful_falcon.core.db.filter import NE_FILTER
from restful_falcon.core.db.filter import NOT_IN_FILTER
from restful_falcon.core.db.filter import OR_FILTER
from restful_falcon.core.exception import HTTPInvalidParam

"""
Pagination:
__limit=10
__offset=0

Filter:
key=value
__and=key,value,[equal|not_equal|like|ilike]
__or=key,value,[equal|not_equal|like|ilike]
__in=key,value1,value2,...
__not_in=key,value1,value2,...
__eq=key,value
__ne=key,value
__gt=key,value
__lt=key,value
__ge=key,value
__le=key,value
__like=key,value
__ilike=key,value
__match=key,value

Order:
__order=key,[desc|asc]
"""
__all__ = ["extractor_from", "is_pagination_field", "is_order_field", "is_filter_field", "is_composite_filter_field"]


def _make_operator_filed(name):
    return "__%s" % name


EXTRACTORS = {}

LIMIT_FIELD = "__limit"
OFFSET_FIELD = "__offset"
PAGINATION_FIELDS = {LIMIT_FIELD, OFFSET_FIELD}


AND_OPERATOR_FIELD = _make_operator_filed(AND_FILTER)
OR_OPERATOR_FIELD = _make_operator_filed(OR_FILTER)
IN_OPERATOR_FIELD = _make_operator_filed(IN_FILTER)
NOT_IN_OPERATOR_FIELD = _make_operator_filed(NOT_IN_FILTER)
EQUAL_OPERATOR_FIELD = _make_operator_filed(EQ_FILTER)
NOT_EQUAL_OPERATOR_FIELD = _make_operator_filed(NE_FILTER)
GREATER_THAN_OPERATOR_FIELD = _make_operator_filed(GT_FILTER)
LESS_THAN_OPERATOR_FIELD = _make_operator_filed(LT_FILTER)
GREATER_THAN_OR_EQUAL_OPERATOR_FIELD = _make_operator_filed(GE_FILTER)
LESS_THAN_OR_EQUAL_OPERATOR_FIELD = _make_operator_filed(LE_FILTER)
LIKE_OPERATOR_FIELD = _make_operator_filed(LIKE_FILTER)
ILIKE_OPERATOR_FIELD = _make_operator_filed(ILIKE_FILTER)
MATCH_OPERATOR_FIELD = _make_operator_filed(MATCH_FILTER)

FILTER_FIELDS = {
    AND_OPERATOR_FIELD, OR_OPERATOR_FIELD, IN_OPERATOR_FIELD,
    NOT_IN_OPERATOR_FIELD, EQUAL_OPERATOR_FIELD, NOT_EQUAL_OPERATOR_FIELD,
    LIKE_OPERATOR_FIELD, ILIKE_OPERATOR_FIELD, MATCH_OPERATOR_FIELD,
    GREATER_THAN_OPERATOR_FIELD, LESS_THAN_OPERATOR_FIELD,
    GREATER_THAN_OR_EQUAL_OPERATOR_FIELD, LESS_THAN_OR_EQUAL_OPERATOR_FIELD
}

COMPOSITE_FILTER_FIELDS = {AND_OPERATOR_FIELD, OR_OPERATOR_FIELD}


ORDER_FIELD = "__order"


class ExtractError(Exception):
    def __init__(self, message):
        self.message = message


class Converter(object):
    def convert(self, value):
        raise NotImplementedError()


class DefaultConverter(Converter):
    def convert(self, value):
        try:
            return str(value)
        except Exception:
            raise ExtractError("Cannot convert to string")


class IntConverter(Converter):
    __slots__ = ("_min", "_max")

    # noinspection PyShadowingBuiltins
    def __init__(self, min=0, max=sys.maxsize):
        self._min = min
        self._max = max

    def convert(self, value):
        try:
            value = int(value)
        except Exception:
            raise ExtractError("{} is not an integer".format(value))
        else:
            if value < self._min or value > self._max:
                raise ExtractError("{} is not in [{}, {}]".format(value, self._min, self._max))
            return value


class TupleConverter(Converter):
    __slots__ = ("_separator", "_range", "_min_size")

    # noinspection PyShadowingBuiltins
    def __init__(self, separator=",", range=(2, 2), min_size=None):
        self._separator = separator
        self._range = range
        self._min_size = min_size

    def convert(self, value):
        # if self._separator not in value:
        #     raise ExtractError("{} need to be separated by {}".format(value, self._separator))
        value = value.split(self._separator)
        if not (self._range[0] <= len(value) <= self._range[1]):
            raise ExtractError("{}'s size is not in [{}, {}]".format(str(value), *self._range))
        if self._min_size:
            for i in range(len(value), self._min_size):
                value.append("")
        return tuple(value)


class Reviser(object):
    def revise(self, value):
        raise NotImplementedError()


class DefaultReviser(Reviser):
    def revise(self, value):
        return value


class KeyMultiValuesReviser(Reviser):
    def revise(self, value):
        _value = (value[0], value[1:])
        return _value


class KeyOperatorReviser(Reviser):
    __slots__ = ("_allowed_operators", "_default_operator")

    def __init__(self, allowed_operators=(), default_operator=None):
        self._allowed_operators = allowed_operators
        self._default_operator = default_operator

    def revise(self, value):
        _value = (value[0], value[-1] if value[-1] else self._default_operator)
        if _value[-1] not in self._allowed_operators:
            raise ExtractError("{} is not in {}".format(value[-1], str(self._allowed_operators)))
        return _value


class KeyValueOperatorReviser(Reviser):
    __slots__ = ("_allowed_operators", "_default_operator")

    def __init__(self, allowed_operators=(), default_operator=None):
        self._allowed_operators = allowed_operators
        self._default_operator = default_operator

    def revise(self, value):
        operator = value[-1] if value[-1] else self._default_operator
        if operator not in self._allowed_operators:
            raise ExtractError("{} is not in {}".format(operator, str(self._allowed_operators)))
        return operator, (value[0], value[1])


class FieldExtractorRegistry(type):
    def __new__(mcs, name, bases, dct):
        cls = super(FieldExtractorRegistry, mcs).__new__(mcs, name, bases, dct)
        if bases != (object,):
            field_name = dct.get("field_name")
            if field_name:
                EXTRACTORS[field_name] = getattr(cls, "extract")
        return cls


class FieldExtractor(object, metaclass=FieldExtractorRegistry):
    field_name = None
    converter = DefaultConverter()
    reviser = DefaultReviser()

    @staticmethod
    def convert_and_revise(value, converter=converter, reviser=reviser):
        if isinstance(value, list):
            for i in range(0, len(value)):
                value[i] = converter.convert(value[i])
                value[i] = reviser.revise(value[i])
        else:
            value = converter.convert(value)
            value = reviser.revise(value)
        return value

    @classmethod
    def extract(cls, param):
        if cls.field_name not in param:
            return None
        filed_value = param[cls.field_name]
        try:
            return cls.convert_and_revise(filed_value, cls.converter, cls.reviser)
        except ExtractError as e:
            raise HTTPInvalidParam(
                e.message, cls.field_name
            )


class AndOperatorFieldExtractor(FieldExtractor):
    field_name = AND_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 3), min_size=3)
    reviser = KeyValueOperatorReviser(
        allowed_operators=(
            EQ_FILTER, NE_FILTER, GT_FILTER, LT_FILTER, GE_FILTER,
            LE_FILTER, LIKE_FILTER, ILIKE_FILTER, MATCH_FILTER
        ),
        default_operator=EQ_FILTER
    )


class OrOperatorFieldExtractor(FieldExtractor):
    field_name = OR_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 3), min_size=3)
    reviser = KeyValueOperatorReviser(
        allowed_operators=(
            EQ_FILTER, NE_FILTER, GT_FILTER, LT_FILTER, GE_FILTER,
            LE_FILTER, LIKE_FILTER, ILIKE_FILTER, MATCH_FILTER
        ),
        default_operator=EQ_FILTER
    )


class InOperatorFieldExtractor(FieldExtractor):
    field_name = IN_OPERATOR_FIELD
    converter = TupleConverter(range=(2, sys.maxsize))
    reviser = KeyMultiValuesReviser()


class NotInOperatorFieldExtractor(FieldExtractor):
    field_name = NOT_IN_OPERATOR_FIELD
    converter = TupleConverter(range=(2, sys.maxsize))
    reviser = KeyMultiValuesReviser()


class EqualOperatorFieldExtractor(FieldExtractor):
    field_name = EQUAL_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class NotEqualOperatorFieldExtractor(FieldExtractor):
    field_name = NOT_EQUAL_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class GreaterThanOperatorFieldExtractor(FieldExtractor):
    field_name = GREATER_THAN_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class LessThanOperatorFieldExtractor(FieldExtractor):
    field_name = LESS_THAN_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class GreaterThanOrEqualOperatorFieldExtractor(FieldExtractor):
    field_name = GREATER_THAN_OR_EQUAL_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class LessThanOrEqualOperatorFieldExtractor(FieldExtractor):
    field_name = LESS_THAN_OR_EQUAL_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class LikeOperatorFieldExtractor(FieldExtractor):
    field_name = LIKE_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class ILikeOperatorFieldExtractor(FieldExtractor):
    field_name = ILIKE_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class MatchOperatorFieldExtractor(FieldExtractor):
    field_name = MATCH_OPERATOR_FIELD
    converter = TupleConverter(range=(2, 2))
    reviser = DefaultReviser()


class LimitFieldExtractor(FieldExtractor):
    field_name = LIMIT_FIELD
    converter = IntConverter()
    reviser = DefaultReviser()

    @classmethod
    def extract(cls, param):
        value = super(LimitFieldExtractor, cls).extract(param)
        if isinstance(value, list):
            return value[-1]
        return value


class OffsetFieldExtractor(FieldExtractor):
    field_name = OFFSET_FIELD
    converter = IntConverter()
    reviser = DefaultReviser()

    @classmethod
    def extract(cls, param):
        value = super(OffsetFieldExtractor, cls).extract(param)
        if isinstance(value, list):
            return value[-1]
        return value


class OrderFieldExtractor(FieldExtractor):
    field_name = ORDER_FIELD
    converter = TupleConverter(range=(1, 2), min_size=2)
    reviser = KeyOperatorReviser(
        allowed_operators=("desc", "asc"), default_operator="desc"
    )


def extractor_from(string):
    def extract(name, param):
        value = param.get(name)
        try:
            return FieldExtractor.convert_and_revise(value)
        except ExtractError as e:
            raise HTTPInvalidParam(e.message, name)

    if string in EXTRACTORS:
        return EXTRACTORS[string]
    return partial(extract, string)


def is_pagination_field(field):
    return field in PAGINATION_FIELDS


def is_order_field(field):
    return field == ORDER_FIELD


def is_filter_field(field):
    return field in FILTER_FIELDS


def is_composite_filter_field(field):
    return field in COMPOSITE_FILTER_FIELDS
