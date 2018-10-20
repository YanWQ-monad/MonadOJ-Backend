# -*- coding: utf-8 -*-

import unittest

from .handlers.admin_problem_test import TestAdminProblem
from .handlers.coroweb_test import TestCoroutineWeb
from .handlers.problem_test import TestProblem
from .utils.convert_test import TestConvert
from .handlers.auth_test import TestAuth
from .utils.apis_test import TestApis


def get_test_suite():
    suite = unittest.TestSuite()

    def add_test_class(cls):
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(cls))

    add_test_class(TestCoroutineWeb)
    add_test_class(TestConvert)
    add_test_class(TestApis)
    add_test_class(TestAuth)
    add_test_class(TestAdminProblem)
    add_test_class(TestProblem)

    return suite
