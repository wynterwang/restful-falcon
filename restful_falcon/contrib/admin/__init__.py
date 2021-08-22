# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/17"
from __future__ import absolute_import

from restful_falcon.contrib.admin.api.group import AuthGroupResource
from restful_falcon.contrib.admin.api.user import AuthUserLogin
from restful_falcon.contrib.admin.api.user import AuthUserLogout
from restful_falcon.contrib.admin.api.user import AuthUserResource
from restful_falcon.contrib.admin.auth import BasicAuthentication
from restful_falcon.contrib.admin.auth import TokenAuthentication
from restful_falcon.contrib.admin.db.model.group import AuthGroup
from restful_falcon.contrib.admin.db.model.user import AuthToken
from restful_falcon.contrib.admin.db.model.user import AuthUser

__all__ = [
    "AuthGroupResource", "AuthUserLogin", "AuthUserLogout", "AuthUserResource", "BasicAuthentication",
    "TokenAuthentication", "AuthGroup", "AuthToken", "AuthUser"
]

default_app_config = "restful_falcon.contrib.admin.apps.AdminConfig"
