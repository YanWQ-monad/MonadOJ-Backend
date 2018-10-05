# -*- coding: utf-8 -*-

"""
Configuration file
"""


class Dict(dict):
    """
    Simple dict but support access as x.y style
    """

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f'`Dict` object has no attribute `{key}`')

    def __setattr__(self, key, value):
        self[key] = value


def to_dict(d):
    """Convert a common dict to Dict

    Args:
        d: (dict) Origin dict object

    Returns:
        Dict: New Dict object
    """
    new_dict = Dict()
    for k, v in d.items():
        new_dict[k] = to_dict(v) if isinstance(v, dict) else v
    return new_dict


configs = {
    'debug': False,
    'web': {
        'host': 'localhost',
        'port': 8082
    },
    'db': {
        'host': 'localhost',
        'port': 3306,
        'user': 'monadoj',
        'password': 'TzlKJNm980kArQCpsHmeBhoha9qLGRn6',
        'db': 'monadoj'
    },
    'session': {
        'max_age': 90000,
        'secret': 'tGK7`iXm(ZtqI;B6}=ndH1KrQ.NCZ3r[9.A9J)G^DwlSq",@IvDeNW-Q;>,ayt'
    },
    'secret': {
        'password_salt': 'g4g4*I^7uj/4t3]4tg4@u867'
    }
}

configs = to_dict(configs)
