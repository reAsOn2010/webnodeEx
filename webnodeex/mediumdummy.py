#!/usr/bin/env python
# -*- coding: utf-8 -*-

from drivers import RedisFetchDriver, RPCFetchDriver
from dummy import DummyRPC, DummyRedis
from ex import MediumYieldNode, MediumYieldRoot


class DummyMediumYieldRoot(MediumYieldRoot):

    def __init__(self):
        self.redis = DummyRedis()
        self.redis_driver = RedisFetchDriver(self.redis)
        self.rpc_driver = RPCFetchDriver()
        self.rpc = {
            'dummy_rpc': DummyRPC()
        }
        super(DummyMediumYieldRoot, self).__init__(self.rpc, [self.redis_driver, self.rpc_driver])

    def finish(self):
        self.redis.mset(self.rpc_driver.get_self_kv())


class Root(DummyMediumYieldRoot):

    def __init__(self):
        super(Root, self).__init__()

    def children(self):
        node1, node2, node3 = yield [
            Node1(i=1),
            Node2(),
            Node3(),
        ]


class NodePlus2(MediumYieldNode):

    def __init__(self, i):
        super(NodePlus2, self).__init__()
        self.i = i + 2

    def register(self):
        d1 = yield self.dummy_rpc.call_by_id(self.i)
        assert(d1 == d1)


class Node1(MediumYieldNode):

    def __init__(self, i):
        super(Node1, self).__init__()
        self.i = i

    def register(self):
        d1, d2, self.d3 = yield [
            self.dummy_rpc.call_by_id(self.i),
            self.dummy_rpc.call_by_id(2),
            [self.dummy_rpc.call_by_id(i) for i in range(1, 6)],
        ]

    def children(self):
        node1, nodes = yield [
            Node2(),
            [NodePlus2(i=x) for x in self.d3],
        ]


class Node2(MediumYieldNode):

    def __init__(self):
        super(Node2, self).__init__()

    def register(self):
        d1, d2 = yield [
            self.dummy_rpc.call_by_id(1),
            self.dummy_rpc.call_by_id(3),
        ]

    def children(self):
        yield []


class Node3(MediumYieldNode):

    def __init__(self):
        super(Node3, self).__init__()

    def register(self):
        d1, d2 = yield [
            self.dummy_rpc.call_by_id(2),
            self.dummy_rpc.call_by_id(4),
        ]
        d3 = yield [
            self.dummy_rpc.call_by_id(d1),
        ]
        assert(d3 == d3)

    def children(self):
        yield []
