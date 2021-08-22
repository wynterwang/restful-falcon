# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/18"
from __future__ import absolute_import

from datetime import datetime

from restful_falcon.contrib.admin.db.model.user import AuthToken
from restful_falcon.contrib.admin.db.model.user import AuthUser as AuthUserModel
from restful_falcon.core.auth.base import Authentication
from restful_falcon.core.auth.base import User
from restful_falcon.core.auth.concrete import BasicAuthentication as _BasicAuthentication
from restful_falcon.core.cache import CACHE
from restful_falcon.core.exception import AuthenticationError
from restful_falcon.util.crypt import check_password
from restful_falcon.util.json import loads

__all__ = ["AuthUser", "BasicAuthentication", "TokenAuthentication"]


class AuthUser(User):
    def __init__(self, auth_user):
        self.__auth_user = auth_user

    def __getattr__(self, item):
        return self.__auth_user.get(item, None)

    @property
    def user_info(self):
        return self.__auth_user

    @property
    def username(self):
        return self.__auth_user["username"]

    @property
    def user_id(self):
        return self.__auth_user["id"]

    @property
    def group(self):
        return self.__auth_user["group_id"]

    @property
    def is_admin(self):
        return self.__auth_user["admin"]


class BasicAuthentication(_BasicAuthentication):
    def has_username(self, username):
        user = AuthUserModel.perform_show_by(filters=[("username", username)])
        if user:
            setattr(self, "user", user)
            return True
        return False

    def check_password(self, username, password):
        # noinspection PyUnresolvedReferences
        return check_password(password, self.user["password"])

    def authenticate(self, req):
        super(BasicAuthentication, self).authenticate(req)
        # noinspection PyUnresolvedReferences
        return AuthUser(self.user)


class TokenAuthentication(Authentication):
    token_field = "X-AUTH-TOKEN"

    @staticmethod
    def _token_cache_interval(auth_token):
        remain = (auth_token["expired_at"] - datetime.now()).seconds
        return min(1800, remain)

    @staticmethod
    def _token_expired(auth_token):
        return datetime.now() > auth_token["expired_at"]

    def _user_from_token(self, auth_token):
        if auth_token and not self._token_expired(auth_token):
            user = AuthUserModel.perform_show(auth_token["user_id"])
            user["token"] = auth_token["token"]
            return user
        if auth_token:
            AuthToken.perform_delete(auth_token["id"])
        raise AuthenticationError(description="Invalid user token")

    def authenticate(self, req):
        user_token = req.get_header(self.token_field)
        if CACHE:
            if CACHE.has(user_token):
                user = CACHE.get(user_token)
                if isinstance(user, str):
                    user = loads(user)
            else:
                auth_token = AuthToken.perform_show_by(filters=[("token", user_token)])
                user = self._user_from_token(auth_token)
                CACHE.set(user_token, user, expire=self._token_cache_interval(auth_token))
        else:
            auth_token = AuthToken.perform_show_by(filters=[("token", user_token)])
            user = self._user_from_token(auth_token)
        return AuthUser(user)

    # noinspection PyMethodMayBeStatic
    # noinspection PyUnusedLocal
    def match(self, req):
        return self.token_field in req.headers
