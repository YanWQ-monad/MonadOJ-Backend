# -*- coding: utf-8 -*-

from unittest.mock import patch
from unittest import TestCase
import time

from tests.util import async_test, MonadSession
from web.model import User
import config


class TestAuth(TestCase):
    @classmethod
    @async_test
    async def setUpClass(self):
        self.client = MonadSession()

    @classmethod
    @async_test
    async def tearDownClass(self):
        await self.client.close()
        self.client = None

    async def get_token(self, username, password):
        payload = {
            'username': username,
            'password': password
        }
        async with self.client.post('/api/auth/login', data=payload) as resp:
            return (await resp.json())['token']

    async def check_token(self, token):
        headers = {'Authorization': token}
        async with self.client.get('/api/auth/check_token', headers=headers) as resp:
            return await resp.json()

    @async_test
    async def test_1_register_success(self):
        payload = {
            'username': 'TestRoot',
            'email': 'test_root@test.com',
            'password': 'TEST ROOT ONLY'
        }
        async with self.client.request('POST', '/api/auth/register', data=payload) as resp:
            msg = await resp.json()

        user = await User.find_all('name=?', args=['TestRoot'])

        self.assertEqual(len(user), 1)
        user = user[0]
        tk = await self.check_token(msg['token'])
        self.assertEqual(tk['uid'], msg['uid'])
        self.assertIsNone(msg['error'])
        self.assertEqual(user.email, 'test_root@test.com')
        self.assertEqual(user.uid, msg['uid'])
        self.assertFalse(user.admin)
        self.assertNotEqual(msg['password'].find('*'), -1)

        # set user to be admin and create a common user in order to complete the test after this
        user.admin = True
        await user.update()
        payload = {
            'username': 'Test',
            'email': 'test_user@test.com',
            'password': 'TEST ONLY'
        }
        async with self.client.request('POST', '/api/auth/register', data=payload):
            pass

    @async_test
    async def test_2_register_duplicate_name(self):
        payload = {
            'username': 'Test',
            'email': 'test_user2@test.com',
            'password': 'TEST ONLY 2'
        }
        async with self.client.request('POST', '/api/auth/register', data=payload) as resp:
            msg = await resp.json()

        self.assertEqual(msg['error'], 'value:invalid')
        self.assertEqual(msg['msg'], 'Username is already existed')

    @async_test
    async def test_2_register_duplicate_email(self):
        payload = {
            'username': 'Test2',
            'email': 'test_user@test.com',
            'password': 'TEST ONLY 2'
        }
        async with self.client.request('POST', '/api/auth/register', data=payload) as resp:
            msg = await resp.json()

        self.assertEqual(msg['error'], 'value:invalid')
        self.assertEqual(msg['msg'], 'Email is already existed')

    @async_test
    async def test_3_login_success(self):
        payload = {
            'username': 'Test',
            'password': 'TEST ONLY'
        }
        async with self.client.post('/api/auth/login', data=payload) as resp:
            msg = await resp.json()

        self.assertIsNone(msg['error'])
        self.assertEqual(msg['msg'], 'Login success')

    @async_test
    async def test_3_login_not_found(self):
        payload = {
            'username': 'Test2',
            'password': 'TEST ONLY'
        }
        async with self.client.post('/api/auth/login', data=payload) as resp:
            msg = await resp.json()

        self.assertEqual(msg['error'], 'auth:user_not_find')

    @async_test
    async def test_3_login_invalid_password(self):
        payload = {
            'username': 'Test',
            'password': 'TEST ANYONE'
        }
        async with self.client.post('/api/auth/login', data=payload) as resp:
            msg = await resp.json()

        self.assertEqual(msg['error'], 'auth:password_error')

    @async_test
    async def test_4_token_success(self):
        token = await self.get_token('TestRoot', 'TEST ROOT ONLY')

        user = await self.check_token(token)

        self.assertIsNone(user['error'])
        self.assertNotEqual(user['password'].find('*'), -1)
        self.assertEqual(user['name'], 'TestRoot')
        self.assertTrue(user['admin'])

    @async_test
    async def test_4_token_invalid(self):
        user = await self.check_token('It is an invalid token')
        self.assertEqual(user['error'], 'auth:invalid_token')

        user = await self.check_token('')
        self.assertEqual(user['error'], 'auth:invalid_token')

        user = await self.check_token('233/233/233')
        self.assertEqual(user['error'], 'auth:invalid_token')

        end_time = int(time.time() + config.configs.session.max_age)
        user = await self.check_token(f'1/{end_time}/123456ABCDEF')
        self.assertEqual(user['error'], 'auth:invalid_token')

        user = await self.check_token(f'1000/{end_time}/123456ABCDEF')
        self.assertEqual(user['error'], 'auth:invalid_token')

    @async_test
    async def test_4_token_outdate(self):
        token = await self.get_token('Test', 'TEST ONLY')

        user = await self.check_token(token)
        self.assertIsNone(user['error'])

        # make the time exceed the lifetime of the token
        end_time = int(time.time() + config.configs.session.max_age + 100)

        with patch('time.time', return_value=end_time):
            user = await self.check_token(token)
            self.assertEqual(user['error'], 'auth:invalid_token')
