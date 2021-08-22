# -*- coding: utf-8 -*-
# __author__ = "wynterwang"
# __date__ = "2020/11/13"
from __future__ import absolute_import

import base64
from functools import partial

from restful_falcon.util.module import import_module

__all__ = ["Cipher", "DefaultCipher"]


class Cipher:
    def __init__(self, module, key=None, mode=None, **kwargs):
        self.__module = module
        self.__kwargs = kwargs
        if key:
            self.__kwargs["key"] = key.encode(encoding="utf-8")
        if mode:
            self.__kwargs["mode"] = mode
        if "iv" in kwargs:
            self.__kwargs["iv"] = self.__kwargs["iv"].encode(encoding="utf-8")

    def _padding(self, _bytes):
        if 1 <= self.__kwargs.get("mode", 0) <= 2:
            block_size = self.__module.block_size
            count = block_size - (len(_bytes) % block_size)
            _bytes = _bytes + b'\0' * count
        return _bytes

    def _un_padding(self, _bytes):
        if 1 <= self.__kwargs.get("mode", 0) <= 2:
            _bytes = _bytes.strip(b'\0')
        return _bytes

    def encrypt(self, plaintext):
        cipher = self.__module.new(**self.__kwargs)
        _bytes = cipher.encrypt(self._padding(plaintext.encode(encoding="utf-8")))
        return base64.encodebytes(_bytes).decode(encoding="utf-8")

    def decrypt(self, ciphertext):
        cipher = self.__module.new(**self.__kwargs)
        _bytes = base64.decodebytes(ciphertext.encode(encoding="utf-8"))
        return self._un_padding(cipher.decrypt(_bytes)).decode(encoding="utf-8")


DEFAULT_MODULE = import_module("Crypto.Cipher.AES")
DEFAULT_IV = "2020101441010202"
DefaultCipher = partial(Cipher, DEFAULT_MODULE, mode=DEFAULT_MODULE.MODE_CBC, iv=DEFAULT_IV)
