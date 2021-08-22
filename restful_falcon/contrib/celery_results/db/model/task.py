# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/18"
from __future__ import absolute_import

from datetime import datetime

from celery import states

from restful_falcon.core.db.model import Column
from restful_falcon.core.db.model import Model
from restful_falcon.core.db.model import Sequence
from restful_falcon.core.db.type import DateTime
from restful_falcon.core.db.type import Integer
from restful_falcon.core.db.type import LargeBinary
from restful_falcon.core.db.type import PickleType
from restful_falcon.core.db.type import String
from restful_falcon.core.db.type import Text


class Task(Model):
    """
    Task result/status.
    """

    __tablename__ = "celery_taskmeta"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, Sequence("task_id_sequence"), primary_key=True, autoincrement=True)
    task_id = Column(String(155), unique=True)
    status = Column(String(50), default=states.PENDING)
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    traceback = Column(Text, nullable=True)


class TaskExtended(Task):
    """
    For the extend result.
    """

    __tablename__ = "celery_taskmeta"
    __table_args__ = {"sqlite_autoincrement": True, "extend_existing": True}

    name = Column(String(155), nullable=True)
    args = Column(LargeBinary, nullable=True)
    kwargs = Column(LargeBinary, nullable=True)
    worker = Column(String(155), nullable=True)
    retries = Column(Integer, nullable=True)
    queue = Column(String(155), nullable=True)


class TaskSet(Model):
    """
    TaskSet result.
    """

    __tablename__ = "celery_tasksetmeta"
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(Integer, Sequence("taskset_id_sequence"), autoincrement=True, primary_key=True)
    taskset_id = Column(String(155), unique=True)
    result = Column(PickleType, nullable=True)
    date_done = Column(DateTime, default=datetime.utcnow, nullable=True)
