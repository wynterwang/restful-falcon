# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/28"
from __future__ import absolute_import

from restful_falcon.core.controller.base import Resource
from restful_falcon.core.exception import AuthenticationError
from restful_falcon.core.exception import PermissionError
from restful_falcon.core.middleware.base import Middleware

__all__ = ["AuthenticationMiddleware", "PermissionMiddleware"]


class AuthenticationMiddleware(Middleware):
    def process_resource(self, req, resp, resource, params):
        if isinstance(resource, Resource) or hasattr(resource, "authentications"):
            if callable(resource.authentications):
                authentications = resource.authentications()
            else:
                authentications = resource.authentications
            if not authentications:
                return
            if not isinstance(authentications, list):
                authentications = [authentications]
            for authentication in authentications:
                if authentication.match(req):
                    req.user = authentication.authenticate(req)
                    if req.user:
                        break
            if not req.user:
                raise AuthenticationError(
                    description="Incorrect credentials"
                )


class PermissionMiddleware(Middleware):
    def process_resource(self, req, resp, resource, params):
        if isinstance(resource, Resource) or hasattr(resource, "permissions"):
            if callable(resource.permissions):
                permissions = resource.permissions()
            else:
                permissions = resource.permissions
            if not permissions:
                return
            if not isinstance(permissions, list):
                permissions = [permissions]
            for permission in permissions:
                if permission.has_permission(req):
                    return
            raise PermissionError(
                description="Not allowed to operate the resource"
            )
