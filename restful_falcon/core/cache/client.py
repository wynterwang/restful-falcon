# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

__all__ = ["CacheClient"]


class CacheClient(object):
    def __init__(self, backend):
        """
        CacheClient constructor
        :param backend: cache backend
        :type backend: restful_falcon.core.backend.base.BaseBackend
        """
        self.backend = backend

    def __getattr__(self, item):
        return getattr(self.backend, item)

    @classmethod
    def create(cls, config):
        backend_class = config["name"]
        backend_options = config.get("options", {})
        return cls(backend_class(**backend_options))

    def has(self, key):
        return self.backend.has(key)

    def get(self, key, default=None):
        return self.backend.get(key, default=default)

    def set(self, key, value, expire=None):
        return self.backend.set(key, value, expire=expire)

    def delete(self, key):
        return self.backend.delete(key)

    def clear(self):
        return self.backend.clear()
