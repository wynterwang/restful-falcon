# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/31"
from __future__ import absolute_import

from uuid import UUID

from falcon import COMBINED_METHODS
from falcon.routing.converters import BaseConverter

from restful_falcon.util.file import exists
from restful_falcon.util.module import import_attr
from restful_falcon.util.wrapper import lazy_property

__all__ = ["route", "static_route", "Router", "BaseConverter", "UUIDStringConverter"]


def _has_http_method(resource, suffix=None):
    for method in COMBINED_METHODS:
        method_name = "on_" + method.lower()
        if suffix:
            method_name += "_" + suffix
        if hasattr(resource, method_name):
            return True
    return False


def route(uri_template, resource=None, router=None, suffix=None):
    return {
        "uri_template": uri_template, "resource": resource,
        "router": router, "suffix": suffix
    }


def static_route(prefix, directory=None, router=None, downloadable=False, fallback_filename=None):
    return {
        "prefix": prefix, "directory": directory, "router": router,
        "downloadable": downloadable, "fallback_filename": fallback_filename
    }


class RouterError(Exception):
    pass


class RouterInitError(RouterError):
    pass


class RouterAddError(RouterError):
    pass


class Router(object):
    def __init__(self, routes=None, static_routes=None):
        self.__routes = {}
        self.__static_routes = {}
        routes = routes or []
        static_routes = static_routes or []
        if not isinstance(routes, list):
            raise RouterInitError("`routes` must be a list")
        if not isinstance(static_routes, list):
            raise RouterInitError("`static_routes` must be a list")
        for _route in routes:
            if not isinstance(_route, dict):
                raise RouterInitError("item of `routes` must be a dict")
            self.add_route(**_route)
        for _static_route in static_routes:
            if not isinstance(_static_route, dict):
                raise RouterInitError("item of `static_routes` must be a dict")
            self.add_static_route(**_static_route)

    def add_route(self, uri_template, resource=None, router=None, suffix=None):
        """

        :param uri_template: uri string
        :type uri_template: str
        :param resource: resource
        :type resource: Resource
        :param router: router
        :type router: Router, str
        :param suffix: Optional responder name suffix for this route
        :type suffix: str
        """
        if not resource and not router:
            raise RouterAddError(
                "`resource` and `router` must specify at least one: {}".format(uri_template)
            )
        if resource and router:
            raise RouterAddError(
                "`resource` and `router` cannot be specified at the same time: {}".format(uri_template)
            )
        if resource and not _has_http_method(resource, suffix=suffix):
            raise RouterAddError("`resource` has no http method: {}".format(uri_template))
        if router:
            if isinstance(router, str):
                router = import_attr(router)
            if not isinstance(router, Router):
                raise RouterAddError(
                    "`router` must be a Router object or a string to locate it: {}".format(uri_template)
                )
        if uri_template in self.__routes:
            self.__routes[uri_template].append({
                "router": router, "resource": resource, "suffix": suffix
            })
        else:
            self.__routes[uri_template] = [{
                "router": router, "resource": resource, "suffix": suffix
            }]

    def add_static_route(self, prefix, directory=None, router=None, downloadable=False, fallback_filename=None):
        if not directory and not router:
            raise RouterAddError(
                "`directory` and `router` must specify at least one: {}".format(prefix)
            )
        if directory and router:
            raise RouterAddError(
                "`directory` and `router` cannot be specified at the same time: {}".format(prefix)
            )
        if directory and not exists(directory):
            raise RouterAddError("`directory` is not exist: {}".format(prefix))
        if router:
            if isinstance(router, str):
                router = import_attr(router)
            if not isinstance(router, Router):
                raise RouterAddError(
                    "`router` must be a Router object or a string to locate it: {}".format(prefix)
                )
        if prefix in self.__static_routes:
            self.__static_routes[prefix].append({
                "router": router, "directory": directory,
                "downloadable": downloadable, "fallback_filename": fallback_filename
            })
        else:
            self.__static_routes[prefix] = [{
                "router": router, "directory": directory,
                "downloadable": downloadable, "fallback_filename": fallback_filename
            }]

    @lazy_property
    def routes(self):
        _routes = []
        for uri in self.__routes:
            route_params = self.__routes[uri]
            for route_param in route_params:
                if route_param["router"]:
                    _child_routes = route_param["router"].routes
                    for _child_route in _child_routes:
                        _routes.append({
                            "uri_template": uri + _child_route["uri_template"],
                            "resource": _child_route["resource"],
                            "suffix": _child_route["suffix"]
                        })
                else:
                    _routes.append({
                        "uri_template": uri, "resource": route_param["resource"],
                        "suffix": route_param["suffix"]
                    })
        return _routes

    @lazy_property
    def static_routes(self):
        _static_routes = []
        for uri in self.__static_routes:
            route_params = self.__static_routes[uri]
            for route_param in route_params:
                if route_param["router"]:
                    _child_static_routes = route_param["router"].static_routes
                    for _child_static_route in _child_static_routes:
                        _static_routes.append({
                            "uri_template": uri + _child_static_route["uri_template"],
                            "directory": _child_static_route["directory"],
                            "downloadable": _child_static_route["downloadable"],
                            "fallback_filename": _child_static_route["fallback_filename"]
                        })
                else:
                    _static_routes.append({
                        "uri_template": uri, "directory": route_param["directory"],
                        "downloadable": route_param["downloadable"],
                        "fallback_filename": route_param["fallback_filename"]
                    })
        return _static_routes


class UUIDStringConverter(BaseConverter):
    """Converts a field value to a UUID string.

    Identifier: `uuid_str`

    In order to be converted, the field value must consist of a
    string of 32 hexadecimal digits, as defined in RFC 4122, Section 3.
    Note, however, that hyphens and the URN prefix are optional.
    """

    __slots__ = ("_with_hyphen",)

    def __init__(self, with_hyphen=False):
        self._with_hyphen = with_hyphen

    def convert(self, value):
        try:
            uuid = UUID(value)
            return str(uuid) if self._with_hyphen else uuid.hex
        except ValueError:
            return None
