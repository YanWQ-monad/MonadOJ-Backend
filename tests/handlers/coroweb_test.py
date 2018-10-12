# -*- coding: utf-8 -*-

from unittest import TestCase

from tests.util import async_test, MonadSession


class TestCoroutineWeb(TestCase):
    @classmethod
    @async_test
    async def setUpClass(cls):
        cls.client = MonadSession()

    @classmethod
    @async_test
    async def tearDownClass(cls):
        await cls.client.close()
        cls.client = None

    @async_test
    async def test_basic_get(self):
        async with self.client.get('/test/get') as resp:
            self.assertEqual(resp.status, 200)
            msg = await resp.json()

        self.assertEqual(msg['msg'], 'Success')
        self.assertIsNone(msg['error'])

    @async_test
    async def test_get_param(self):
        params = dict(param='Get Param')
        async with self.client.get('/test/get_params', params=params) as resp:
            msg = await resp.json()

        self.assertIsNone(msg['error'])
        self.assertEqual(msg['msg'], 'Get Param')

    @async_test
    async def test_get_missing_param(self):
        async with self.client.get('/test/get_params') as resp:
            self.assertEqual(resp.status, 400)
            msg = await resp.json()

        self.assertIsNotNone(msg['error'])
        self.assertEqual(msg['error'], 'request:missing_params')

    @async_test
    async def test_get_param_default(self):
        params = dict(param='Get Param')
        async with self.client.get('/test/get_default_params', params=params) as resp:
            msg = await resp.json()

        self.assertIsNone(msg['error'])
        self.assertEqual(msg['msg'], 'Get Param DEFAULT')

    @async_test
    async def test_post(self):
        payload = dict(data='Post Data')
        async with self.client.post('/test/post', data=payload) as resp:
            self.assertEqual(resp.status, 200)
            msg = await resp.json()

        self.assertIsNone(msg['error'])
        self.assertEqual(msg['msg'], 'Post Data')

    @async_test
    async def test_api_error(self):
        async with self.client.get('/test/api_error') as resp:
            self.assertEqual(resp.status, 400)
            msg = await resp.json()

        self.assertEqual(msg['error'], 'test:test_error')
        self.assertEqual(msg['msg'], 'Some Error')

    @async_test
    async def test_204(self):
        async with self.client.get('/test/204') as resp:
            self.assertEqual(resp.status, 204)

    @async_test
    async def test_return_str(self):
        async with self.client.get('/test/return_str') as resp:
            msg = await resp.text()

        self.assertEqual(msg, 'Hello')

    @async_test
    async def test_return_byte(self):
        async with self.client.get('/test/return_byte') as resp:
            msg = await resp.read()

        self.assertEqual(msg, b'Hello bytes')

    @async_test
    async def test_return_with_500(self):
        async with self.client.get('/test/return_with_500') as resp:
            self.assertEqual(resp.status, 500)
            msg = await resp.text()

        self.assertEqual(msg, 'Server internal error (fake)')

    @async_test
    async def test_websocket(self):
        async with self.client.ws_connect('/test/websocket') as ws:
            await ws.send_json(dict(type='msg', msg='Hello from test client'))
            msg = (await ws.receive_json())['msg']
            self.assertEqual(msg, 'Hello from test client')

            await ws.send_json(dict(type='hello'))
            msg = (await ws.receive_json())['error']
            self.assertEqual(msg, 'Invalid message type: hello')
