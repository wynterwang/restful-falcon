# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/17"
from __future__ import absolute_import

import enum

from restful_falcon.core.db.mixin import IdAndTimeColumnsMixin
from restful_falcon.core.db.mixin import UserColumnsMixin
from restful_falcon.core.db.model import Column
from restful_falcon.core.db.model import Model
from restful_falcon.core.db.type import Boolean
from restful_falcon.core.db.type import DateTime
from restful_falcon.core.db.type import Enum
from restful_falcon.core.db.type import Integer
from restful_falcon.core.db.type import String


class AuthUser(Model, IdAndTimeColumnsMixin, UserColumnsMixin):
    username = Column(String(63), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)
    first_name = Column(String(31), nullable=True)
    last_name = Column(String(15), nullable=True)
    company = Column(String(63), nullable=True)
    department = Column(String(63), nullable=True)
    telephone = Column(String(31), nullable=True)
    email = Column(String(63), nullable=True)
    address = Column(String(127), nullable=True)
    group_id = Column(Integer, nullable=True, index=True)
    admin = Column(Boolean, default=False)
    system = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)


class AuditActions(enum.Enum):
    login = "login"
    logout = "logout"


class AuthAudit(Model, IdAndTimeColumnsMixin):
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(63), nullable=False)
    action = Column(Enum(AuditActions), nullable=False)


class AuthToken(Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(63), nullable=False, index=True)
    expired_at = Column(DateTime, nullable=False)
