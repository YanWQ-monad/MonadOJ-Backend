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

    def test_extend_dict(self):
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'b': 3, 'c': 4}

        new_dict = convert.extend_dict(dict1, dict2)
        self.assertEqual(new_dict['a'], 1)
        self.assertEqual(new_dict['b'], 3)

        new_dict = convert.extend_dict(dict2, dict1)
        self.assertEqual(new_dict['b'], 2)

    def test_array_dict_normal(self):
        array = [1, 2, 3]
        new_dict = convert.array_dict(array, ['b', 'a', 'c'])

        expect_dict = {'a': 2, 'b': 1, 'c': 3}
        self.assertDictEqual(new_dict, expect_dict)

    def test_array_dict_with_empty_key(self):
        array = [1, 2, 3]
        new_dict = convert.array_dict(array, ['a', 'b', ''])

        self.assertFalse(3 in new_dict.values())

    def test_dict_array_normal(self):
        origin_dict = {'a': 2, 'b': 1, 'c': 3}
        array = convert.dict_array(origin_dict, ['c', 'b', 'a'])

        self.assertListEqual(array, [3, 1, 2])

    def test_dict_array_with_missing_key(self):
        origin_dict = {'a': 2, 'b': 1, 'c': 3}
        array = convert.dict_array(origin_dict, ['a', 'b', 'd'])

        self.assertIsNone(array[2])
