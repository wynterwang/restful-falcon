# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/21"
from __future__ import absolute_import

import copy


def extend(dict1, dict2):
    dict3: dict = copy.deepcopy(dict1)
    dict3.update(dict2)
    return dict3


PASSWORD_PATTERN = "^(?=.*?[A-Z])(?=(.*[a-z]){1,})(?=(.*[\d]){1,})(?=(.*[\W]){1,})(?!.*\s).{8,}$"


login_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Login validator schema",
    "description": "Validator for login data",
    "type": "object",
    "properties": {
        "username": {
            "description": "The username of user",
            "type": "string",
            "pattern": "^\w+$",
            "minLength": 1,
            "maxLength": 63
        },
        "password": {
            "description": "The password of user",
            "type": "string",
            "pattern": PASSWORD_PATTERN,
            "minLength": 1,
            "maxLength": 63
        },

    },
    "additionalProperties": False,
    "minProperties": 2,
    "maxProperties": 2,
    "required": ["username", "password"]
}

_auth_user_common_properties = {
    "first_name": {
        "description": "The first name of user",
        "type": "string",
        "minLength": 1,
        "maxLength": 31
    },
    "last_name": {
        "description": "The last name of user",
        "type": "string",
        "minLength": 1,
        "maxLength": 15
    },
    "company": {
        "description": "The company of user",
        "type": "string",
        "minLength": 1,
        "maxLength": 63
    },
    "telephone": {
        "description": "The telephone of user",
        "type": "string",
        "pattern": "^[1]([3-9])[0-9]{9}$",
        "minLength": 1,
        "maxLength": 31
    },
    "email": {
        "description": "The email of user",
        "type": "string",
        "pattern": "^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$",
        "minLength": 1,
        "maxLength": 63
    },
    "address": {
        "description": "The address of user",
        "type": "string",
        "minLength": 1,
        "maxLength": 127
    },
    "group_id": {
        "description": "The group id of user",
        "type": "integer",
        "minimum": 1
    },
    "admin": {
        "description": "Whether the user is admin",
        "type": "boolean"
    },
    "system": {
        "description": "Whether the user is system account",
        "type": "boolean"
    },
    "enabled": {
        "description": "Whether the user is enabled",
        "type": "boolean"
    }
}


auth_user_schema = {
    "create": {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "User create validator schema",
        "description": "Validator for user create data",
        "type": "object",
        "properties": extend(_auth_user_common_properties, {
            "username": {
                "description": "The username of user",
                "type": "string",
                "pattern": "^\w+$",
                "minLength": 1,
                "maxLength": 63
            },
            "password": {
                "description": "The password of user",
                "type": "string",
                "pattern": PASSWORD_PATTERN,
                "minLength": 1,
                "maxLength": 63
            }
        }),
        "required": ["username", "password"],
        "additionalProperties": False
    },
    "update": {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "User update validator schema",
        "description": "Validator for user update data",
        "type": "object",
        "properties": _auth_user_common_properties,
        "minProperties": 1,
        "additionalProperties": False
    }
}
