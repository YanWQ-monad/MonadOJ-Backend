# -*- coding: utf-8 -*-

from unittest import TestCase

from utils.apis import Page


class TestApis(TestCase):
    def test_page_1(self):
        p = Page(100, 1)
        self.assertEqual(p.page_count, 4)
        self.assertEqual(p.offset, 0)
        self.assertEqual(p.limit, 30)

    def test_page_2(self):
        p = Page(90, 9, 10)
        self.assertEqual(p.page_count, 9)
        self.assertEqual(p.offset, 80)
        self.assertEqual(p.limit, 10)

    def test_page_3(self):
        p = Page(91, 10, 10)
        self.assertEqual(p.page_count, 10)
        self.assertEqual(p.offset, 90)
        self.assertEqual(p.limit, 10)
