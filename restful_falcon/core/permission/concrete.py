# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/29"
from __future__ import absolute_import

from restful_falcon.core.permission.base import Permission

__all__ = ["AllowAny", "IsAuthenticated", "IsAdminUser", "IsAuthenticatedOrReadOnly"]


class AllowAny(Permission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, req):
        return True


class IsAuthenticated(Permission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, req):
        return req.user and req.user.is_authenticated


class IsAdminUser(Permission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, req):
        return req.user and req.user.is_admin


class IsAuthenticatedOrReadOnly(Permission):
    """
    The request is authenticated as a user, or is a read-only request.
    """
    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, req):
        return (
            req.method in self.SAFE_METHODS or
            req.user and
            req.user.is_authenticated
        )
