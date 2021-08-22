# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/26"
from __future__ import absolute_import

from falcon.request import Request as _Request

__all__ = ["Request"]


class Request(_Request):
    def __init__(self, *args, **kwargs):
        self.__user = None
        super(Request, self).__init__(*args, **kwargs)

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user):
        if not self.__user:
            self.__user = user
        else:
            raise AttributeError("`Request.user` only can set once")
