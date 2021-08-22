# -*- coding: utf-8 -*-
# __author__ = "wynter"
# __date__ = "2020/8/15"
from __future__ import absolute_import


BANNER = """
-----------------------------------------------------------------------
  ____  _____ ____ _____ __       _       _____     _                 
 |  _ \| ____/ ___|_   _/ _|_   _| |     |  ___|_ _| | ___ ___  _ __  
 | |_) |  _| \___ \ | || |_| | | | |_____| |_ / _` | |/ __/ _ \| '_ \ 
 |  _ <| |___ ___) || ||  _| |_| | |_____|  _| (_| | | (_| (_) | | | |
 |_| \_\_____|____/ |_||_|  \__,_|_|     |_|  \__,_|_|\___\___/|_| |_|

-----------------------------------------------------------------------
"""


class Missing(str):
    pass


unset = Missing("<unset>")


DEFAULT_LOGGER_FORMATTER = "default"
DEFAULT_LOGGER_HANDLER = "console"

DEFAULT_OPTS = {
    "name": unset,
    "bind": {
        "host": unset,
        "port": unset
    },
    "logger": {
        "version": 1,
        "formatters": {
            DEFAULT_LOGGER_FORMATTER: {
                "format": "[%(asctime)s] [%(pathname)s-%(lineno)d] [%(levelname)s]: %(message)s"
            }
        },
        "handlers": {
            DEFAULT_LOGGER_HANDLER: {
                "level": "INFO",
                "formatter": DEFAULT_LOGGER_FORMATTER,
                "class": "logging.StreamHandler",
                "stream": "__import__(sys.stdout)"
            }
        },
        "loggers": {
        },
        "root": {
            "handlers": [DEFAULT_LOGGER_HANDLER],
            "propagate": False
        }
    },
    "db": {
        "url": "sqlite:///:memory:",
        "options": {
            "echo": True
        }
    },
    "middleware": [],
    "authentication": [],
    "permission": [],
    "installed_apps": []
}
