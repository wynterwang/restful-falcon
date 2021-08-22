# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

__all__ = ["BaseBackend"]


class BaseBackend(object):
    def has(self, key):
        raise NotImplementedError()

    def get(self, key, default=None):
        raise NotImplementedError()

    def set(self, key, value, expire=None):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()
