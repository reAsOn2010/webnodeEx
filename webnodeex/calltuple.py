#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


def default_key_generator(f, *args, **kwargs):
    import inspect

    func_key = '%s.%s' % (f.im_class.__name__, f.__name__)
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


class CallTuple(object):

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.generate_func = default_key_generator
        self._done = False
        self._result = None

    def done(self):
        return self._done

    def generate_key(self):
        return self.generate_func(self.func, *self.args, **self.kwargs)

    def set_result(self, value, not_set_none=False):
        if not_set_none:
            if value is None:
                return
        self._result = value
        self._done = True

    def result(self):
        return self._result

    def __repr__(self):
        return '<%s %s %s: %s>' % (str(self.func), str(self.args), str(self.kwargs), self._result)

    def call(self):
        if self._done:
            return
        try:
            value = self.func(*self.args, **self.kwargs)
            self.set_result(value)
        except Exception as e:
            # TODO: determine if necessary to raise exception
            self.set_result(None)
            logging.exception('call func failed %s' % self)
            raise e


class CallTupleCenter(object):

    def __init__(self, generate_func):
        self._dict = {}
        if not generate_func:
            self.generate_func = default_key_generator
        else:
            self.generate_func = generate_func

    def get_calltuple(self, func, *args, **kwargs):
        key = self.generate_key(func, *args, **kwargs)
        call = self._dict.get(key)
        if not call:
            call = CallTuple(func, *args, **kwargs)
            self._dict[key] = call
        return (key, call)

    def generate_key(self, func, *args, **kwargs):
        return self.generate_func(func, *args, **kwargs)

    def get_all(self):
        return self._dict
