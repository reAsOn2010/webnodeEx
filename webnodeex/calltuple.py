#!/usr/bin/env python
# -*- coding: utf-8 -*-


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

    def generate_key(self):
        return self.generate_func(self.func, *self.args, **self.kwargs)

    def call(self):
        return self.func(*self.args, **self.kwargs)
