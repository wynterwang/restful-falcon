# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

import redis

from restful_falcon.core.cache.backend.base import BaseBackend

__all__ = ["RedisBackend"]

DEFAULT_CONN_POOL = "ConnectionPool"


def pool_class(conn_pool):
    cls = getattr(redis, conn_pool)
    if not cls:
        raise TypeError("Unknown Connection Pool: {}".format(conn_pool))
    return cls


class RedisBackend(BaseBackend):
    def __init__(self, url, db=None, decode_components=False, conn_pool=DEFAULT_CONN_POOL, **kwargs):
        connection_pool = pool_class(conn_pool).from_url(
            url, db=db, decode_components=decode_components, **kwargs
        )
        self.client = redis.Redis(connection_pool=connection_pool)

    def __del__(self):
        del self.client

    def __getattr__(self, item):
        return getattr(self.client, item)

    def has(self, key):
        return key in self.client

    def get(self, key, default=None):
        value = self.client.get(key)
        return value if value else default

    def set(self, key, value, expire=None, **kwargs):
        return self.client.set(key, value, ex=expire, **kwargs)

    def delete(self, key):
        return self.client.delete(key)

    def clear(self):
        return self.client.flushdb()
