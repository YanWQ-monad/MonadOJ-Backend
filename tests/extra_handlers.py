#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp.web
import logging
import json

from web.coroweb import get, post
import utils.apis as apis


@get('/test/get')
async def get_test():
    return dict(msg='Success')


@get('/test/get_params')
async def get_param_test(*, param):
    return dict(msg=param)


@get('/test/get_default_params')
async def get_default_params_test(*, param, param2='DEFAULT'):
    return dict(msg=' '.join([param, param2]))


@post('/test/post')
async def post_test(*, data):
    return dict(msg=data)


@get('/test/api_error')
async def api_error_test():
    raise apis.APIError('test:test_error', 'Some Error')


@get('/test/204')
async def status_204_test():
    return 204


@get('/test/return_str')
async def return_str_test():
    return 'Hello'


@get('/test/return_byte')
async def return_byte_test():
    return b'Hello bytes'


@get('/test/return_with_500')
async def return_with_500_test():
    return 500, 'Server internal error (fake)'


@get('/test/websocket')
async def ws_test(*, request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data['type'] == 'close':
                await ws.close()
            elif data['type'] == 'msg':
                await ws.send_json(dict(msg=data['msg']))
            else:
                await ws.send_json(dict(error=f'Invalid message type: {data["type"]}'))
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.warning(f'Websocket connection closed with exception:\n{ws.exception()}')

    return ws
