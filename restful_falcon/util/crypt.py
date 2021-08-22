# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/9/18"
from __future__ import absolute_import

import crypt
import time

import hashlib

__all__ = ["make_password", "check_password", "token"]


def make_password(raw_password, salt=None):
    return crypt.crypt(raw_password, salt=salt)


def check_password(raw_password, password):
    words = password.split("$")
    if len(words) < 3:
        return False
    salt = "${}${}".format(words[1], words[2])
    return password == make_password(raw_password, salt=salt)


def token(*args):
    string = str(args) + str(time.time())
    md5 = hashlib.md5()
    md5.update(string.encode("utf-8"))
    return md5.hexdigest()
