#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.0.1'

from calltuple import CallTuple


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


class WebNodeEx(object):

    def __init__(self):
        self.var2key = {}
        self.key2value = {}
        self._iterator = None
        self.current_level_key2value = {}
        self.center = ClientCenter(self)

    def children(self):
        raise NotImplementedError()

    def obj(self):
        raise NotImplementedError()

    def submit(self, call_tuple):
        key = call_tuple.generate_key()
        self.key2value[key] = call_tuple
        self.current_level_key2value[key] = call_tuple
        return key

    def get_kvmap(self):
        return self.key2value

    def restore(self, all_key2value):
        self.key2value.update((key, all_key2value[key]) for key in self.key2value.viewkeys() & all_key2value.viewkeys())

    def next(self):
        if self._iterator is None:
            self._iterator = self.register()
        self.current_level_key2value.clear()
        self.var2key.update(next(self._iterator, {}))
        return self.current_level_key2value

    def __getattr__(self, name):
        client = self.center.get(name)
        if not client:
            return self.key2value.get(self.var2key.get(name, None), None)
        return client


class WebNodeExRoot(WebNodeEx):

    def __init__(self, rpc, drivers):
        super(WebNodeExRoot, self).__init__()
        for key, client in rpc.iteritems():
            ClientCenter.put(key, client)
        self.drivers = drivers
        self.all_key2value = {}

    def gao(self):
        nodes = self.children()
        while nodes:
            next_level_nodes = []
            current_key2value = {}

            for node in nodes:
                key2value = node.next()
                if not key2value:
                    next_level_nodes.extend(node.children())
                else:
                    next_level_nodes.append(node)
                current_key2value.update(key2value)

            # TODO: aggregate and filter duplicate fetch
            current_key2value.update((key, self.all_key2value[key]) for key in current_key2value.viewkeys() & self.all_key2value.viewkeys())

            print current_key2value

            for driver in self.drivers:
                driver.prepare(current_key2value)

            for driver in self.drivers:
                driver.execute(current_key2value)

            for driver in self.drivers:
                driver.finish(current_key2value)

            self.all_key2value.update(current_key2value)

            for node in nodes:
                node.restore(current_key2value)

            nodes = next_level_nodes
