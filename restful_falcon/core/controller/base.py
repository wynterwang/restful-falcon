# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/25"
from __future__ import absolute_import

import traceback
from collections import Iterable
from logging import getLogger

import copy

from restful_falcon.core.auth.base import Authentication
from restful_falcon.core.config import CONF
from restful_falcon.core.controller.extractor import extractor_from
from restful_falcon.core.controller.extractor import is_composite_filter_field
from restful_falcon.core.controller.extractor import is_filter_field
from restful_falcon.core.controller.extractor import is_order_field
from restful_falcon.core.controller.extractor import is_pagination_field
from restful_falcon.core.controller.isolation import ResourceIsolation
from restful_falcon.core.controller.isolation import ResourceIsolationByUser
from restful_falcon.core.controller.validator import ResourceSchema
from restful_falcon.core.db.engine import Session
from restful_falcon.core.exception import HTTPInvalidParam
from restful_falcon.core.permission.base import Permission
from restful_falcon.util.module import import_obj
from restful_falcon.util.string import to_snake_case
from restful_falcon.util.wrapper import lazy_property

__all__ = ["Resource", "Context"]

logger = getLogger(__name__)


class ResourceMeta(type):
    def __new__(mcs, name, bases, dct):
        if bases != (object,):
            if "resource_name" not in dct:
                dct["resource_name"] = to_snake_case(name)
        return super(ResourceMeta, mcs).__new__(mcs, name, bases, dct)


class Resource(object, metaclass=ResourceMeta):
    authentication_classes = CONF.get("authentication")
    auto_fill_fields = True
    permission_classes = CONF.get("permission")
    resource_id = "rid"
    resource_name = None
    resource_model = None
    resource_isolation = False
    resource_isolation_class = ResourceIsolationByUser
    validator_schema = None

    def has_model(self):
        return self.resource_model is not None

    def has_schema(self):
        return self.validator_schema is not None

    @lazy_property
    def authentications(self):
        authentications = self.authentication_classes or []
        if isinstance(authentications, Iterable):
            authentications = list(authentications)
        else:
            authentications = [authentications]
        for i in range(0, len(authentications)):
            try:
                authentications[i] = import_obj(authentications[i], bases=(Authentication,))
            except Exception as e:
                logger.warning(str(e))
                logger.warning(traceback.format_exc())
        return authentications

    @lazy_property
    def permissions(self):
        permissions = self.permission_classes or []
        if isinstance(permissions, Iterable):
            permissions = list(permissions)
        else:
            permissions = [permissions]
        for i in range(0, len(permissions)):
            try:
                permissions[i] = import_obj(permissions[i], bases=(Permission,))
            except Exception as e:
                logger.warning(str(e))
                logger.warning(traceback.format_exc())
        return permissions

    @lazy_property
    def schema(self):
        if isinstance(self.validator_schema, ResourceSchema):
            return self.validator_schema
        elif isinstance(self.validator_schema, dict):
            if all(attr not in self.validator_schema for attr in ["list", "create", "update"]):
                return ResourceSchema(self.validator_schema)
            return ResourceSchema(
                list=self.validator_schema.get("list"),
                create=self.validator_schema.get("create"),
                update=self.validator_schema.get("update")
            )
        raise TypeError(
            "`{}.validator_schema` should be an object with type "
            "in [ResourceSchema, dict]".format(self.__class__.__name__)
        )

    @lazy_property
    def isolation_obj(self):
        if issubclass(self.resource_isolation_class, ResourceIsolation):
            return self.resource_isolation_class()
        elif isinstance(self.resource_isolation_class, str):
            return import_obj(self.resource_isolation_class, bases=(ResourceIsolation,))
        raise TypeError(
            "`{}.resource_isolation_class` should be an object with type "
            "in [ResourceIsolation, str]".format(self.__class__.__name__)
        )


class Context(object):
    def __init__(self, resource, request, response, params, autocommit=False):
        """
        Context constructor

        :param resource: resource object
        :type resource: Resource
        :param request: request object
        :type request: restful_falcon.core.request.Request
        :param response: response object
        :type response: restful_falcon.core.response.Response
        :param params: extend parameters
        :type params: dict
        """
        self.resource = resource
        self.__request = request
        self.__response = response
        self.params = params
        self.session = None
        self.autocommit = autocommit
        self._extract_query_params()

    def __enter__(self):
        if hasattr(self.resource, "has_model"):
            if self.resource.has_model():
                self.session = Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if self.autocommit and not exc_val:
                self.session.commit()
            self.session.close()

    def __init_specific_fields(self):
        self.__limit = None
        self.__offset = None
        self.__orders = None
        self.__filters = []

    def __extract_pagination_filed(self, field):
        attr_name = "_{}{}".format(self.__class__.__name__, field)
        setattr(self, attr_name, extractor_from(field)(self.request.params))

    def __extract_orders_filed(self, field):
        attr_name = "_{}__orders".format(format(self.__class__.__name__))
        attr_value = extractor_from(field)(self.request.params)
        setattr(self, attr_name, attr_value if isinstance(attr_value, list) else [attr_value])

    def __extract_filter_field(self, field):
        field_value = extractor_from(field)(self.request.params)
        if is_composite_filter_field(field):
            if not isinstance(field_value, list):
                raise HTTPInvalidParam("Need multiple items", field)
            self.__filters.append((field.strip("_"), field_value))
        else:
            field_values = field_value
            if not isinstance(field_values, list):
                field_values = [field_values]
            for field_value in field_values:
                self.__filters.append((field.strip("_"), field_value))

    def __extract_normal_field(self, field):
        field_values = extractor_from(field)(self.request.params)
        if not isinstance(field_values, list):
            field_values = [field_values]
        for field_value in field_values:
            self.__filters.append((field, field_value))

    def _extract_query_params(self):
        self.__init_specific_fields()
        for field in self.request.params:
            _field = field.lower()
            if is_pagination_field(_field):
                self.__extract_pagination_filed(_field)
            elif is_order_field(_field):
                self.__extract_orders_filed(_field)
            elif is_filter_field(_field):
                self.__extract_filter_field(_field)
            else:
                self.__extract_normal_field(field)

    @property
    def request(self):
        """
        Request getter

        :return: request object
        :rtype: restful_falcon.core.request.Request
        """
        return self.__request

    @property
    def response(self):
        """
        Response getter

        :return: response object
        :rtype: restful_falcon.core.response.Response
        """
        return self.__response

    @property
    def limit(self):
        return self.__limit

    @property
    def offset(self):
        return self.__offset

    @property
    def orders(self):
        return self.__orders

    def _isolation_filters(self):
        filters = None
        if self.resource.resource_isolation and self.resource.isolation_obj:
            filters = self.resource.isolation_obj.isolation_filters(self.__request)
        return filters or []

    @lazy_property
    def filters(self):
        isolation_filters = self._isolation_filters()
        if isolation_filters:
            self.__filters.extend(isolation_filters)
        return self.__filters

    @lazy_property
    def request_data(self):
        def try_fill_fields(_data):
            try:
                if self.resource.auto_fill_fields and getattr(self.resource.resource_model, "require_auto_fill", False):
                    if hasattr(self.resource.resource_model, "auto_fill_fields"):
                        create = True if self.request.method == "POST" else False
                        for field in self.resource.resource_model.auto_fill_fields(create):
                            _data[field[0]] = getattr(self.request.user, field[1])
            except Exception as e:
                logger.debug(str(e))
                logger.debug(traceback.format_exc())
            finally:
                return _data

        data = copy.copy(self.request.media)
        return try_fill_fields(data)
