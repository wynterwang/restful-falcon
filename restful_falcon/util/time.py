# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/11/25"
from __future__ import absolute_import

import datetime

from dateutil import tz
from functools import partial

from restful_falcon.core.config import CONF

__all__ = ["now"]


if getattr(CONF, "utc", False):
    now = datetime.datetime.utcnow
else:
    time_zone = None
    if hasattr(CONF, "time_zone"):
        time_zone = tz.gettz(CONF.time_zone)
    now = partial(datetime.datetime.now, tz=time_zone)
