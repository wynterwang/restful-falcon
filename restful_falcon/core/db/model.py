# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/17"
from __future__ import absolute_import

import traceback
from logging import getLogger

import copy
from functools import wraps
# noinspection PyUnresolvedReferences
from sqlalchemy import BLANK_SCHEMA
# noinspection PyUnresolvedReferences
from sqlalchemy import CheckConstraint
# noinspection PyUnresolvedReferences
from sqlalchemy import Column
# noinspection PyUnresolvedReferences
from sqlalchemy import ColumnDefault
# noinspection PyUnresolvedReferences
from sqlalchemy import Computed
# noinspection PyUnresolvedReferences
from sqlalchemy import Constraint
# noinspection PyUnresolvedReferences
from sqlalchemy import DDL
# noinspection PyUnresolvedReferences
from sqlalchemy import DefaultClause
# noinspection PyUnresolvedReferences
from sqlalchemy import FetchedValue
# noinspection PyUnresolvedReferences
from sqlalchemy import ForeignKey
# noinspection PyUnresolvedReferences
from sqlalchemy import ForeignKeyConstraint
# noinspection PyUnresolvedReferences
from sqlalchemy import IdentityOptions
# noinspection PyUnresolvedReferences
from sqlalchemy import Index
# noinspection PyUnresolvedReferences
from sqlalchemy import MetaData
# noinspection PyUnresolvedReferences
from sqlalchemy import PassiveDefault
# noinspection PyUnresolvedReferences
from sqlalchemy import PrimaryKeyConstraint
# noinspection PyUnresolvedReferences
from sqlalchemy import Sequence
# noinspection PyUnresolvedReferences
from sqlalchemy import Table
# noinspection PyUnresolvedReferences
from sqlalchemy import ThreadLocalMetaData
# noinspection PyUnresolvedReferences
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.attributes import QueryableAttribute

from restful_falcon.core.db.engine import Session
from restful_falcon.core.db.filter import make_filter
from restful_falcon.util.string import to_snake_case

__all__ = [
    "BLANK_SCHEMA", "CheckConstraint", "Column", "ColumnDefault", "Computed", "Constraint", "DDL", "DefaultClause",
    "FetchedValue", "ForeignKey", "ForeignKeyConstraint", "IdentityOptions", "Index", "MetaData", "PassiveDefault",
    "PrimaryKeyConstraint", "Sequence", "Table", "ThreadLocalMetaData", "UniqueConstraint", "Model"
]

logger = getLogger(__name__)


def process_if_no_session(autocommit=False):
    def wrapper(func):
        @wraps(func)
        def _wrapper(cls, *args, **kwargs):
            if kwargs.get("session"):
                return func(cls, *args, **kwargs)
            kwargs["session"] = Session()
            result = func(cls, *args, **kwargs)
            if autocommit:
                kwargs["session"].commit()
            return result
        return _wrapper
    return wrapper


