# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/18"
from __future__ import absolute_import

from restful_falcon.contrib.admin.db.model.group import AuthGroup
from restful_falcon.core.controller.base import Resource
from restful_falcon.core.controller.mixin import ResourceOperatesMixin
from restful_falcon.core.permission.concrete import IsAdminUser


class AuthGroupResource(Resource, ResourceOperatesMixin):
    resource_model = AuthGroup
    permission_classes = (IsAdminUser,)
