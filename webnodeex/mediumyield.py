#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict
from exception import WebNodeException
from proxy import ClientCenter


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

    def send(self, key2value):
        try:
            if self._call_iter is None:
                self._call_iter = self.register()
                self._current_level_key2value.clear()
                self._current_keys = self._call_iter.next()
            else:
                assert(isinstance(self._current_keys, (basestring, list)))
                if isinstance(self._current_keys, basestring):
                    to_send = key2value.get(self._current_keys).result()
                else:
                    to_send = []
                    for item in self._current_keys:
                        assert(isinstance(item, (basestring, list)))
                        if isinstance(item, list):
                            to_send.append([key2value.get(k).result() for k in item])
                        else:
                            to_send.append(key2value.get(item).result())
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

    def center(self):
        return self._center

    def __getattr__(self, name):
        client = self._center.get(name)
        if not client:
            raise WebNodeException('No such rpc client: %s' % name)
        return client


class MediumYieldRoot(MediumYieldNode):

    def __init__(self, drivers):
        super(MediumYieldRoot, self).__init__()
        self.drivers = drivers
        self.all_key2value = {}

    def prepare(self):
        self.on_prepare()

    def on_prepare(self):
        pass

    def finish(self):
        self.on_finish()

    def on_finish(self):
        pass

    def gao(self):
        self.prepare()
        nodes = self.nurture()
        level = 0
        while nodes:
            logging.debug('level: %d' % level)
            level += 1
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

            logging.debug(self.all_key2value)

            for driver in self.drivers:
                driver.prepare(current_key2value)

            for driver in self.drivers:
                driver.execute(current_key2value)

            for driver in self.drivers:
                driver.finish(current_key2value)

            self.all_key2value.update(current_key2value)

            nodes = next_level_nodes

        self.finish()
