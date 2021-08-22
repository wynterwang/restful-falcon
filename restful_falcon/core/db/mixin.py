# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/18"
from __future__ import absolute_import

from functools import partial
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime
from sqlalchemy.types import Integer
from sqlalchemy.types import String

from restful_falcon.util.string import uuid_str
from restful_falcon.util.time import now

__all__ = [
    "IncrementalIdColumnMixin", "make_uuid_column_mixin", "UUIDTypeIdColumnMixin", "CreateTimeColumnMixin",
    "UpdateTimeColumnMixin", "TimeColumnsMixin", "IdAndTimeColumnsMixin", "make_uuid_and_time_columns_mixin",
    "UUIDAndTimeColumnsMixin", "make_create_user_column_mixin", "CreateUserColumnMixin",
    "make_update_user_column_mixin", "UpdateUserColumnMixin", "make_user_columns_mixin", "UserColumnsMixin"
]


# noinspection PyAbstractClass
class _Column(Column):
    """

    This class is added to control the position of declarative column
    """
    def __init__(self, *args, **kwargs):
        creation_order = kwargs.pop("creation_order", None)
        super(_Column, self).__init__(*args, **kwargs)
        if creation_order:
            self._creation_order = creation_order


class IncrementalIdColumnMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


def make_uuid_column_mixin(with_hyphen=False, length=None):
    if not length:
        length = 36 if with_hyphen else 32
    length = int(length)

    class _UUIDTypeIdColumnMixin:
        id = Column(String(length), primary_key=True, default=partial(uuid_str, with_hyphen=with_hyphen))
    return _UUIDTypeIdColumnMixin


UUIDTypeIdColumnMixin = make_uuid_column_mixin()


class CreateTimeColumnMixin:
    # noinspection PyMethodParameters
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=now)


class UpdateTimeColumnMixin:
    # noinspection PyMethodParameters
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=now, onupdate=now)


class TimeColumnsMixin(CreateTimeColumnMixin, UpdateTimeColumnMixin):
    pass


class IdAndTimeColumnsMixin(IncrementalIdColumnMixin, TimeColumnsMixin):
    pass


def make_uuid_and_time_columns_mixin(with_hyphen=False, length=None):
    class _UUIDAndTimeColumnsMixin(
        make_uuid_column_mixin(with_hyphen=with_hyphen, length=length), TimeColumnsMixin
    ):
        pass
    return _UUIDAndTimeColumnsMixin


UUIDAndTimeColumnsMixin = make_uuid_and_time_columns_mixin()


# noinspection PyShadowingBuiltins
def make_create_user_column_mixin(type=Integer, index=True, nullable=True, default=None):
    class _CreateUserColumnMixin:
        require_auto_fill = True

        # noinspection PyUnusedLocal
        @classmethod
        def auto_fill_fields(cls, create=True):
            if not create:
                return []
            return [("created_by", "id")]

        # noinspection PyMethodParameters
        @declared_attr
        def created_by(cls):
            return Column(type, index=index, nullable=nullable, default=default)
    return _CreateUserColumnMixin


CreateUserColumnMixin = make_create_user_column_mixin()


# noinspection PyShadowingBuiltins
def make_update_user_column_mixin(type=Integer, index=False, nullable=True, default=None):
    class _UpdateUserColumnMixin:
        require_auto_fill = True

        # noinspection PyUnusedLocal
        @classmethod
        def auto_fill_fields(cls, create=True):
            return [("updated_by", "id")]

        # noinspection PyMethodParameters
        @declared_attr
        def updated_by(cls):
            return Column(type, index=index, nullable=nullable, default=default)
    return _UpdateUserColumnMixin


UpdateUserColumnMixin = make_update_user_column_mixin()


# noinspection PyShadowingBuiltins
def make_user_columns_mixin(type=Integer, create_index=True, update_index=False, nullable=True, default=None):
    class _UserColumnsMixin(
        make_create_user_column_mixin(type=type, index=create_index, nullable=nullable, default=default),
        make_update_user_column_mixin(type=type, index=update_index, nullable=nullable, default=default)
    ):
        require_auto_fill = True

        # noinspection PyUnusedLocal
        @classmethod
        def auto_fill_fields(cls, create=True):
            if not create:
                return [("updated_by", "id")]
            return [("created_by", "id"), ("updated_by", "id")]
    return _UserColumnsMixin


UserColumnsMixin = make_user_columns_mixin()
