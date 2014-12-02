#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.util import ObjectDict

from webnodeex import WebNodeEx, WebNodeExTree


class DummyRPC(object):

    def call_by_id(i=0):
        return i

    def call_by_ids(ids=[]):
        return []


class Root(WebNodeExTree):

    def child():
        return [Node1(), Node1()]


class Node1(WebNodeEx):

    def __init__(self):
        super(Node1, self).__init__()
        self.client = DummyRPC()

    def prime(self):
        return ObjectDict(
            d1=self.register(self.client.call_by_id, 1),
            d2=self.register(self.client.call_by_id, 2),
        )

    def children(self):
        return []

    def obj(self):
        return ObjectDict(
            data1=self.d1,
            data2=self.d2,
        )
