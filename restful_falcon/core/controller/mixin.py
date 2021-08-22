# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/25"
from __future__ import absolute_import

from restful_falcon.core.controller.base import Context
from restful_falcon.core.controller.base import Resource
from restful_falcon.core.exception import HTTPNotFound

__all__ = [
    "ListOperateMixin", "CreateOperateMixin", "ShowOperateMixin", "UpdateOperateMixin", "DeleteOperateMixin",
    "ResourceQueryOperatesMixin", "ResourceOperatesMixin"
]


class ListOperateMixin:
    def on_get(self, request, response, **params):
        """
        Get method

        :type self: restful_falcon.core.controller.base.Resource, ListOperateMixin
        :param request: request object
        :type request: restful_falcon.core.request.Request
        :param response: response object
        :type response: restful_falcon.core.response.Response
        :param params: extend parameters
        :type params: dict
        """
        if self.has_schema():
            validator = self.schema.list_validator()
            validator and validator(request)
        with Context(self, request, response, params) as context:
            data = self.list(
                context, filters=context.filters, orders=context.orders,
                limit=context.limit, offset=context.offset
            )
            response.media = {"count": data[0], "data": data[1]} if data else {"count": 0, "data": []}

    def list(self, context, filters=None, orders=None, limit=None, offset=None):
        """
        List resources

        :type self: restful_falcon.core.controller.base.Resource
        :param context: context object
        :type context: restful_falcon.core.controller.base.Context
        :param filters: filter list
        :type filters: list
        :param orders: order list
        :type orders: list
        :param limit: limit number
        :type limit: int
        :param offset: offset number
        :type offset: int
        :rtype: tuple
        """
        if isinstance(self, Resource) and self.has_model():
            return self.resource_model.perform_list(
                filters=filters, orders=orders, limit=limit, offset=offset, session=context.session
            )


class CreateOperateMixin:
    def on_post(self, request, response, **params):
        """
        Post method

        :type self: restful_falcon.core.controller.base.Resource, CreateOperateMixin
        :param request: request object
        :type request: restful_falcon.core.request.Request
        :param response: response object
        :type response: restful_falcon.core.response.Response
        :param params: extend parameters
        :type params: dict
        """
        if self.has_schema():
            validator = self.schema.create_validator()
            validator and validator(request)
        with Context(self, request, response, params, autocommit=True) as context:
            data = self.create(context, context.request_data)
            if data:
                response.media = data

    def create(self, context, data):
        """
        Create a resource

        :type self: restful_falcon.core.controller.base.Resource
        :param context: context object
        :type context: restful_falcon.core.controller.base.Context
        :param data: data to be created
        :type data: dict
        :rtype: dict
        """
        if isinstance(self, Resource) and self.has_model():
            return self.resource_model.perform_create(data, session=context.session)


class ShowOperateMixin:
    def on_get_item(self, request, response, **params):
        """
        Get item method

        :type self: restful_falcon.core.controller.base.Resource, ShowOperateMixin
        :param request: request object
        :type request: restful_falcon.core.request.Request
        :param response: response object
        :type response: restful_falcon.core.response.Response
        :param params: extend parameters
        :type params: dict
        """
        with Context(self, request, response, params) as context:
            data = self.show(context, params[self.resource_id], filters=context.filters)
            if data:
                response.media = data
            else:
                raise HTTPNotFound()

    def show(self, context, resource_id, filters=None):
        """
        Get detail information of a resource

        :type self: restful_falcon.core.controller.base.Resource
        :param context: context object
        :type context: restful_falcon.core.controller.base.Context
        :param resource_id: resource id
        :param filters: filter list
        :type filters: list
        :rtype: dict
        """
        if isinstance(self, Resource) and self.has_model():
            return self.resource_model.perform_show(
                resource_id, filters=filters, session=context.session
            )


class UpdateOperateMixin:
    def on_put_item(self, request, response, **params):
        """
        Put item method

        :type self: restful_falcon.core.controller.base.Resource, UpdateOperateMixin
        :param request: request object
        :type request: restful_falcon.core.request.Request
        :param response: response object
        :type response: restful_falcon.core.response.Response
        :param params: extend parameters
        :type params: dict
        """
        if self.has_schema():
            validator = self.schema.update_validator()
            validator and validator(request)
        with Context(self, request, response, params, autocommit=True) as context:
            data = self.update(
                context, params[self.resource_id],
                context.request_data, filters=context.filters
            )
            if data:
                response.media = data
            else:
                raise HTTPNotFound()

    def update(self, context, resource_id, data, filters=None):
        """
        Update a resource

        :type self: restful_falcon.core.controller.base.Resource
        :param context: context object
        :type context: restful_falcon.core.controller.base.Context
        :param resource_id: resource id
        :param data: data to be updated
        :type data: dict
        :param filters: filter list
        :type filters: list
        :rtype: dict
        """
        if isinstance(self, Resource) and self.has_model():
            return self.resource_model.perform_update(
                resource_id, data, filters=filters, session=context.session
            )


class DeleteOperateMixin:
    def on_delete_item(self, request, response, **params):
        """
        Delete item method

        :type self: restful_falcon.core.controller.base.Resource, DeleteOperateMixin
        :param request: request object
        :type request: restful_falcon.core.request.Request
        :param response: response object
        :type response: restful_falcon.core.response.Response
        :param params: extend parameters
        :type params: dict
        """
        with Context(self, request, response, params, autocommit=True) as context:
            data = self.delete(context, params[self.resource_id], filters=context.filters)
            if data:
                response.media = data
            else:
                raise HTTPNotFound()

    def delete(self, context, resource_id, filters=None):
        """
        Delete a resource

        :type self: restful_falcon.core.controller.base.Resource
        :param context: context object
        :type context: restful_falcon.core.controller.base.Context
        :param resource_id: resource id
        :param filters: filter list
        :type filters: list
        :rtype: dict
        """
        if isinstance(self, Resource) and self.has_model():
            return self.resource_model.perform_delete(
                resource_id, filters=filters, session=context.session
            )


class ResourceQueryOperatesMixin(ListOperateMixin, ShowOperateMixin):
    pass


class ResourceOperatesMixin(
    ListOperateMixin, CreateOperateMixin,
    ShowOperateMixin, UpdateOperateMixin, DeleteOperateMixin
):
    pass
