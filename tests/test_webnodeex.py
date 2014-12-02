# -*- coding: utf-8 -*-

import unittest
from tornado.util import ObjectDict
from webnodeex import WebNodeEx, WebNodeExTree


class WebNodeExTest(unittest.TestCase):

    def setUp(self):

        class DummyRPC(object):

            def call_by_id(i=0):
                return i

            def call_by_ids(ids=[]):
                return []


        class Node1(WebNodeEx):

            def __init__(self):
                self.client = DummyRPC()

            def fetch():
                return ObjectDict(
                    d1=register(self.client.call_by_id, 1),
                    d2=register(self.client.call_by_id, 2),
                )

            def child():
                return []

            def obj():
                return ObjectDict(
                    data1=self.d1,
                    data2=self.d2,
                )

        class Node2(WebNodeEx):

            def __init__(self):
                self.client = DummyRPC()

            def fetch():
                return ObjectDict(
                    d1=register(self.client.call_by_id, 1),
                    d2=register(self.client.call_by_id, 3),
                )

            def child():
                return []

            def obj():
                return ObjectDict(
                    data1=self.d1,
                    data2=self.d2,
                )

        class Root(WebNodeExTree):

            def child():
                return [Node1(), Node2()]

        self.root = WebNodeExTree()


    def test_gather_func(self):
