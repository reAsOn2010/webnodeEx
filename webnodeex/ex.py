#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from itertools import repeat

from calltuple import CallTuple


class WebNodeException(Exception):
    pass


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


class LargeYieldNode(object):

    def __init__(self):
        self.var2key = {}
        self.key2child = {}
        self.key2value = {}
        self._iterator = None
        self._children = None
        self.current_level_key2value = {}
        self.center = ClientCenter(self)

    def register(self):
        yield {}

    def children(self):
        yield {}

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

    def nurture(self):
        if self._children is None:
            self._children = self.children()
        self.key2child.update(next(self._children, {}))
        nodes = reduce(lambda x, y: x.extend(y) or x if isinstance(y, list) else x.append(y) or x,
                       self.key2child.values(), [])
        return nodes

    def __getattr__(self, name):
        client = self.center.get(name)
        if not client:
            return self._fetch(name)
        return client

    def _fetch(self, name):
        value = self.var2key.get(name, None)
        if not value:
            return None
        if isinstance(value, list):
            return map(lambda x: self.key2value.get(x, None), value)
        return self.key2value.get(value, None)


class LargeYieldRoot(LargeYieldNode):

    def __init__(self, rpc, drivers):
        super(LargeYieldRoot, self).__init__()
        for key, client in rpc.iteritems():
            ClientCenter.put(key, client)
        self.drivers = drivers
        self.all_key2value = {}

    def gao(self):
        nodes = self.nurture()
        while nodes:
            next_level_nodes = []
            current_key2value = {}

            for node in nodes:
                key2value = node.next()
                if not key2value:
                    next_generation = node.nurture()
                    if next_generation:
                        next_level_nodes.extend(next_generation)
                else:
                    next_level_nodes.append(node)
                current_key2value.update(key2value)

            # aggregate and filter duplicate fetch
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


class MediumYieldNode(object):

    def __init__(self):
        self._key2child = {}
        self._call_iter = None
        self._child_iter = None
        self._current_level_key2value = OrderedDict()
        self._current_keys = []
        self._center = ClientCenter(self)
        self._key = ''

    def key(self):
        if not self._key:
            name = self.__class__.__name__
            params = []
            for k, v in self.__dict__.iteritems():
                if k not in ['_key2child', '_call_iter', '_child_iter', '_current_level_key2value', '_current_keys', '_center', '_key']:
                    params.append('%s:%s' % (str(k), str(v)))
            self._key = '%s|%s' % (name, ','.join(params))
        return self._key

    def register(self):
        yield []

    def children(self):
        yield []

    def submit(self, call_tuple):
        key = call_tuple.generate_key()
        self._current_level_key2value[key] = call_tuple
        return key

    def trans(self, key2value):
        f = lambda x: \
            [key2value.get(key) for key in x] \
            if isinstance(x, list) \
            else key2value.get(key)
        return map(f, self._current_keys)

    def send(self, key2value):
        try:
            if self._call_iter is None:
                self._call_iter = self.register()
                self._current_level_key2value.clear()
                self._current_keys = self._call_iter.next()
            else:
                assert(isinstance(self._current_keys, (basestring, list)))
                if isinstance(self._current_keys, basestring):
                    to_send = key2value.get(self._current_keys)
                else:
                    to_send = []
                    for item in self._current_keys:
                        assert(isinstance(item, (basestring, list)))
                        if isinstance(item, list):
                            to_send.append([key2value.get(k) for k in item])
                        else:
                            to_send.append(key2value.get(item))
                self._current_level_key2value.clear()
                self._current_keys = self._call_iter.send(to_send)
        except StopIteration:
            self._current_level_key2value.clear()
            pass
        finally:
            return self._current_level_key2value

    def nurture(self):
        if self._child_iter is None:
            self._child_iter = self.children()
        _child = next(self._child_iter, [])
        nodes = []
        for item in _child:
            if isinstance(item, list):
                nodes.extend(item)
                for node in item:
                    self._key2child[node.key()] = node
            else:
                nodes.append(item)
                self._key2child[item.key()] = item
        try:
            self._child_iter.send(_child)
        except StopIteration:
            pass
        return nodes

    def __getattr__(self, name):
        client = self._center.get(name)
        if not client:
            raise WebNodeException('No such rpc client: %s' % name)
        return client


class MediumYieldRoot(MediumYieldNode):

    def __init__(self, rpc, drivers):
        super(MediumYieldRoot, self).__init__()
        for key, client in rpc.iteritems():
            ClientCenter.put(key, client)
        self.drivers = drivers
        self.all_key2value = {}

    def gao(self):
        nodes = self.nurture()
        while nodes:
            next_level_nodes = []
            current_key2value = {}

            for node in nodes:
                key2value = node.send(self.all_key2value)
                # key2value = node.next()
                if not key2value:
                    next_generation = node.nurture()
                    if next_generation:
                        next_level_nodes.extend(next_generation)
                else:
                    next_level_nodes.append(node)
                current_key2value.update(key2value)

            # aggregate and filter duplicate fetch
            current_key2value.update((key, self.all_key2value[key]) for key in current_key2value.viewkeys() & self.all_key2value.viewkeys())

            print current_key2value

            for driver in self.drivers:
                driver.prepare(current_key2value)

            for driver in self.drivers:
                driver.execute(current_key2value)

            for driver in self.drivers:
                driver.finish(current_key2value)

            self.all_key2value.update(current_key2value)

            nodes = next_level_nodes
