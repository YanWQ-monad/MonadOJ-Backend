# -*- coding: utf-8 -*-

import functools
import hashlib
import time

from utils.apis import APIPermissionError, APINeedLogin
from utils.convert import to_int
from web.model import User
from config import configs


def gen_token(user):
    """Get token from a User Model

    Args:
        user: (User) User Model

    Returns:
        str: The token of the user
    """
    # token format: 'uid;expires;sha'
    expires = str(int(time.time()) + configs.session.max_age)
    key = '{}-{}+{}-{}'.format(user.uid, expires, user.password, configs.session.secret)
    sha = hashlib.sha512(key.encode('utf-8')).hexdigest()
    token = '/'.join([str(user.uid), expires, sha])

    return token


async def parse_token(token):
    """Parse token to User Model

    Args:
        token: (str) The token

    Returns:
        - None: If the token is invalid
          User: The User Model of the token
    """
    if not token:
        return None
    lst = token.split('/')
    if len(lst) != 3:
        return None
    uid, expires, sha = lst
    if to_int(expires, default=0) < time.time():
        return None
    user = await User.find(uid)
    if user is None:
        return None
    key = '{}-{}+{}-{}'.format(str(uid), expires, user.password, configs.session.secret)
    if sha != hashlib.sha512(key.encode('utf-8')).hexdigest():
        return None

    user.password = '********'
    return user


async def check_admin(token):
    user = await parse_token(token)
    if user is None or user.admin is False:
        raise APIPermissionError()
    return user


def admin_required(func):
    """Handler decorator for filtering non-administrator

    If the user of the token (from headers) has not administrator permission,
    apis.APIPermissionError will be raised

    Raises:
        apis.APIPermissionError if the user is not administrator
    """
    @functools.wraps(func)
    async def wrapper(wrapper_request, *args, **kwargs):
        user = wrapper_request.user
        if user is None or not user.admin:
            raise APIPermissionError()

        return await func(*args, **kwargs)

    wrapper.__require_request__ = True

    return wrapper


def login_required(func):
    """Handler decorator for filtering non-login-request

    If the user of the token (from headers) is not valid user,
    apis.APINeedLogin will be raised

    Raises:
        apis.APINeedLogin if the user is not administrator
    """
    @functools.wraps(func)
    async def wrapper(wrapper_request, *args, **kwargs):
        if wrapper_request.user is None:
            raise APINeedLogin()

        return await func(*args, **kwargs)

    wrapper.__require_request__ = True

    return wrapper
