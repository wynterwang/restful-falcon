# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/24"
from __future__ import absolute_import

__all__ = ["ResourceIsolation", "ResourceIsolationByUser"]


class ResourceIsolation:
    def isolation_filters(self, request):
        """

        :param request: request object
        :type request: restful_falcon.core.request.Request
        :return: filter list
        :rtype: list
        """
        raise NotImplementedError()


class ResourceIsolationByUser(ResourceIsolation):
    def isolation_filters(self, request):
        if not request.user.is_admin:
            return [("created_by", request.user.user_id)]
