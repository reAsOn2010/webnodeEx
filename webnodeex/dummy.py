#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DummyRPC(object):

    def __init__(self):
        self._CALL_TIME_MAP = {}

    def call_by_id(self, i=0):
        check = self._CALL_TIME_MAP.get(i)
        assert(check is None)
        self._CALL_TIME_MAP[i] = True
        return i

    def call_by_ids(self, ids=[]):
        check = self._CALL_TIME_MAP.get(str(ids))
        assert(check is None)
        self._CALL_TIME_MAP[str(ids)] = True
        return ids


class DummyRedis(object):

    def __init__(self):
        self._CALL_TIME_MAP = {}
        self._DATA = {'DummyRPC.call_by_id:i,1': 1,
                      'DummyRPC.call_by_id:i,2': 2}

    def get(self, key=None):
        check = self._CALL_TIME_MAP.get(key)
        assert(check is None)
        self._CALL_TIME_MAP[key] = True

        if key > 5:
            return None
        return key

    def mget(self, keys=[]):
        check = self._CALL_TIME_MAP.get(str(keys))
        assert(check is None)
        self._CALL_TIME_MAP[str(keys)] = True

        result = []
        for key in keys:
            result.append(self._DATA.get(key))
        else:
            result.append(None)
        return result

    def mset(self, kv={}):
        for key, value in kv.iteritems():
            self._DATA[key] = value
        return len(kv)

    def set(self, key, value):
        self._DATA[key] = value
        return 1
