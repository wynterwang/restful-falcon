# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/18"
from __future__ import absolute_import

import uuid

__all__ = ["to_words", "to_snake_case", "uuid_str"]


def to_words(string):
    words = []
    i, j, mode = 0, 0, 1
    for char in string:
        if mode == 0:
            if "A" <= char <= "Z":
                words.append(string[i:j])
                i, mode = j, 1
        elif char < "A" or char > "Z":
            mode = 0
        j += 1
    if i != j:
        words.append(string[i:j])
    else:
        words.append(string)
    return words


def to_snake_case(string):
    words = to_words(string)
    return "_".join(words).lower()


def uuid_str(generator=uuid.uuid4, with_hyphen=True):
    if with_hyphen:
        return str(generator())
    else:
        return generator().hex
