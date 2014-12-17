#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.util import ObjectDict

from ex import WebNodeEx, WebNodeExRoot
from drivers import RedisFetchDriver, RPCFetchDriver


class DummyRPC(object):

    def call_by_id(self, i=0):
        return i

    def call_by_ids(self, ids=[]):
        return []


class DummyRedis(object):

    def get(self, key=None):
        if key > 5:
            return None
        return key

    def mget(self, keys=[]):
        print 'mget %s' % str(keys)
        result = []
        d = {'DummyRPC.call_by_id:i,1': 1,
             'DummyRPC.call_by_id:i,2': 2}
        for key in keys:
            result.append(d.get(key))
        else:
            result.append(None)
        return result

    def mset(self, kv={}):
        return None


class DummyNodeExRoot(WebNodeExRoot):

    def __init__(self):
        self.redis = DummyRedis()
        self.redis_driver = RedisFetchDriver(self.redis)
        self.rpc_driver = RPCFetchDriver()
        self.rpc = {
            'dummy_rpc': DummyRPC()
        }
        super(DummyNodeExRoot, self).__init__(self.rpc, [self.redis_driver, self.rpc_driver])

    def finish(self):
        self.redis.mset(self.rpc_driver.get_self_kv())


class Root(DummyNodeExRoot):

    def __init__(self):
        super(Root, self).__init__()

    def children(self):
        yield {
            'node1': Node1(i=1),
            'node2': Node2(),
            'node3': Node3(),
        }


class NodePlus2(WebNodeEx):

    def __init__(self, i):
        super(NodePlus2, self).__init__()
        self.i = i + 2

    def register(self):
        yield ObjectDict(
            d1=self.dummy_rpc.call_by_id(self.i)
        )


class Node1(WebNodeEx):

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


class Node2(WebNodeEx):

    def __init__(self):
        super(Node2, self).__init__()

    def register(self):
        yield {
            'd1': self.dummy_rpc.call_by_id(1),
            'd2': self.dummy_rpc.call_by_id(3),
        }

    def children(self):
        yield {}


class Node3(WebNodeEx):

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
