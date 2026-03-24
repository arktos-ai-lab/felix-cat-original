#coding: utf8
"""
Unit tests for `mem_parser` module.
"""

import unittest

import mock

from .. import mem_parser


class TestE2D(unittest.TestCase):
    def test_empty(self):
        element = mock.MagicMock()
        element.getchildren.return_value = []

        actual = mem_parser.e2d(element)
        expected = {}

        assert actual == expected, actual

    def test_unicode_child(self):
        element = mock.MagicMock()
        child = mock.MagicMock()
        child.tag = "source"
        child.text = u"text"
        element.getchildren.return_value = [child]

        actual = mem_parser.e2d(element)
        expected = {"source" : u"text"}

        assert actual == expected, actual

    def test_utf8_child(self):
        element = mock.MagicMock()
        child = mock.MagicMock()
        child.tag = "source"
        child.text = "text"
        element.getchildren.return_value = [child]

        actual = mem_parser.e2d(element)
        expected = {"source" : u"text"}

        assert actual == expected, actual

    def test_empty_child(self):
        element = mock.MagicMock()
        child = mock.MagicMock()
        child.tag = "source"
        child.text = None
        element.getchildren.return_value = [child]

        actual = mem_parser.e2d(element)
        expected = {"source" : u""}

        assert actual == expected, actual
