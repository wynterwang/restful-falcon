# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/27"
from __future__ import absolute_import

import json
from datetime import date
from datetime import datetime
from uuid import UUID

import enum
from functools import wraps

__all__ = ["dumps", "loads"]


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.name
        return super(JSONEncoder, self).default(obj)


@wraps(json.dumps)
def dumps(*args, **kwargs):
    return json.dumps(*args, cls=JSONEncoder, **kwargs)


@wraps(json.loads)
def loads(*args, **kwargs):
    return json.loads(*args, **kwargs)
