#coding: UTF8

import unittest
from .. import model
import edist

class TestGloss100(unittest.TestCase):
    def setUp(self):
        self.records = [model.MemoryRecord(source=u"foo",
                             trans=u"bar"),
                        model.MemoryRecord(source=u"cmyk分解",
                             trans=u"CMYK separation"),]

    def test_simple(self):
        hits = [r for r in self.records if r.source_cmp in u"I luv foo!"]
        assert len(hits) == 1, hits
        assert hits[0].source_cmp == u"foo", hits

    def test_mixed(self):
        hits = [r for r in self.records if r.source_cmp in u"this has cmyk分解 inside"]
        assert len(hits) == 1, hits
        assert hits[0].source_cmp == u"cmyk分解", hits

    def test_mixed_70(self):
        hits = [r for r in self.records if edist.get_subscore(r.source_cmp, u"this has cmyk分解 inside") >= .7]
        assert len(hits) == 1, hits
        assert hits[0].source_cmp == u"cmyk分解", hits
