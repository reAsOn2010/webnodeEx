#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools

from calltuple import default_key_generator
from calltuple import CallTuple


class BaseFetchDriver(object):

    _namespace = None

    def __init__(self, namespace):
        self._namespace = namespace
        if not self._namespace:
            raise NotImplementedError

    def fetch(self, kv):
        raise NotImplementedError


class RedisFetchDriver(BaseFetchDriver):

    def __init__(self, client, gen_func=None):
        super(RedisFetchDriver, self).__init__('redis')
        self.client = client
        self.gen_func = gen_func
        if not gen_func:
            self.gen_func = default_key_generator

    def mget(self, keys):
        '''
        This mget accepts a list of key
        return key and value, which can be directly update into dict
        Override this method as you want
        '''
        values = self.client.mget(keys)
        zipped = zip(keys, values)
        result = itertools.compress(zipped, [pair[1] is not None for pair in zipped])
        return result

    def prepare(self, kv):
        pass

    def execute(self, kv):
        keys = []
        for k, v in kv.iteritems():
            if isinstance(v, CallTuple):
                keys.append(k)
        result = self.mget(keys)
        kv.update(result)

    def finish(self, kv):
        pass


class RPCFetchDriver(BaseFetchDriver):

    def __init__(self, aggregate_rule=None, client=None):
        super(RPCFetchDriver, self).__init__('RPC')
        self.rule = aggregate_rule
        self._kv = {}

    def prepare(self, kv):
        pass

    def execute(self, kv):
        for k, v in kv.iteritems():
            if isinstance(v, CallTuple):
                try:
                    value = v.call()
                    kv[k] = value
                    self._kv[k] = value
                except:
                    kv[k] = None

    def finish(self, kv):
        pass

    def get_self_kv(self):
        return self._kv
