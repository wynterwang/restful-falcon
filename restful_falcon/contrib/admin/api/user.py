# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/18"
from __future__ import absolute_import

from datetime import datetime
from datetime import timedelta

from restful_falcon.contrib.admin.api.schema.user import auth_user_schema
from restful_falcon.contrib.admin.api.schema.user import login_schema
from restful_falcon.contrib.admin.auth import BasicAuthentication
from restful_falcon.contrib.admin.auth import TokenAuthentication
from restful_falcon.contrib.admin.db.model.group import AuthGroup
from restful_falcon.contrib.admin.db.model.user import AuditActions
from restful_falcon.contrib.admin.db.model.user import AuthAudit
from restful_falcon.contrib.admin.db.model.user import AuthToken
from restful_falcon.contrib.admin.db.model.user import AuthUser
from restful_falcon.core.cache import CACHE
from restful_falcon.core.controller.base import Resource
from restful_falcon.core.controller.mixin import CreateOperateMixin
from restful_falcon.core.controller.mixin import ResourceOperatesMixin
from restful_falcon.core.exception import AuthenticationError
from restful_falcon.core.exception import ResourceValidateError
from restful_falcon.core.permission.concrete import AllowAny
from restful_falcon.core.permission.concrete import IsAdminUser
from restful_falcon.util.crypt import check_password
from restful_falcon.util.crypt import make_password
from restful_falcon.util.crypt import token

TOKEN_DURATION = 7200


class AuthUserResource(Resource, ResourceOperatesMixin):
    resource_model = AuthUser
    validator_schema = auth_user_schema
    authentication_classes = (TokenAuthentication, BasicAuthentication)
    permission_classes = (IsAdminUser,)

    @staticmethod
    def validate_group_id(group_id):
        if not AuthGroup.exist(filters=[("id", group_id)]):
            raise ResourceValidateError(
                description="User group does not exist: `group_id`({})".format(group_id)
            )

    def create(self, context, data):
        if "group_id" in data:
            self.validate_group_id(data["group_id"])
        data["password"] = make_password(data["password"])
        return super(AuthUserResource, self).create(context, data)

    def update(self, context, resource_id, data, filters=None):
        if "group_id" in data:
            self.validate_group_id(data["group_id"])
        return super(AuthUserResource, self).update(context, resource_id, data, filters=filters)


class AuthUserLogin(Resource, CreateOperateMixin):
    auto_fill_fields = False
    resource_model = AuthUser
    validator_schema = login_schema
    permission_classes = (AllowAny,)

    def create(self, context, data):
        user = self.resource_model.perform_show_by(filters=[("username", data["username"])])
        if not user or not check_password(data["password"], user["password"]):
            raise AuthenticationError(
                description="Invalid password" if user else "Invalid username"
            )
        current_time = datetime.now()
        auth_token = AuthToken.perform_create({
            "user_id": user["id"],
            "token": token(user["username"], user["company"], user["department"]),
            "expired_at": current_time + timedelta(seconds=TOKEN_DURATION)
        }, session=context.session)
        AuthAudit.perform_create({
            "user_id": user["id"], "username": user["username"], "action": AuditActions.login.name
        }, session=context.session)
        return auth_token


class AuthUserLogout(Resource, CreateOperateMixin):
    auto_fill_fields = False
    resource_model = AuthUser
    authentication_classes = (TokenAuthentication,)

    def create(self, context, data):
        user_info = context.request.user.user_info
        if CACHE:
            CACHE.delete(user_info["token"])
        AuthAudit.perform_create({
            "user_id": user_info["id"], "username": user_info["username"],
            "action": AuditActions.logout.name
        }, session=context.session)
        AuthToken.perform_delete_by(
            filters=[("token", user_info["token"])],
            session=context.session
        )
        return {
            "title": "User logout",
            "description": "User '{}' logout successful".format(user_info["username"])
        }
