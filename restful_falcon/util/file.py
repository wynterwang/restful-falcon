# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/5"
from __future__ import absolute_import

import os

__all__ = ["exists", "is_file", "is_dir", "list_files"]


def exists(file):
    return os.path.exists(file)


def is_file(file):
    if exists(file):
        return os.path.isfile(file)
    return False


def is_dir(file):
    if exists(file):
        return os.path.isdir(file)
    return False


def list_files(directory, recursive=False, only_file=False):
    files = []
    if os.path.isdir(directory):
        stack = [os.path.join(directory, file) for file in os.listdir(directory)]
        index = 0
        while index < len(stack):
            if is_dir(stack[index]) and recursive:
                stack.extend((os.path.join(stack[index], file) for file in os.listdir(stack[index])))
            if only_file:
                if is_file(stack[index]):
                    files.append(stack[index])
            else:
                files.append(stack[index])
            index += 1
    return files
