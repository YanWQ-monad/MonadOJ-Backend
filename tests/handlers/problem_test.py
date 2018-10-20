# -*- coding: utf-8 -*-

import json

from tests.util import async_test, MonadSession
from unittest import TestCase


class TestProblem(TestCase):
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
    async def test_problem_list(self):
        params = {'index': 1}
        async with self.client.get('/api/problems_list', params=params) as resp:
            msg = await resp.json()

        self.assertEqual(len(msg['problems']), 3)
        self.assertEqual(msg['page']['page_index'], 1)

        names = [
            'A+B Problem',
            'A-B Problem',
            'A*B Problem']

        for (name, problem) in zip(names, msg['problems']):
            self.assertEqual(name, problem['name'])

    @async_test
    async def test_get_problem(self):
        pid = 1000
        async with self.client.get(f'/api/problem/{pid}') as resp:
            msg = await resp.json()

        problem = {
            'pid': 1000,
            'name': 'A+B Problem',
            'description': 'Calc `a+b` from given a, b',
            'input_format': 'Two integers a, b',
            'output_format': 'An integer, the result of `a+b`',
            'hint': 'No hint'
        }

        for (key, value) in problem.items():
            self.assertIn(key, msg)
            self.assertEqual(msg[key], value)

        sample = json.loads(msg['samples'])[0]
        self.assertEqual(sample['input'], '856 1070')
        self.assertEqual(sample['output'], '1926')

        testcases = msg['testcases']['testcases']
        self.assertEqual(len(testcases), 10)

    @async_test
    async def test_problem_not_found(self):
        async with self.client.get('/api/problem/999') as resp:
            msg = await resp.json()

        self.assertEqual(resp.status, 400)
        self.assertEqual(msg['msg'], 'No such problem')
