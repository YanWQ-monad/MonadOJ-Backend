# -*- coding: utf-8 -*-

from unittest import TestCase

import utils.convert as convert
import utils.apis as apis


class TestConvert(TestCase):
    def test_to_int_normal(self):
        self.assertEqual(convert.to_int('123456'), 123456)

    def test_to_int_exception(self):
        with self.assertRaises(apis.APIBadRequest):
            convert.to_int('123.456')

        with self.assertRaises(apis.APIValueError):
            convert.to_int('hello', err=apis.APIValueError)

    def test_to_int_default(self):
        number = convert.to_int('none', default=1013)
        self.assertEqual(number, 1013)
