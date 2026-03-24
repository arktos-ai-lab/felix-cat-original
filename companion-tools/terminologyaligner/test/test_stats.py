# coding: utf-8
__author__ = 'Ryan'

import unittest
from TerminologyAligner import stats

class Associations(unittest.TestCase):
    def setUp(self):
        stats.THRESHOLD = 1

    def test_empty(self):
        associations = stats.Associations()
        assert associations.get_associations(u"a") == {}, associations.get_associations(u"a")
        assert associations.get_association(u"a", u"b") == 0, associations.get_association(u"a", u"b")

    def test_one_segment(self):
        source_tokens = [[u'a', u'b', u'c']]
        target_tokens = [[u'漢', u'字']]

        associations = stats.Associations()
        for source, target in zip(source_tokens, target_tokens):
            associations.add_associations(source, target)

        expected = 1
        actual = associations.get_association(u"a", u'漢')
        assert actual == expected, actual

    def test_one_segment_counts(self):
        source_tokens = [[u'a', u'b', u'c']]
        target_tokens = [[u'漢', u'字']]

        associations = stats.Associations()
        for source, target in zip(source_tokens, target_tokens):
            associations.add_associations(source, target)

        expected = 1
        actual = associations.get_count(u"a")
        assert actual == expected, actual

    def test_two_segments(self):
        source_tokens = [[u'a', u'b', u'c'],
                       [u'a', u'か', u'な']]
        target_tokens = [[u'漢', u'字'],
                       [u'漢', u'字']]


        associations = stats.Associations()
        for source, target in zip(source_tokens, target_tokens):
            associations.add_associations(source, target)

        expected = 2
        actual = associations.get_association(u"a", u'漢')
        assert actual == expected, actual

    def test_two_segments_counts(self):
        source_tokens = [[u'a', u'b', u'c'],
                       [u'a', u'か', u'な']]
        target_tokens = [[u'漢', u'字'],
                       [u'漢', u'字']]


        associations = stats.Associations()
        for source, target in zip(source_tokens, target_tokens):
            associations.add_associations(source, target)

        expected = 1
        actual = associations.get_count(u"b")
        assert actual == expected, actual

    def test_two_get_strong(self):
        source_tokens = [[u'a', u'b', u'c'],
                       [u'a', u'か', u'な']]
        target_tokens = [[u'漢', u'字'],
                       [u'漢', u'字']]


        associations = stats.Associations()
        for source, target in zip(source_tokens, target_tokens):
            associations.add_associations(source, target)

        expected = [(u'a', u'漢', 2),
                    (u'a',  u'字', 2),
                    ]
        actual = associations.get_strong()
        assert actual == expected, actual


    def test_three_get_strong(self):
        source_tokens = [[u'a', u'b', u'c'],
                       [u'a', u'd', u'e'],
                       [u'a', u'f', u'g'],]
        target_tokens = [u'漢和',
                       u'漢字',
                       u'漢等']


        associations = stats.Associations()
        for source, target in zip(source_tokens, target_tokens):
            associations.add_associations(source, target)

        expected = [(u'a', u'漢', 3),
                    ]
        actual = associations.get_strong()
        assert actual == expected, actual