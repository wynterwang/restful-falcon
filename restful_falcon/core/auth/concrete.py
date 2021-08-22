# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/20"
from __future__ import absolute_import

import base64

from restful_falcon.core.auth.base import Authentication
from restful_falcon.core.exception import AuthenticationError

__all__ = ["BasicAuthentication"]


class BasicAuthentication(Authentication):
    @staticmethod
    def __parse_auth(auth):
        _bytes = base64.b64decode(auth)
        _str = _bytes.decode(encoding="utf-8")
        return tuple(_str.split(":"))

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def has_username(self, username):
        return True

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def check_password(self, username, password):
        return True

    def authenticate(self, req):
        if req.auth and req.auth[:6] == "Basic ":
            username, password = self.__parse_auth(req.auth[6:])
            if not self.has_username(username):
                raise AuthenticationError(description="Invalid username")
            if not self.check_password(username, password):
                raise AuthenticationError(description="Invalid password")

    def match(self, req):
        return "AUTHORIZATION" in req.headers and req.auth.startswith("Basic ")
