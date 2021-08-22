## application.py
# -*- coding: utf-8 -*-
from .configuration import CONF

from restful_falcon.core.app import Application


application = Application(CONF)
