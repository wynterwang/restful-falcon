# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

import uuid

import cacheout

from restful_falcon.core.cache.backend.base import BaseBackend

__all__ = ["MemoryBackend"]

DEFAULT_CACHE_TYPE = "Cache"


def cache_class(cache_type):
    cls = getattr(cacheout, cache_type)
    if not cls:
        raise TypeError("Unknown Cache Type: {}".format(cache_type))
    return cls


class MemoryBackend(BaseBackend):
    def __init__(self, maxsize=None, ttl=None, default=None, cache_type=DEFAULT_CACHE_TYPE):
        self.name = str(uuid.uuid1())
        self.manager = cacheout.CacheManager({
            self.name: {
                "maxsize": maxsize, "ttl": ttl, "default": default
            }
        }, cache_class(cache_type))

    def __getattr__(self, item):
        return getattr(self.manager[self.name], item)

    def has(self, key):
        return self.manager[self.name].has(key)

    def get(self, key, default=None):
        return self.manager[self.name].get(key, default=default)

    def set(self, key, value, expire=None):
        return self.manager[self.name].set(key, value, ttl=expire)

    def delete(self, key):
        return self.manager[self.name].delete(key)

    def clear(self):
        return self.manager[self.name].clear()
