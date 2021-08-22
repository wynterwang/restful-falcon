# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/12"
from __future__ import absolute_import

# noinspection PyUnresolvedReferences
from falcon.errors import HTTPBadGateway
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPBadRequest
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPConflict
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPFailedDependency
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPForbidden
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPGatewayTimeout
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPGone
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPInsufficientStorage
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPInternalServerError
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPInvalidHeader
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPInvalidParam
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPLengthRequired
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPLocked
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPLoopDetected
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPMethodNotAllowed
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPMissingHeader
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPMissingParam
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPNetworkAuthenticationRequired
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPNotAcceptable
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPNotFound
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPNotImplemented
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPPayloadTooLarge
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPPreconditionFailed
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPPreconditionRequired
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPRangeNotSatisfiable
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPRequestHeaderFieldsTooLarge
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPServiceUnavailable
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPTooManyRequests
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPUnauthorized
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPUnavailableForLegalReasons
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPUnprocessableEntity
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPUnsupportedMediaType
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPUriTooLong
# noinspection PyUnresolvedReferences
from falcon.errors import HTTPVersionNotSupported
# noinspection PyUnresolvedReferences
from falcon.http_error import HTTPError
# noinspection PyUnresolvedReferences
from sqlalchemy.exc import DatabaseError

from restful_falcon.util.string import to_words

__all__ = [
    "HTTPError", "HTTPBadGateway", "HTTPBadRequest", "HTTPConflict", "HTTPFailedDependency", "HTTPForbidden",
    "HTTPGatewayTimeout", "HTTPGone", "HTTPInsufficientStorage", "HTTPInternalServerError", "HTTPInvalidHeader",
    "HTTPInvalidParam", "HTTPLengthRequired", "HTTPLocked", "HTTPLoopDetected", "HTTPMethodNotAllowed",
    "HTTPMissingHeader", "HTTPMissingParam", "HTTPNetworkAuthenticationRequired", "HTTPNotAcceptable",
    "HTTPNotFound", "HTTPNotImplemented", "HTTPPayloadTooLarge", "HTTPPreconditionFailed", "HTTPPreconditionRequired",
    "HTTPRangeNotSatisfiable", "HTTPRequestHeaderFieldsTooLarge", "HTTPServiceUnavailable", "HTTPTooManyRequests",
    "HTTPUnauthorized", "HTTPUnavailableForLegalReasons", "HTTPUnprocessableEntity", "HTTPUnsupportedMediaType",
    "HTTPUriTooLong", "HTTPVersionNotSupported", "AuthenticationError", "PermissionError", "ResourceValidateError",
    "DatabaseError", "db_error_handler"
]


class AuthenticationError(HTTPUnauthorized):
    def __init__(self, description=None, challenges=None, headers=None, **kwargs):
        super(AuthenticationError, self).__init__(
            title="Authentication error",
            description=description, challenges=challenges, headers=headers, **kwargs
        )


# noinspection PyShadowingBuiltins
class PermissionError(HTTPForbidden):
    def __init__(self, description=None, headers=None, **kwargs):
        super(PermissionError, self).__init__(
            title="Permission error",
            description=description, headers=headers, **kwargs
        )


class ResourceValidateError(HTTPBadRequest):
    def __init__(self, description=None, headers=None, **kwargs):
        super(ResourceValidateError, self).__init__(
            title="Resource validate error",
            description=description, headers=headers, **kwargs
        )


# noinspection PyUnusedLocal
def db_error_handler(req, resp, ex, params):
    ex_name = " ".join(to_words(ex.__class__.__name__))
    ex_msg = getattr(ex, "_message")()
    raise HTTPBadRequest(
        title="Database {}".format(ex_name).capitalize(), description=ex_msg
    )
