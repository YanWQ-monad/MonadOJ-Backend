# -*- coding: utf-8 -*-

from utils.auth import parse_token
from aiohttp import web
import logging
import json


@web.middleware
async def auth(request, handler):
    """Parse `User-Token` in headers
    Parse the token and store User Model to `request.user`

    Args:
        request (aiohttp.web.Request): Request instance
        handler (function): The handler function

    Returns:
        Any: Forward the return value from handler()
    """
    token = request.headers.get('Authorization', '')
    user = await parse_token(token)
    request.user = user

    resp = await handler(request)
    return resp


@web.middleware
async def response(request, handler):
    """Processing the response from the handler

    Args:
        request (aiohttp.web.Request): Request instance
        handler (function): The handler function

    Returns:
        aiohttp.web.Response: The response generate from the return value of handler
    """
    def is_status_code(code):
        return isinstance(code, int) and 100 <= code < 600

    logging.debug('Response handler...')
    r = await handler(request)
    status = 200

    if isinstance(r, tuple) and len(r) == 2:
        _status, body = r
        if is_status_code(_status):
            r = body
            status = _status

    # StreamResponse object
    if isinstance(r, web.StreamResponse):
        return r

    # binary response
    if isinstance(r, bytes):
        logging.debug("=========")
        resp = web.Response(body=r)
        resp.content_type = 'application/octet-stream'
        return resp

    # body only
    if isinstance(r, str):
        if r.startswith('redirect:'):
            return web.HTTPFound(r[9:])
        resp = web.Response(body=r.encode('utf-8'), status=status)
        resp.content_type = 'text/html;charset=utf-8'
        return resp

    # json data
    if isinstance(r, dict):
        r['error'] = r.get('error', None)
        resp = web.Response(
            body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'),
            status=status)
        resp.content_type = 'application/json;charset=utf-8'
        return resp

    # status code only
    if is_status_code(r):
        return web.Response(status=r)

    # default:
    resp = web.Response(body=str(r).encode('utf-8'), status=status)
    resp.content_type = 'text/plain;charset=utf-8'
    return resp


middlewares = [auth, response]
