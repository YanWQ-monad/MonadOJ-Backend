# -*- coding: utf-8 -*-

from utils.apis import APIBadRequest


def to_int(s, *, err=APIBadRequest, default=None):
    try:
        num = int(s)
    except ValueError:
        if default is not None:
            return default
        raise err('one of the params must be an integer')
    return num


def extend_dict(*args):
    result = dict()
    for arg in args:
        result.update(arg)
    return result


def array_dict(arr, order):
    assert len(arr) == len(order)
    ret = dict(zip(order, arr))
    if '' in ret:
        del ret['']
    return ret


def dict_array(d, order):
    arr = [None for _ in range(len(order))]

    for (k, v) in d.items():
        if k in order:
            arr[order.index(k)] = v

    return arr
