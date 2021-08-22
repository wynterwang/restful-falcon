# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/8/29"
from __future__ import absolute_import

__all__ = ["Permission"]


class OperandHolder:
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class AND:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, req):
        return (
            self.op1.has_permission(req) &
            self.op2.has_permission(req)
        )


class OR:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, req):
        return (
            self.op1.has_permission(req) |
            self.op2.has_permission(req)
        )


class PermissionMetaclass(type):
    def __and__(cls, other):
        return OperandHolder(AND, cls, other)

    def __or__(cls, other):
        return OperandHolder(OR, cls, other)

    def __rand__(cls, other):
        return OperandHolder(AND, other, cls)

    def __ror__(cls, other):
        return OperandHolder(OR, other, cls)


class Permission(object, metaclass=PermissionMetaclass):
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, req):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True
