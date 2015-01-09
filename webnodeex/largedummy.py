#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.util import ObjectDict

from drivers import RedisFetchDriver, RPCFetchDriver
from dummy import DummyRedis
from largeyield import LargeYieldNode, LargeYieldRoot


class DummyLargeYieldRoot(LargeYieldRoot):

    def __init__(self):
        self.redis = DummyRedis()
        self.redis_driver = RedisFetchDriver(self.redis)
        self.rpc_driver = RPCFetchDriver()
        super(DummyLargeYieldRoot, self).__init__([self.redis_driver, self.rpc_driver])

    def finish(self):
        self.redis.mset(self.rpc_driver.get_self_kv())


class Root(DummyLargeYieldRoot):

    def __init__(self):
        super(Root, self).__init__()

    def children(self):
        yield {
            'node1': Node1(i=1),
            'node2': Node2(),
            'node3': Node3(),
        }


class NodePlus2(LargeYieldNode):

    def __init__(self, i):
        super(NodePlus2, self).__init__()
        self.i = i + 2

    def register(self):
        yield ObjectDict(
            d1=self.dummy_rpc.call_by_id(self.i)
        )


class Node1(LargeYieldNode):

    def __init__(self, i):
        super(Node1, self).__init__()
        self.i = i

    def register(self):
        yield ObjectDict(
            d1=self.dummy_rpc.call_by_id(self.i),
            d2=self.dummy_rpc.call_by_id(2),
            d3=[self.dummy_rpc.call_by_id(i) for i in range(1, 6)]
        )

    def children(self):
        yield {
            'node1': Node2(),
            'nodes': [NodePlus2(i=x) for x in self.d3],
        }


class Node2(LargeYieldNode):

    def __init__(self):
        super(Node2, self).__init__()

    def register(self):
        yield {
            'd1': self.dummy_rpc.call_by_id(1),
            'd2': self.dummy_rpc.call_by_id(3),
        }

    def children(self):
        yield {}


class Node3(LargeYieldNode):

    def __init__(self):
        super(Node3, self).__init__()

    def register(self):
        yield {
            'd1': self.dummy_rpc.call_by_id(2),
            'd2': self.dummy_rpc.call_by_id(4),
        }
        yield {
            'd3': self.dummy_rpc.call_by_id(self.d1),
        }

    def children(self):
        yield {}
