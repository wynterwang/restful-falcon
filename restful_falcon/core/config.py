# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/4"
from __future__ import absolute_import

import json
from collections import Mapping

import re

from restful_falcon.core.constants import Missing
from restful_falcon.util.file import is_dir
from restful_falcon.util.file import is_file
from restful_falcon.util.file import list_files
from restful_falcon.util.module import import_attr

__all__ = ["Configuration", "CONF", "init_config"]

IMPORT_STR_PATTERN = re.compile("^__import__\(([\w.]+)\)$")


def _format(value):
    if isinstance(value, str):
        match = IMPORT_STR_PATTERN.match(value)
        if match:
            return import_attr(match.group(1))
    return value


class _Configuration(Mapping):
    def __init__(self, opts, base=""):
        self.__opts = opts or {}
        self.__base = base

    def __getattr__(self, name):
        try:
            value = self.__opts[name]
            if isinstance(value, dict):
                base = "{}.{}".format(self.__base, name).strip(".")
                return _Configuration(value, base=base)
            return value
        except KeyError:
            name = "{}.{}".format(self.__base, name).strip(".")
            raise AttributeError("No attribute `{}`".format(name))

    def __getitem__(self, key):
        return self.__opts[key]

    def __contains__(self, key):
        return key in self.__opts

    def __iter__(self):
        for key in self.__opts.keys():
            yield key

    def __len__(self):
        return len(self.__opts)

    def get(self, key, default=None):
        if key in self:
            return self.__opts[key]
        return default

    def update(self, dict_obj):
        self.__opts.update(dict_obj)

    def iterkeys(self):
        return iter(self.__opts)

    def itervalues(self):
        for key in self.__opts:
            yield self.__opts[key]

    def iteritems(self):
        for key in self.__opts:
            yield (key, self.__opts[key])

    def keys(self):
        return list(self.__opts)

    def items(self):
        return [(key, self.__opts[key]) for key in self.__opts]

    def values(self):
        return [self.__opts[key] for key in self.__opts]

    def check(self):
        def _check(name, value):
            if isinstance(value, Missing):
                name = name.strip(".")
                raise AttributeError("Attribute `{}` must set".format(name))
            if isinstance(value, dict):
                for key, val in value.items():
                    _check("{}.{}".format(name, key), val)
        _check("", self.__opts)

    def to_dict(self):
        config = {}
        for key in self:
            value = getattr(self, key)
            if isinstance(value, _Configuration):
                config[key] = value.to_dict()
            else:
                config[key] = _format(value)
        return config


class Configuration(object):
    def __init__(self, opts=None, conf_file=None, conf_dir=None, **kwargs):
        self._config = _Configuration(opts)

        opts = opts or {}
        opts.update(kwargs)
        self.update_from(opts=opts, conf_file=conf_file, conf_dir=conf_dir)

    def __repr__(self):
        return repr(self._config)

    def __str__(self):
        return str(self._config)

    def __getattr__(self, attr):
        return getattr(self._config, attr)

    def __getitem__(self, item):
        return self._config[item]

    def __contains__(self, item):
        return item in self._config

    def _update_from(self, file_name):
        with open(file_name) as f:
            dict_obj = json.load(f)
        self._config.update(dict_obj)

    def update_from(self, opts=None, conf_file=None, conf_dir=None):
        if opts:
            self._config.update(opts)
        if conf_file and is_file(conf_file):
            self._update_from(conf_file)
        if conf_dir and is_dir(conf_dir):
            for file in list_files(conf_dir, recursive=True, only_file=True):
                self._update_from(file)
        self._config.check()


CONF = Configuration()


def init_config(conf_file, conf_dir, **opts):
    import copy
    from logging.config import dictConfig
    from restful_falcon.core.constants import DEFAULT_OPTS

    _opts = copy.deepcopy(DEFAULT_OPTS)
    if opts:
        _opts.update(opts)
    global CONF
    CONF.update_from(_opts, conf_file=conf_file, conf_dir=conf_dir)

    if hasattr(CONF, "logger"):
        dictConfig(CONF.logger.to_dict())
    return CONF
