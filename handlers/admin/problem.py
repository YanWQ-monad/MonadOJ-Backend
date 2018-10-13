# -*- coding: utf-8 -*-

import aiofiles
import zipfile
import shutil
import json
import os

from utils.convert import to_int, dict_array, array_dict
from web.model import Problem, ProblemList
from constant import TESTCASE_DICT_KEYS
from utils.auth import admin_required
from web.coroweb import get, post
from config import configs
import utils.apis as apis


@post('/api/admin/problem/add')
@admin_required
async def admin_add_problem(*, request, name, description, input_format, output_format, samples, hint):
    problem = Problem(
        name=name,
        description=description,
        input_format=input_format,
        output_format=output_format,
        samples=samples,
        hint=hint,
        testcases=json.dumps(dict(spj=None, testcases=[])),
        provider=request.user.name
    )

    await problem.save()

    return problem


@post('/api/admin/problem/edit')
@admin_required
async def admin_edit_problem(*, pid, name, description, input_format, output_format, samples, hint, testcases, spj=False):
    problem = await Problem.find(pid)
    if problem is None:
        raise apis.APIBadRequest('No such problem')

    problem.name = name
    problem.description = description
    problem.input_format = input_format
    problem.output_format = output_format
    problem.samples = samples
    problem.hint = hint

    dict_testcases = json.loads(testcases)
    testcases = [dict_array(testcase, TESTCASE_DICT_KEYS) for testcase in dict_testcases]
    problem.testcases = json.dumps(dict(spj=spj, testcases=testcases))

    await problem.update()

    return problem


@get('/api/admin/problem/get')
@admin_required
async def admin_get_problem(*, pid):
    problem = await Problem.find(pid)
    if problem is None:
        raise apis.APIBadRequest('No such problem')

    origin_testcases = json.loads(problem.testcases)
    array_testcases = origin_testcases['testcases']
    testcases = [array_dict(testcase, TESTCASE_DICT_KEYS) for testcase in array_testcases]
    problem.testcases = dict(testcases=testcases, spj=origin_testcases['spj'])

    return problem


@post('/api/admin/problem/upload_testcases')
@admin_required
async def admin_upload_testcases(*, pid, zip_bin, spj=False):
    def namelist_filter(lst, with_spj):
        prefixes = [name[:-3] for name in lst if name.endswith('.in') and '/' not in name]
        testcases = [dict(index=i, name=name, out=(f'{name}.out' in lst)) for (i, name) in enumerate(prefixes)]
        if not with_spj:
            testcases = list(filter(lambda item: item['out'], testcases))
        return testcases

    async def write_file(path, data):
        async with aiofiles.open(path, 'wb') as f:
            await f.write(data.replace(b'\r\n', b'\n').replace(b'\r', b'\n'))
        os.chmod(path, 0o640)

    problem = await Problem.find(pid)
    if problem is None:
        raise apis.APIBadRequest('No such problem')

    try:
        zip_file = zipfile.ZipFile(zip_bin.file)
    except zipfile.BadZipFile:
        raise apis.APIBadRequest('Bad zip file')

    files = zip_file.namelist()
    files = namelist_filter(files, spj)

    data_dir = os.path.join(configs.judge.testcases_path, str(pid))
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.mkdir(data_dir, mode=0o750)

    for testcase in files:
        index, name, out = dict_array(testcase, ['index', 'name', 'out'])
        await write_file(os.path.join(data_dir, f'{index}.in'), zip_file.read(f'{name}.in'))
        if out:
            await write_file(os.path.join(data_dir, f'{index}.out'), zip_file.read(f'{name}.out'))

    testcases = []
    for (index, testcase) in enumerate(files):
        testcase['memory'] = 256
        testcase['time'] = 1000
        testcase['score'] = 100 // len(files) + (100 % len(files) >= (len(files) - index))

        dumped = dict_array(testcase, TESTCASE_DICT_KEYS)
        testcases.append(dumped)

    problem.testcases = json.dumps(dict(testcases=testcases, spj=spj))
    await problem.update()

    return dict(testcases=files)


@get('/api/admin/problem/list')
@admin_required
async def admin_list_problem(*, index):
    index = to_int(index)

    num = await ProblemList.count_item('pid')
    page = apis.Page(num, page_index=index)
    problems = await ProblemList.find_all(order_by='pid ASC', limit=(page.offset, page.limit))
    return dict(page=page, problems=problems)