class BaseModel(object):
    id_field = "id"
    show_columns = None

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        return "{}s".format(to_snake_case(cls.__name__))

    __table_args__ = {"useexisting": True}

    def __repr__(self):
        columns = self.show_columns or self.columns()
        return "<{cls}({val})>".format(
            cls=self.__class__.__name__,
            val=",".join(("{}={}".format(column, getattr(self, column)) for column in columns))
        )

    def __str__(self):
        columns = self.show_columns or self.columns()
        return "<{cls}({val})>".format(
            cls=self.__class__.__name__,
            val=",".join(("{}={}".format(column, getattr(self, column)) for column in columns))
        )

    def to_dict(self):
        columns = self.columns()
        return dict([(column, getattr(self, column)) for column in columns])

    @classmethod
    def columns(cls):
        if hasattr(cls, "_table_columns"):
            return getattr(cls, "_table_columns")
        _table_columns = []
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), QueryableAttribute):
                _table_columns.append(attr)
        setattr(cls, "_table_columns", _table_columns)
        return _table_columns

    @classmethod
    def record_to_dict(cls, record, columns=None):
        if record:
            if isinstance(record, cls):
                return record.to_dict()
            if not isinstance(record, (list, tuple)) or not isinstance(columns, (list, tuple)):
                raise ValueError(
                    "{}.record_to_dict: record or columns type error".format(cls.__name__)
                )
            if len(record) != len(columns):
                raise ValueError(
                    "{}.record_to_dict: the length of record and columns is not equal".format(cls.__name__)
                )
            _record = {}
            for i in range(0, len(record)):
                _record[columns[i]] = record[i]
            return _record
        return {}

    @classmethod
    def records_to_list(cls, records, columns=None):
        _records = []
        for record in records:
            _records.append(cls.record_to_dict(record, columns=columns))
        return _records

    @classmethod
    def make_query(cls, session, columns=None):
        if columns:
            return session.query(
                *(getattr(cls, column) for column in columns if hasattr(cls, column))
            )
        else:
            return session.query(cls)

    # noinspection PyShadowingBuiltins
    @classmethod
    def add_filter(cls, query, filter):
        """
        Add filter to query

        :param query: query object
        :type query: sqlalchemy.orm.Query
        :param filter: filter object
        :type filter: tuple, sqlalchemy.sql.operators.ColumnOperators
        :return: query object
        :rtype: sqlalchemy.orm.Query

        Filter definition:
            filter := [equal_filter | simple_filter | composite_filter]
            equal_filter := (attr_name, attr_value)
            simple_filter := (filter_name, (attr_name, attr_value)),
                            where filter_name in ["eq", "ne", "gt", "lt", "ge",
                            "le", "like", "ilike", "match", "in", "not_in"]
            composite_filter := (filter_name, ([equal_filter|simple_filter] ...)),
                            where filter_name in ["and", "or"]

        Filter examples:
            1) equal_filter: ("name", "test"), ("age", 18);
            2) simple_filter: ("like", ("name", "test")), ("ge", ("age", 18));
            3) composite_filter: ("and", (("like", ("name", "test")), ("age", 18))).
        """
        try:
            filter = make_filter(cls, filter)
            query = query.filter(filter)
        except Exception as e:
            logger.warning(str(e))
            logger.warning(traceback.format_exc())
        finally:
            return query

    @classmethod
    def add_filters(cls, query, filters):
        """
        Add filters to query

        :param query: query object
        :type query: sqlalchemy.orm.Query
        :param filters: filter object list
        :type filters: collections.Iterable
        :return: query object
        :rtype: sqlalchemy.orm.Query
        """
        if not filters or not isinstance(filters, list):
            logger.debug("Add filters ({}) failed, ignore".format(str(filters)))
            return query
        # noinspection PyShadowingBuiltins
        for filter in filters:
            query = cls.add_filter(query, filter)
        return query

    @classmethod
    def add_order(cls, query, order):
        def check():
            try:
                if not isinstance(order, tuple) or len(order) != 2:
                    raise TypeError("Order field ({}) requires a tuple with size 2".format(str(order)))
                if not hasattr(cls, order[0]):
                    raise AttributeError("Model ({}) has not attribute ({})".format(cls.__name__, order[0]))
                order_list = ["desc", "asc"]
                if order[1].lower() not in order_list:
                    raise ValueError("Order should be in {}".format(str(order_list)))
                return True
            except Exception as e:
                logger.warning(str(e))
                logger.warning(traceback.format_exc())
                return False

        if check():
            field = getattr(cls, order[0])
            query = query.order_by(getattr(field, order[1])())
        return query

    @classmethod
    def add_orders(cls, query, orders):
        if not orders or not isinstance(orders, list):
            logger.debug("Add orders ({}) failed, ignore".format(str(orders)))
            return query
        for order in orders:
            query = cls.add_order(query, order)
        return query

    @classmethod
    def add_limit(cls, query, limit):
        try:
            if limit is not None:
                limit = int(limit)
                query = query.limit(limit)
        except Exception as e:
            logger.warning(str(e))
            logger.warning(traceback.format_exc())
        finally:
            return query

    @classmethod
    def add_offset(cls, query, offset):
        try:
            if offset is not None:
                offset = int(offset)
                query = query.offset(offset)
        except Exception as e:
            logger.warning(str(e))
            logger.warning(traceback.format_exc())
        finally:
            return query

    @classmethod
    def perform_list(cls, session=None, columns=None, filters=None, orders=None, limit=None, offset=None):
        return cls._perform_list(
            session=session, columns=columns, filters=filters, orders=orders, limit=limit, offset=offset
        )

    @classmethod
    @process_if_no_session()
    def _perform_list(cls, session=None, columns=None, filters=None, orders=None, limit=None, offset=None):
        count, records = cls.list(
            session, columns=columns, filters=filters,
            orders=orders, limit=limit, offset=offset,
        )
        return count, cls.records_to_list(records, columns=columns)

    @classmethod
    def list(cls, session, columns=None, filters=None, orders=None, limit=None, offset=None):
        """
        List operate

        :param session: session object
        :type session: restful_falcon.core.db.engine.Session
        :param columns: column list
        :type columns: list
        :param filters: filter list
        :type filters: collections.Iterable
        :param orders: order list
        :type orders: collections.Iterable
        :param limit: limit number
        :type limit: int
        :param offset: offset number
        :type offset: int
        :return: number of records and records
        :rtype: tuple
        """
        query = cls.make_query(session, columns=columns)
        query = cls.add_filters(query, filters)
        query = cls.add_orders(query, orders)
        count = query.count()
        query = cls.add_limit(query, limit)
        query = cls.add_offset(query, offset)
        return count, query.all()

    @classmethod
    def perform_create(cls, data, session=None):
        return cls._perform_create(data, session=session)

    @classmethod
    @process_if_no_session(autocommit=True)
    def _perform_create(cls, data, session=None):
        record = cls.create(session, data)
        return cls.record_to_dict(record)

    @classmethod
    def create(cls, session, data):
        """
        Create operate

        :param session: session object
        :type session: restful_falcon.core.db.engine.Session
        :param data: record data
        :type data: dict
        :return: the created record
        """
        # noinspection PyArgumentList
        record = cls(**data)
        session.add(record)
        session.flush()
        return record

    @classmethod
    def perform_show_by(cls, filters, session=None):
        return cls._perform_show_by(filters, session=session)

    @classmethod
    @process_if_no_session()
    def _perform_show_by(cls, filters, session=None):
        record = cls.show_by(session, filters)
        return cls.record_to_dict(record)

    @classmethod
    def show_by(cls, session, filters):
        query = cls.make_query(session)
        query = cls.add_filters(query, filters)
        return query.first()

    @classmethod
    def perform_show(cls, rid, filters=None, session=None):
        return cls._perform_show(rid, filters=filters, session=session)

    @classmethod
    @process_if_no_session()
    def _perform_show(cls, rid, filters=None, session=None):
        record = cls.show(session, rid, filters=filters)
        return cls.record_to_dict(record)

    @classmethod
    def show(cls, session, rid, filters=None):
        """
        Show operate

        :param session: session object
        :type session: restful_falcon.core.db.engine.Session
        :param rid: id value
        :param filters: filter list
        :type filters: list
        :return: the current record
        """
        filters = copy.deepcopy(filters) if filters else []
        filters.insert(0, (cls.id_field, rid))
        return cls.show_by(session, filters)

    @classmethod
    def perform_update_by(cls, filters, data, session=None):
        return cls._perform_update_by(filters, data, session=session)

    @classmethod
    @process_if_no_session(autocommit=True)
    def _perform_update_by(cls, filters, data, session=None):
        records = cls.update_by(session, filters, data)
        return cls.records_to_list(records)

    @classmethod
    def update_by(cls, session, filters, data):
        if not filters:
            return []
        query = cls.make_query(session)
        query = cls.add_filters(query, filters)
        query.update(data)
        session.flush()
        return query.all()

    @classmethod
    def perform_update(cls, rid, data, filters=None, session=None):
        return cls._perform_update(rid, data, filters=filters, session=session)

    @classmethod
    @process_if_no_session(autocommit=True)
    def _perform_update(cls, rid, data, filters=None, session=None):
        record = cls.update(session, rid, data, filters=filters)
        return cls.record_to_dict(record)

    @classmethod
    def update(cls, session, rid, data, filters=None):
        """
        Update operate

        :param session: session object
        :type session: restful_falcon.core.db.engine.Session
        :param rid: id value
        :param data: update data
        :type data: dict
        :param filters: filter list
        :type filters: list
        :return: the updated record
        """
        filters = copy.deepcopy(filters) if filters else []
        filters.insert(0, (cls.id_field, rid))
        records = cls.update_by(session, filters, data)
        return records[0] if records else {}

    @classmethod
    def perform_delete_by(cls, filters, session=None):
        return cls._perform_delete_by(filters, session=session)

    @classmethod
    @process_if_no_session(autocommit=True)
    def _perform_delete_by(cls, filters, session=None):
        records = cls.delete_by(session, filters)
        return cls.records_to_list(records)

    @classmethod
    def delete_by(cls, session, filters):
        if not filters:
            return []
        query = cls.make_query(session)
        query = cls.add_filters(query, filters)
        records = query.all()
        query.delete()
        return records

    @classmethod
    def perform_delete(cls, rid, filters=None, session=None):
        return cls._perform_delete(rid, filters=filters, session=session)

    @classmethod
    @process_if_no_session(autocommit=True)
    def _perform_delete(cls, rid, filters=None, session=None):
        record = cls.delete(session, rid, filters=filters)
        return cls.record_to_dict(record)

    @classmethod
    def delete(cls, session, rid, filters=None):
        """
        Delete operate

        :param session: session object
        :type session: restful_falcon.core.db.engine.Session
        :param rid: id value
        :param filters: filter list
        :type filters: list
        :return: the deleted record
        """
        filters = copy.deepcopy(filters) if filters else []
        filters.insert(0, (cls.id_field, rid))
        records = cls.delete_by(session, filters)
        return records[0] if records else {}

    @classmethod
    @process_if_no_session()
    def exist(cls, filters, session=None):
        if not filters:
            return False
        query = cls.make_query(session)
        query = cls.add_filters(query, filters)
        return query.count() > 0


Model: BaseModel = declarative_base(name="Model", cls=BaseModel)
