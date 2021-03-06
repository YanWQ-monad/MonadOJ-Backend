# -*- coding: utf-8 -*-

from unittest import TestCase
import json
import os

from utils.convert import extend_dict, array_dict
from tests.util import async_test, MonadSession
from constant import TESTCASE_DICT_KEYS
from web.model import Problem
import config


class TestAdminProblem(TestCase):
    @classmethod
    @async_test
    async def setUpClass(cls):
        cls.problem_list = [
            {
                'name': 'A+B Problem',
                'description': 'Calc `a+b` from given a, b',
                'input_format': 'Two integers a, b',
                'output_format': 'An integer, the result of `a+b`',
                'samples': json.dumps([
                    {'input': '856 1070', 'output': '1926'},
                    {'input': '1 3', 'output': '4'}]),
                'hint': 'No hint'
            },
            {
                'name': 'A-B Problem',
                'description': 'Calc `a-b` from given a, b',
                'input_format': 'Two integers a, b',
                'output_format': 'An integer, the result of `a-b`',
                'samples': json.dumps([
                    {'input': '856 1070', 'output': '-214'},
                    {'input': '5 2', 'output': '3'}]),
                'hint': 'No hint'
            },
            {
                'name': 'A*B Problem',
                'description': 'Calc `a*b` from given a, b',
                'input_format': 'Two integers a, b',
                'output_format': 'An integer, the result of `a*b`',
                'samples': json.dumps([
                    {'input': '856 1070', 'output': '915920'},
                    {'input': '3 4', 'output': '12'}]),
                'hint': ''
            }
        ]
        cls.client = MonadSession()
        payload = {
            'username': 'TestRoot',
            'password': 'TEST ROOT ONLY'
        }
        async with cls.client.post('/api/auth/login', data=payload) as resp:
            cls.token = (await resp.json())['token']
        cls.headers = {
            'Authorization': cls.token
        }

    @classmethod
    @async_test
    async def tearDownClass(cls):
        await cls.client.close()
        cls.client = None

    @async_test
    async def test_1_create_problem(self):
        keys = ['name', 'description', 'input_format', 'output_format', 'samples', 'hint']

        async with self.client.post('/api/admin/problem/add', data=self.problem_list[0], headers=self.headers) as resp:
            msg = await resp.json()

        self.assertEqual(msg['pid'], 1000)
        problem = await Problem.find(1000)

        for key in keys:
            self.assertEqual(msg[key], self.problem_list[0][key])
            self.assertEqual(msg[key], problem[key])

    @async_test
    async def test_2_create_more_problems(self):
        for (index, problem_info) in enumerate(self.problem_list[1:], start=1001):
            async with self.client.post('/api/admin/problem/add', data=problem_info, headers=self.headers) as resp:
                msg = await resp.json()

            self.assertEqual(msg['pid'], index)

        problem_count = await Problem.count_item('pid')
        self.assertEqual(problem_count, len(self.problem_list))

    @async_test
    async def test_3_list_problems(self):
        params = {
            'index': '1'
        }
        async with self.client.get('/api/admin/problem/list', params=params, headers=self.headers) as resp:
            msg = await resp.json()

        self.assertEqual(msg['page']['page_count'], 1)
        self.assertEqual(msg['page']['item_count'], 3)

        for (pid, problem) in enumerate(msg['problems'], start=1000):
            self.assertEqual(problem['pid'], pid)
            self.assertEqual(problem['name'], self.problem_list[pid - 1000]['name'])

    @async_test
    async def test_4_get_problem(self):
        params = {
            'pid': 1000
        }
        async with self.client.get('/api/admin/problem/get', params=params, headers=self.headers) as resp:
            msg = await resp.json()

        self.assertEqual(msg['pid'], 1000)
        keys = ['name', 'description', 'input_format', 'output_format', 'samples', 'hint']
        for key in keys:
            self.assertEqual(msg[key], self.problem_list[0][key])

    @async_test
    async def test_5_edit_problem(self):
        self.problem_list[2]['hint'] = 'No hint'
        request_body = extend_dict(self.problem_list[2], {
            'pid': 1002,
            'testcases': '[]'
        })
        async with self.client.post('/api/admin/problem/edit', data=request_body, headers=self.headers) as resp:
            msg = await resp.json()

        problem = await Problem.find(1002)
        self.assertIsNotNone(problem)
        self.assertEqual(msg['hint'], 'No hint')
        self.assertEqual(problem.hint, 'No hint')

    @async_test
    async def test_6_add_testcases(self):
        request_body = {
            'pid': '1000',
            'zip_bin': open('tests/resources/data_1000.zip', 'rb')
        }
        async with self.client.post('/api/admin/problem/upload_testcases', data=request_body, headers=self.headers) as resp:
            msg = await resp.json()

        self.assertEqual(len(msg['testcases']), 10)

        for (index, testcase) in enumerate(msg['testcases']):
            self.assertEqual(testcase['index'], index)
            self.assertEqual(testcase['score'], 10)

        expect_list = [f'{index}.{suffix}' for index in range(10) for suffix in ['in', 'out']]
        files_list = os.listdir(os.path.join(config.configs.judge.testcases_path, '1000'))
        self.assertListEqual(sorted(files_list), sorted(expect_list))

        problem = await Problem.find(1000)
        self.assertIsNotNone(problem)
        testcases = json.loads(problem.testcases)['testcases']
        self.assertEqual(len(testcases), 10)

    @async_test
    async def test_7_add_more_testcases(self):
        for pid in range(1001, 1000+len(self.problem_list)):
            request_body = {
                'pid': str(pid),
                'zip_bin': open(f'tests/resources/data_{pid}.zip', 'rb')
            }
            async with self.client.post('/api/admin/problem/upload_testcases', data=request_body, headers=self.headers):
                pass

        expect_list = [str(pid) for pid in range(1000, 1000+len(self.problem_list))]
        dirs_list = os.listdir(os.path.join(config.configs.judge.testcases_path))
        self.assertListEqual(sorted(dirs_list), sorted(expect_list))

    @async_test
    async def test_8_update_testcases_information(self):
        params = {
            'pid': 1001
        }
        async with self.client.get('/api/admin/problem/get', params=params, headers=self.headers) as resp:
            problem = await resp.json()

        testcases_detail = problem['testcases']['testcases']
        for testcase in testcases_detail:
            testcase['time'] = 2000

        problem['testcases'] = json.dumps(testcases_detail)

        async with self.client.post('/api/admin/problem/edit', data=problem, headers=self.headers) as resp:
            msg = await resp.json()
            self.assertIsNone(msg['error'])

        db_problem = await Problem.find(1001)
        self.assertIsNotNone(db_problem)

        testcases = json.loads(db_problem.testcases)['testcases']
        for testcase in testcases:
            testcase = array_dict(testcase, TESTCASE_DICT_KEYS)
            self.assertEqual(testcase['time'], 2000)
