# -*- coding: utf-8 -*-

import json

from utils.convert import to_int, array_dict
from web.model import ProblemList, Problem
from constant import TESTCASE_DICT_KEYS
from web.coroweb import get
import utils.apis as apis


@get('/api/problems_list')
async def problems_list(*, index):
    index = to_int(index)

    num = await ProblemList.count_item('pid', where='visible=1')
    page = apis.Page(num, page_index=index)
    problems = await ProblemList.find_all(where='visible=1', order_by='pid ASC', limit=(page.offset, page.limit))

    return dict(page=page, problems=problems)


@get('/api/problem/{pid}')
async def get_problem(*, pid):
    pid = to_int(pid)

    problem = await Problem.find(pid)
    if problem is None:
        raise apis.APIBadRequest('No such problem')

    origin_testcases = json.loads(problem.testcases)
    array_testcases = origin_testcases['testcases']
    testcases = [array_dict(testcase, TESTCASE_DICT_KEYS) for testcase in array_testcases]
    problem.testcases = dict(testcases=testcases, spj=origin_testcases['spj'])

    return problem
