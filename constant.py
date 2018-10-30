# -*- coding: utf-8 -*-

TESTCASE_DICT_KEYS = [
    'index', 'out', 'time', 'memory', 'score']

JUDGE_RESULT_KEYS_ALL = [
    'cpu_time', 'signal', 'memory', 'exit_code', 'result', 'error', 'real_time', 'score']

JUDGE_RESULT_KEYS_USER = [
    'cpu_time', '', 'memory', '', 'result', '', '', 'score']


class JUDGE_STATUS:
    PENDING = 0
    RUNNING = 1
    DONE = 2


class JUDGE_RESULT:
    PENDING = 0
    ACCEPTED = 1
    CPU_TIME_LIMIT_EXCEEDED = 2
    REAL_TIME_LIMIT_EXCEEDED = 3
    MEMORY_LIMIT_EXCEEDED = 4
    RUNTIME_ERROR = 5
    SYSTEM_ERROR = 6
    WRONG_ANSWER = 7
    COMPILE_ERROR = 8
    PARTLY_CORRECT = 9
