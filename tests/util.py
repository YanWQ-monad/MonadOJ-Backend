# -*- coding: utf-8 -*-

import asyncio
import aiohttp

import config


def async_test(func):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(func)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class MonadSession(aiohttp.ClientSession):
    async def _request(self, method, url, **kwargs):
        if url.find('://') == -1:
            url = f'http://{config.configs.web.host}:{config.configs.web.port}' + url
        return await aiohttp.ClientSession._request(self, method, url, **kwargs)

    def _ws_connect(self, url, **kwargs):
        url = f'ws://{config.configs.web.host}:{config.configs.web.port}' + url
        return aiohttp.ClientSession._ws_connect(self, url, **kwargs)
