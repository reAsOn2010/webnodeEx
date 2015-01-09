#!/usr/bin/env python
# -*- coding: utf-8 -*-

from calltuple import CallTuple
from exception import WebNodeException


class ClientProxy(object):

    def __init__(self, node, client, attrs=None):
        self.node = node
        self.client = client
        self._attrs = [] if attrs is None else attrs

    def __getattr__(self, name):
        attrs = self._attrs[:]
        attrs.append(name)
        return ClientProxy(self.node, self.client, attrs)

    def __call__(self, *args, **kwargs):
        func = reduce(getattr, [self.client] + self._attrs)
        return self.node.submit(CallTuple(func, *args, **kwargs))


class ClientCenter(object):

    RPC_CLIENTS = {}

    def __init__(self, node):
        self.node = node

    @classmethod
    def put(cls, name, client):
        cls.RPC_CLIENTS[name] = client

    def get(self, name):
        client = self.RPC_CLIENTS.get(name, None)
        if not client:
            return None
        return ClientProxy(self.node, client)


class ResultProxy(object):

    def __init__(self):
        self._ready = False
        self.value = None

    def set_result(self, value):
        if self._value is not None:
            raise WebNodeException('Set value to ready result')
        self._value = value
        self._ready = True

    @property
    def value(self):
        return self._value

    @property
    def ready(self):
        return self._ready
