# -*- coding: utf-8 -*-

from utils.apis import APIBadRequest


def to_int(s, *, err=APIBadRequest, default=None):
    try:
        num = int(s)
    except ValueError:
        if default is not None:
            return default
        raise err('params must be an integer')
    return num
