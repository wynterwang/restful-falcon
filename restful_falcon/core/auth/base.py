# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/20"
from __future__ import absolute_import

__all__ = ["User", "Authentication"]


class User(object):
    @property
    def user_info(self):
        return None

    @property
    def username(self):
        return None

    @property
    def user_id(self):
        return None

    @property
    def group(self):
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_admin(self):
        return False


class Authentication(object):
    def authenticate(self, req):
        """
        Authenticate operate. It should return the corresponding user's info
        if authenticate success.

        :param req: request object
        :type req: restful_falcon.core.request.Request
        :return: user if authenticate success, otherwise None
        """
        raise NotImplementedError()

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def match(self, req):
        """
        Check request header whether match the current authentication.

        :param req: request object
        :type req: restful_falcon.core.request.Request
        :return: True if header match the current authentication,
                otherwise False.
        :rtype: bool
        """
        return True
