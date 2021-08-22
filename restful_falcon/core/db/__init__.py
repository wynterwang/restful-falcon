# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/17"
from __future__ import absolute_import

from sqlalchemy.engine.base import Engine
from restful_falcon.core.config import CONF
from restful_falcon.core.db.engine import create_engine
from restful_falcon.core.db.engine import Session


ENGINE: Engine = (
    create_engine(CONF.db.to_dict()) if "db" in CONF else None
)
