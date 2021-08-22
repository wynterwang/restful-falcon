# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/23"
from __future__ import absolute_import

from restful_falcon.core.db.mixin import IdAndTimeColumnsMixin
from restful_falcon.core.db.model import Column
from restful_falcon.core.db.model import Model
from restful_falcon.core.db.type import String


class AuthGroup(Model, IdAndTimeColumnsMixin):
    name = Column(String(63), unique=True, index=True, nullable=False)
