# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/10"
from __future__ import absolute_import

import importlib

__all__ = ["import_module", "import_attr", "import_cls", "import_obj"]


def import_module(name):
    if not isinstance(name, str):
        raise ImportError(
            "`name` should be an string object: {}".format(name.__class__.__name__)
        )
    return importlib.import_module(name)


def import_attr(name):
    if not isinstance(name, str):
        raise ImportError(
            "`name` should be an string object: {}".format(name.__class__.__name__)
        )
    pkg, _, attr = name.rpartition(".")
    pkg = importlib.import_module(pkg)
    return getattr(pkg, attr)


def _format_cls_names(bases):
    if not isinstance(bases, (tuple, list)):
        bases = (bases,)
    return str([base.__name__ for base in bases])


def import_cls(name, bases=None):
    if isinstance(name, type) and (not bases or issubclass(name, bases)):
        return name
    cls = import_attr(name)
    if not bases or issubclass(cls, bases):
        return cls
    raise ImportError(
        "{} is not subclass of {}".format(cls.__name__, _format_cls_names(bases))
    )


def import_obj(name, *args, bases=None, **kwargs):
    if isinstance(name, bases):
        return name
    cls = import_cls(name, bases=bases)
    return cls(*args, **kwargs)
