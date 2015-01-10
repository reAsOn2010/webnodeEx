#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from webnodeex.dummy import DummyRPC
from webnodeex.mediumdummy import Root
from webnodeex.proxy import ClientCenter


class MediumYieldNodeTest(unittest.TestCase):

    def setUp(self):
        ClientCenter.put('dummy_rpc', DummyRPC())
        self.root = Root()

    def test_gather_func(self):
        self.root.gao()

    def test_redis_mset(self):
        for i in range(1, 3):
            key = 'DummyRPC.call_by_id:i,%d' % i
            assert(self.root.redis._DATA[key] == i)
        for i in range(3, 8):
            key = 'DummyRPC.call_by_id:i,%d' % i
            assert(self.root.redis._DATA.get(key) is None)
        self.root.gao()
        for i in range(1, 8):
            key = 'DummyRPC.call_by_id:i,%d' % i
            assert(self.root.redis._DATA[key] == i)
