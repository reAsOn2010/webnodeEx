#!/usr/bin/env python
# -*- coding: utf-8 -*-

from calltuple import default_key_generator


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
        if not keys:
            values = []
        else:
            values = self.client.mget(keys)
        return values

    def mset(self, kv={}):
        return self.client.mset(kv)

    def prepare(self, kv):
        pass

    def execute(self, kv):
        keys = []
        for k, v in kv.iteritems():
            if not v.done():
                keys.append(k)
        values = self.mget(keys)
        map(lambda x, y: kv[x].set_result(y, not_set_none=True), keys, values)

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
            if not v.done():
                v.call()
                self._kv[k] = v.result()

    def finish(self, kv):
        pass

    def get_self_kv(self):
        return self._kv
