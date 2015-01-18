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
        for key, node in self.root._key2child.iteritems():
            if key == 'Node1|i:1':
                assert node.d3 == [1, 2, 3, 4, 5]
                for key2, node2 in node._key2child.iteritems():
                    if key2 == 'Node2|':
                        assert node2.d1 == 1
                        assert node2.d2 == 3
                    elif key2 in ['NodePlus2|i:%d' % num for num in range(3, 8)]:
                        assert node2.d1 == int(key2[-1])
                    else:
                        assert False
            elif key == 'Node2|':
                assert node.d1 == 1
                assert node.d2 == 3
            elif key == 'Node3|':
                assert node.d3 == 2
            else:
                assert False

    def test_redis_mset(self):
        for i in range(1, 3):
            key = 'DummyRPC.call_by_id:i,%d' % i
            assert self.root.redis._DATA[key] == i
        for i in range(3, 8):
            key = 'DummyRPC.call_by_id:i,%d' % i
            assert self.root.redis._DATA.get(key) is None
        self.root.gao()
        for i in range(1, 8):
            key = 'DummyRPC.call_by_id:i,%d' % i
            assert self.root.redis._DATA[key] == i
