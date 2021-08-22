# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/4"
from __future__ import absolute_import

from restful_falcon.util.version import get_version

VERSION = (0, 0, 13, "alpha", 0)

__version__ = get_version(VERSION)


def setup():
    import os
    from restful_falcon.util.module import import_module
    from restful_falcon.apps.registry import apps

    config_module = os.environ.get("RESTFUL_FALCON_CONFIG")
    if not config_module:
        raise EnvironmentError("Missing environment variable `RESTFUL_FALCON_CONFIG`")
    try:
        config_module = import_module(config_module)
    except Exception as e:
        raise RuntimeError(
            "Import project configuration error: {}".format(str(e))
        )
    config = config_module.CONF
    apps.populate(config.workspace, config.get("installed_apps", []))
