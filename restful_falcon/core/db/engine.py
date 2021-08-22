# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/17"
from __future__ import absolute_import

from sqlalchemy import create_engine as _create_engine
from sqlalchemy.orm import sessionmaker

__all__ = ["create_engine", "Session"]

Session = sessionmaker()


def create_engine(config):
    engine = _create_engine(config["url"], **config.get("options", {}))
    Session.configure(bind=engine, autoflush=True, autocommit=False)
    return engine
