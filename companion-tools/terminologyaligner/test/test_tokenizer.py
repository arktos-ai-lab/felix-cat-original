# coding: UTF-8
__author__ = 'Ryan'

import unittest
from TerminologyAligner import tokenize

class TestHasAsian(unittest.TestCase):
    def test_ascii(self):
        text = u"foo"
        assert not tokenize.has_asian(text)
    def test_Japanese(self):
        text = u"日本語"
        assert tokenize.has_asian(text)
    def test_mixed(self):
        text = u"English and 日本語"
        assert tokenize.has_asian(text)

class TestGetCharType(unittest.TestCase):
    def test_digit(self):
        c = u"1"
        expected = "digit"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_letter(self):
        c = u"a"
        expected = "letter"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_punctuation(self):
        c = u"!"
        expected = "punctuation"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_space(self):
        c = u"\n"
        expected = "space"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual


    # dbc "ascii"
    def test_full_digit(self):
        c = u"２"
        expected = "full digit"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_full_letter(self):
        c = u"Ｂ"
        expected = "full letter"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_full_punctuation(self):
        c = u"？"
        expected = "full punctuation"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual


    def test_half_katakana(self):
        c = u"ｶ"
        expected = "half katakana"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_katakana(self):
        c = u"カ"
        expected = "katakana"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_hiragana(self):
        c = u"ま"
        expected = "hiragana"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_kanji(self):
        c = u"日"
        expected = "kanji"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_hangul(self):
        c = u"한"
        expected = "hangul"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_dbc_space(self):
        c = u"　"
        expected = "dbc space"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

    def test_sbc(self):
        c = unichr(127)
        expected = "sbc"
        actual = tokenize.get_char_type(c)
        assert actual == expected, actual

class TestGetAsciiCharType(unittest.TestCase):
    def test_digit(self):
        c = u"1"
        expected = "digit"
        actual = tokenize.get_ascii_char_type(c)
        assert actual == expected, actual

    def test_letter(self):
        c = u"a"
        expected = "letter"
        actual = tokenize.get_ascii_char_type(c)
        assert actual == expected, actual

    def test_punctuation(self):
        c = u"!"
        expected = "punctuation"
        actual = tokenize.get_ascii_char_type(c)
        assert actual == expected, actual

    def test_space(self):
        c = u"\n"
        expected = "space"
        actual = tokenize.get_ascii_char_type(c)
        assert actual == expected, actual

    def test_sbc(self):
        c = unichr(127)
        expected = "sbc"
        actual = tokenize.get_ascii_char_type(c)
        assert actual == expected, actual

class TestTokenize(unittest.TestCase):
    def test_empty(self):
        text = u""
        actual = tokenize.tokenize(text)
        assert not actual, actual

    def test_kanji(self):
        text = u"日本"
        actual = tokenize.tokenize(text)
        assert actual == [u"日本"], actual

    def test_hiragana(self):
        text = u"ひらがな"
        actual = tokenize.tokenize(text)
        assert actual == [u"ひらがな"], actual

    def test_katakana_with_space(self):
        text = u"カタ カナ"
        actual = tokenize.tokenize(text)
        assert actual == [u"カタ", u"カナ"], actual

    def test_kanji_and_hiragana(self):
        text = u"日本語が難しい"
        actual = tokenize.tokenize(text)
        assert actual == [u"日本語", u"が", u"難", u"しい"], actual

    def test_this_is_a_house(self):
        text = u"This is a house"
        actual = tokenize.tokenize(text)
        expected = [u"This", u"is", u"a", u"house"]
        assert actual == expected, actual