# -*- coding: utf-8 -*-

import json

from web.model import Problem, ProblemList
from utils.auth import check_admin
from web.coroweb import get, post
from utils.convert import to_int
import utils.apis as apis


@post('/api/admin/problem/add')
async def admin_add_problem(*, token, name, description, input_format, output_format, samples, hint):
    user = await check_admin(token)

    problem = Problem(
        name=name,
        description=description,
        input_format=input_format,
        output_format=output_format,
        samples=samples,
        hint=hint,
        testcases=json.dumps(dict(spj=None, testcases=[])),
        provider=user.name
    )

    await problem.save()

    return problem


@post('/api/admin/problem/edit')
async def admin_edit_problem(*, token, pid, name, description, input_format, output_format, samples, hint, testcases, spj=False):
    await check_admin(token)

    problem = await Problem.find(pid)
    if problem is None:
        raise apis.APIBadRequest('No such problem')

    problem.name = name
    problem.description = description
    problem.input_format = input_format
    problem.output_format = output_format
    problem.samples = samples
    problem.hint = hint
    problem.testcases = json.dumps(dict(spj=spj, testcases=json.loads(testcases)))

    await problem.update()

    return problem


@get('/api/admin/problem/list')
async def admin_list_problem(*, token, index):
    await check_admin(token)

    index = to_int(index)

    num = await ProblemList.count_item('pid')
    page = apis.Page(num, page_index=index)
    problems = await ProblemList.find_all(order_by='pid ASC', limit=(page.offset, page.limit))
    return dict(page=page, problems=problems)
