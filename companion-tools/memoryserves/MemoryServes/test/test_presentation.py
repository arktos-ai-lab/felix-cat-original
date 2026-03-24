import unittest
from .. import presentation

class TestFormatNum(unittest.TestCase):
    def test_1(self):
        actual = presentation.format_num(1)
        assert actual == "1", actual

    def test_1001(self):
        actual = presentation.format_num(1001)
        assert actual == "1,001", actual

    def test_spam(self):
        actual = presentation.format_num("spam")
        assert actual == "spam", actual

    def test_unicode(self):
        actual = presentation.format_num(u"spam")
        assert actual == u"spam", actual
