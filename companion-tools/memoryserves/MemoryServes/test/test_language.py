#!/usr/bin/env python

import unittest

from .. import language


class TestGetCodes(unittest.TestCase):
    def test_Default(self):
        code = language.get_code("Default")
        assert code is None, code

    def test_Swedish(self):
        code = language.get_code("Swedish")
        assert code == "SV", code

    def test_Italian_Greek(self):
        c1, c2 = language.get_codes("Italian", "Greek")
        assert c1 == "IT", c1
        assert c2 == "EL", c2

    def test_EN_JA(self):
        c1, c2 = language.get_codes("EN", "JA")
        assert c1 == "EN", c1
        assert c2 == "JA", c2

    def test_None(self):
        code = language.get_code("Imaginary Language")
        assert code is None, code
