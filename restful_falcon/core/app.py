# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/12"
from __future__ import absolute_import

from logging import getLogger

from falcon.api import API

from restful_falcon.core.exception import DatabaseError
from restful_falcon.core.exception import db_error_handler
from restful_falcon.core.middleware.base import Middleware
from restful_falcon.core.middleware.default import AuthenticationMiddleware
from restful_falcon.core.middleware.default import PermissionMiddleware
from restful_falcon.core.request import Request
from restful_falcon.core.response import Response
from restful_falcon.util.module import import_attr
from restful_falcon.util.module import import_cls
from restful_falcon.util.module import import_obj
from restful_falcon.util.wrapper import lazy_property
from restful_falcon.util.wrapper import singleton

__all__ = ["Application"]

logger = getLogger(__name__)


@singleton(ignore_params=True)
class Application(object):
    def __init__(self, config):
        self.__config = config
        # 初始化API服务
        self.__init_falcon_api()

    @lazy_property
    def middleware(self):
        middleware = [AuthenticationMiddleware, PermissionMiddleware]
        if "middleware" in self.__config:
            if isinstance(middleware, list):
                middleware.extend(self.__config.middleware)
            else:
                middleware.append(self.__config.middleware)
        for i in range(0, len(middleware)):
            middleware[i] = import_obj(middleware[i], bases=(Middleware,))
        return middleware

    def __init_falcon_api(self):
        from falcon.media import JSONHandler
        from falcon.routing.converters import BaseConverter
        from restful_falcon.util.json import dumps
        from restful_falcon.util.json import loads
        from restful_falcon.core.router import UUIDStringConverter

        self.__api = API(
            request_type=Request, response_type=Response,
            middleware=self.middleware
        )
        extra_handlers = {
            "application/json": JSONHandler(dumps=dumps, loads=loads),
        }
        self.__api.req_options.media_handlers.update(extra_handlers)
        self.__api.resp_options.media_handlers.update(extra_handlers)
        self.__api.add_error_handler(DatabaseError, handler=db_error_handler)
        self.__api.router_options.converters["uuid_str"] = UUIDStringConverter
        if "router_options" in self.__config:
            for name, cls in self.__config.router_options.to_dict().items():
                self.__api.router_options.converters[name] = import_cls(cls, bases=(BaseConverter,))
        self.__init_routes()

    def __init_routes(self):
        from restful_falcon.core.router import Router

        if "router" in self.__config:
            router = self.__config.router
        elif "name" in self.__config:
            router = "{name}.router.router".format(name=self.__config.name)
        else:
            logger.warning("No route defined")
            return
        if not isinstance(router, Router):
            router = import_attr(router)
        routes = router.routes
        for route in routes:
            self.__api.add_route(**route)
        static_routes = router.static_routes
        for static_route in static_routes:
            self.__api.add_static_route(**static_route)

    def run(self, host=None, port=None):
        from wsgiref.simple_server import make_server

        host = host or self.__config.bind.host
        port = port or self.__config.bind.port
        httpd = make_server(host, port, self.__api)
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, InterruptedError):
            print("Application <{name}> is stopped, bye bye!".format(name=self.__config.get("name")))

    def __call__(self, env, start_response):
        return self.__api(env, start_response)
