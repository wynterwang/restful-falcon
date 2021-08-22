# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

import threading
import traceback
from logging import getLogger

from functools import wraps

__all__ = ["lazy_property", "singleton", "ignore_errors_except"]

logger = getLogger(__name__)


def lazy_property(func):
    attr_name = "_lazy_" + func.__name__

    @property
    @wraps(func)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    return _lazy_property


def singleton(ignore_params=False):
    def _singleton(cls):
        lock = threading.Lock()
        instances = {}

        @wraps(cls)
        def get_instance(*args, **kwargs):
            with lock:
                if ignore_params:
                    signature = cls.__name__
                else:
                    signature = str((cls.__name__, tuple(args), tuple(kwargs.items())))
                if signature not in instances:
                    instances[signature] = cls(*args, **kwargs)
            return instances[signature]
        return get_instance
    return _singleton


def ignore_errors_except(errors=(Exception,)):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                logger.warning(
                    "func ({}) raise exception: {}".format(func.__name__, str(e))
                )
                logger.warning(traceback.format_exc())
        return _wrapper
    return wrapper
