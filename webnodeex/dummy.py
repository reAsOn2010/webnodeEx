#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
