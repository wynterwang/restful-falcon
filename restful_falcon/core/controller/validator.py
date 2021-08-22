# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/14"
from __future__ import absolute_import

import falcon
import jsonschema
from functools import partial
from functools import wraps

__all__ = ["validate", "validate_request", "validate_response", "ResourceSchema"]


def validate_request(req, req_field="media", req_schema=None):
    if req_schema is not None:
        try:
            jsonschema.validate(
                getattr(req, req_field), req_schema,
                format_checker=jsonschema.FormatChecker()
            )
        except jsonschema.ValidationError as e:
            if not e.absolute_path:
                error_message = e.message
            else:
                error_message = "{}: {}".format(".".join(e.absolute_path), e.message)
            raise falcon.HTTPBadRequest(
                "Request data failed validation",
                description=error_message
            )


def validate_response(resp, resp_schema=None):
    if resp_schema is not None:
        try:
            jsonschema.validate(
                resp.media, resp_schema,
                format_checker=jsonschema.FormatChecker()
            )
        except jsonschema.ValidationError:
            raise falcon.HTTPInternalServerError(
                "Response data failed validation"
                # Do not return 'e.message' in the response to
                # prevent info about possible internal response
                # formatting bugs from leaking out to users.
            )


def validate(req_schema=None, req_field="media", resp_schema=None):
    """Decorator for validating ``req.media`` using JSON Schema.

    This decorator provides standard JSON Schema validation via the
    ``jsonschema`` package available from PyPI. Semantic validation via
    the *format* keyword is enabled for the default checkers implemented
    by ``jsonschema.FormatChecker``.

    Note:
        The `jsonschema`` package must be installed separately in order to use
        this decorator, as Falcon does not install it by default.

        See `json-schema.org <http://json-schema.org/>`_ for more
        information on defining a compatible dictionary.

    Args:
        req_schema (dict, optional): A dictionary that follows the JSON
            Schema specification. The request will be validated against this
            schema.
        req_field (str, optional): A field of request to validate. The default
            field is media.
        resp_schema (dict, optional): A dictionary that follows the JSON
            Schema specification. The response will be validated against this
            schema.

    Example:
        .. code:: python

            from falcon.media.validators import jsonschema

            # -- snip --

            @jsonschema.validate(my_post_schema)
            def on_post(self, req, resp):

            # -- snip --

    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, req, resp, *args, **kwargs):
            validate_request(req, req_schema=req_schema, req_field=req_field)
            result = func(self, req, resp, *args, **kwargs)
            validate_response(resp, resp_schema=resp_schema)
            return result
        return wrapper
    return decorator


class ResourceSchema(object):
    default_validate_field = "media"
    list_validate_field = "params"
    create_validate_field = "media"
    update_validate_field = "media"

    # noinspection PyShadowingBuiltins
    def __init__(self, default=None, list=None, create=None, update=None):
        self._default = default
        self._list = list
        self._create = create
        self._update = update

    def __validator(self, name):
        req_schema = getattr(self, name)
        if not req_schema and not self._default:
            return
        if req_schema:
            req_field = getattr(self, "{}_validate_field".format(name.strip("_")))
            return partial(validate_request, req_field=req_field, req_schema=req_schema)
        return partial(validate_request, req_field=self.default_validate_field, req_schema=self._default)

    def list_validator(self):
        return self.__validator("_list")

    def create_validator(self):
        return self.__validator("_create")

    def update_validator(self):
        return self.__validator("_update")
