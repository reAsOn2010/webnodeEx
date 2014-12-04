#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.0.1'

from calltuple import CallTuple


class WebNodeEx(object):

    def __init__(self):
        self.var2key = {}
        self.key2value = {}
        self._iterator = None
        self.current_level_key2value = {}

    def register(self):
        raise NotImplementedError()

    def children(self):
        raise NotImplementedError()

    def obj(self):
        raise NotImplementedError()

    def submit(self, func, *args, **kwargs):
        call_tuple = CallTuple(func, *args, **kwargs)
        key = call_tuple.generate_key()
        self.key2value[key] = call_tuple
        self.current_level_key2value[key] = call_tuple
        return key

    def get_kvmap(self):
        return self.key2value

    def restore(self, all_key2value):
        self.key2value.update((key, all_key2value[key]) for key in self.key2value.viewkeys() & all_key2value.viewkeys())

    def __getattr__(self, var):
        return self.key2value.get(self.var2key.get(var, None), None)

    def next(self):
        if self._iterator is None:
            self._iterator = self.register()
        self.current_level_key2value.clear()
        self.var2key.update(next(self._iterator, {}))
        return self.current_level_key2value

    def printall(self):
        print self.var2key
        print self.key2value
        print self.d1
        print self.d2


class WebNodeExTree(WebNodeEx):

    def __init__(self, drivers=None):
        super(WebNodeExTree, self).__init__()
        self.drivers = drivers
        self.all_key2value = {}

    def register(self):
        pass

    def obj(self):
        pass

    def prepare(self):
        pass

    def finish(self):
        pass

    def gao(self):

        self.prepare()
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

        self.finish()

    def printall(self, nodes):
        print self.all_key2value
        for node in nodes:
            node.printall()
