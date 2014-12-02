#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webnodeex.utils import default_key_generator


def func_identity_generator(f, *args, **kwargs):
    return default_key_generator(f, *args, **kwargs)


class WebNodeEx(object):

    def __set__(self, obj, val):
        print 'setting'
        self.kv = {}
        self.obj = val

    def fetch(self):
        raise NotImplementedError()

    def children(self):
        raise NotImplementedError()

    def obj(self):
        raise NotImplementedError()

    def register(self, func, *args, **kwargs):
        key = func_identity_generator(func, args, kwargs)
        self.kv[key] = (func, args, kwargs)
        return key

    @property
    def kv(self):
        return self.kv


class WebNodeExTree(WebNodeEx):

    def fetch(self):
        pass

    def obj(self):
        pass

    def gao(self):
        self._all = {}

        nodes = self.children()
        while nodes:

            for node in nodes:
                var2key = node.prime()
                key2value = node.kv
