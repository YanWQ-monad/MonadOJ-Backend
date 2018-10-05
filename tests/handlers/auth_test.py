# -*- coding: utf-8 -*-

from unittest import TestCase

from tests.util import async_test, MonadSession
from web.model import User


class TestAuth(TestCase):
    @async_test
    async def setUp(self):
        self.client = MonadSession()

    @async_test
    async def tearDown(self):
        await self.client.close()
        self.client = None

    async def get_token(self, username, password):
        payload = {
            'username': username,
            'password': password
        }
        req = await self.client.post('/api/auth/login', data=payload)
        return (await req.json())['token']

    @async_test
    async def test_1_register_success(self):
        payload = {
            'username': 'TestRoot',
            'email': 'test_root@test.com',
            'password': 'TEST ROOT ONLY'
        }
        req = await self.client.request('POST', '/api/auth/register', data=payload)
        resp = await req.json()
        user = await User.find_all('name=?', args=['TestRoot'])

        self.assertEqual(len(user), 1)
        user = user[0]
        self.assertIsNone(resp['error'])
        self.assertEqual(user.email, 'test_root@test.com')
        self.assertEqual(user.uid, resp['uid'])
        self.assertFalse(user.admin)
        self.assertNotEqual(resp['password'].find('*'), -1)

        # set user to be admin in order to complete the test after this
        user.admin = True
        await user.update()
        payload = {
            'username': 'Test',
            'email': 'test_user@test.com',
            'password': 'TEST ONLY'
        }
        await self.client.request('POST', '/api/auth/register', data=payload)

    @async_test
    async def test_2_register_duplicate_name(self):
        payload = {
            'username': 'Test',
            'email': 'test_user2@test.com',
            'password': 'TEST ONLY 2'
        }
        req = await self.client.request('POST', '/api/auth/register', data=payload)
        resp = await req.json()

        self.assertEqual(resp['error'], 'value:invalid')
        self.assertEqual(resp['msg'], 'Username is already existed')

    @async_test
    async def test_2_register_duplicate_email(self):
        payload = {
            'username': 'Test2',
            'email': 'test_user@test.com',
            'password': 'TEST ONLY 2'
        }
        req = await self.client.request('POST', '/api/auth/register', data=payload)
        resp = await req.json()

        self.assertEqual(resp['error'], 'value:invalid')
        self.assertEqual(resp['msg'], 'Email is already existed')

    @async_test
    async def test_3_login_success(self):
        payload = {
            'username': 'Test',
            'password': 'TEST ONLY'
        }
        req = await self.client.post('/api/auth/login', data=payload)
        resp = await req.json()

        self.assertIsNone(resp['error'])
        self.assertEqual(resp['msg'], 'Login success')

    @async_test
    async def test_3_login_not_found(self):
        payload = {
            'username': 'Test2',
            'password': 'TEST ONLY'
        }
        req = await self.client.post('/api/auth/login', data=payload)
        resp = await req.json()

        self.assertEqual(resp['error'], 'auth:user_not_find')

    @async_test
    async def test_3_login_invalid_passwd(self):
        payload = {
            'username': 'Test',
            'password': 'TEST ANYONE'
        }
        req = await self.client.post('/api/auth/login', data=payload)
        resp = await req.json()

        self.assertEqual(resp['error'], 'auth:password_error')

    @async_test
    async def test_4_token_success(self):
        token = await self.get_token('TestRoot', 'TEST ROOT ONLY')

        req = await self.client.get('/api/auth/check_token', params={'token': token})
        user = await req.json()

        self.assertIsNone(user['error'])
        self.assertNotEqual(user['password'].find('*'), -1)
        self.assertEqual(user['name'], 'TestRoot')
        self.assertTrue(user['admin'])

    @async_test
    async def test_4_token_invalid(self):
        payload = {'token': 'It is an invalid token'}
        req = await self.client.get('/api/auth/check_token', params=payload)
        user = await req.json()

        self.assertEqual(user['error'], 'auth:invalid_token')
