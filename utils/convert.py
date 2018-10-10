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
