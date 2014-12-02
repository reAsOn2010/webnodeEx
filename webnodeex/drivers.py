#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseFetchDriver(object):

    _namespace = None

    def __init__(self, namespace):
        self._namespace = namespace
        if not self._namespace:
            raise NotImplementedError

    def _in():
        NotImplementedError()

    def _out():
        NotImplementedError()


def default_key_generator(f, *args, **kwargs):
    import inspect

    func_key = '%s.%s' % (f.im_func.__module__, f.__name__)
    arg_keys = inspect.getargspec(f).args
    has_self = bool(arg_keys) and arg_keys[0] in ('self', 'cls')
    if has_self:
        arg_keys = arg_keys[1:]

    kwargs = kwargs.items()
    for i in range(0, len(args)):
        kwargs.append((arg_keys[i], args[i]))

    if kwargs:
        params_key = map(lambda x: ','.join(x),
                         map(lambda x: map(unicode, x),
                             sorted(kwargs, key=lambda x: x[0])))

    return ':'.join([func_key] + params_key)


class RedisFetchDriver(BaseFetchDriver):

    def __init__(self, gen_func=None):
        super(RedisFetchDriver, self).__init('redis')
        self.gen_func = gen_func
        if not gen_func:
            self.gen_func = default_key_generator

    def _fetch():
        pass
