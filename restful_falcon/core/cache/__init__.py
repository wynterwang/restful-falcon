# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

from restful_falcon.core.cache.client import CacheClient
from restful_falcon.core.config import CONF

__all__ = ["CACHE", "CacheClient"]

CACHE: CacheClient = (
    CacheClient.create(CONF.cache.to_dict()) if "cache" in CONF else None
)
