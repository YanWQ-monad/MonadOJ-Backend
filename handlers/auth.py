# -*- coding: utf-8 -*-

import hashlib

from web.coroweb import get, post
from web.model import User
from config import configs
import utils.auth as auth
import utils.apis as apis


@post('/api/auth/login')
async def user_login(*, username, password):
    user = await User.find_all('name=?', [username], size=1)
    if len(user) == 0:
        return dict(error='auth:user_not_find', msg='No such user')
    user = user[0]

    sha = hashlib.sha512()
    salt = configs.secret.password_salt
    sha.update(f'{salt}{username}{user.email}{password}{salt}'.encode('utf-8'))
    if sha.hexdigest() != user.password:
        return dict(error='auth:password_error', msg='Username or password is incorrect')

    return dict(msg='Login success', token=auth.gen_token(user))


@get('/api/auth/check_token')
async def check_token(*, token):
    user = await auth.parse_token(token)
    if user is None:
        return dict(error='auth:invalid_token', msg='Invalid Token')
    user.password = '********'
    return user


@post('/api/auth/register')
async def user_register(*, username, email, password):
    if len(await User.find_all('name=?', [username], size=1)) > 0:
        raise apis.APIValueError('Username is already existed')
    if len(await User.find_all('email=?', [email], size=1)) > 0:
        raise apis.APIValueError('Email is already existed')

    sha = hashlib.sha512()
    salt = configs.secret.password_salt
    sha.update(f'{salt}{username}{email}{password}{salt}'.encode('utf-8'))

    gravatar = 'https://www.gravatar.com/avatar/{}?d=mm&s=128'.format(hashlib.md5(email.lower().encode('utf-8')).hexdigest())
    user = User(name=username, email=email, password=sha.hexdigest(), admin=False, image=gravatar)
    await user.save()

    user.token = auth.gen_token(user)
    user.password = '********'
    return user
