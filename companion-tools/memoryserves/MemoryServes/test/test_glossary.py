#coding: UTF8

import unittest
from .. import api
from .. import model
import cPickle


from apitest_base import ApiTester

class TestGloss(ApiTester):
    def test_mem_doesnt_exist(self):
        self.add_record("xxx", "yyy")
        rows = cPickle.loads(self.api.gloss("10", query="I have xxx movies", minscore="1.0"))
        assert rows is None, rows

    def test_simple_100(self):
        self.add_record("xxx", "yyy")
        rows = cPickle.loads(self.api.gloss("1", query="I have xxx movies", minscore="1.0"))
        assert len(rows) == 1, rows
        data = rows[0]
        assert data["source"] == u"xxx", data
        assert data["trans"] == u"yyy", data

    def test_j(self):
        self.add_record("分解", "separation")
        rows = cPickle.loads(self.api.gloss("1", query="I have CMYK分解 movies", minscore="1.0"))
        assert len(rows) == 1, rows
        data = rows[0]
        assert data["source"] == u"分解", data
        assert data["trans"] == u"separation", data

    def test_mixed_j_and_e(self):
        self.add_record("CMYK分解", "CMYK separation")
        rows = cPickle.loads(self.api.gloss("1", query="I have CMYK分解 movies", minscore="1.0"))
        assert len(rows) == 1, rows
        data = rows[0]
        assert data["source"] == u"CMYK分解", data
        assert data["trans"] == u"CMYK separation", data

    def test_UT414_100(self):
        self.add_record(u"UT414", u"UT414")
        rows = cPickle.loads(self.api.gloss("1", query="I have UT414 movies", minscore="1.0"))
        assert len(rows) == 1, rows
        data = rows[0]
        assert data["source"] == u"UT414", data
        assert data["trans"] == u"UT414", data

    def test_UT414_50(self):
        self.add_record(u"UT414", u"UT414")
        rows = cPickle.loads(self.api.gloss("1", query="I have UT414 movies", minscore=".5"))
        assert len(rows) == 1, rows
        data = rows[0]
        assert data["source"] == u"UT414", data
        assert data["trans"] == u"UT414", data

    def test_simple_100_nomatch(self):
        self.add_record("xxx", "yyy")
        rows = cPickle.loads(self.api.gloss("1", query="I have xx movies", minscore="1.0"))
        assert rows == [], rows

    def test_simple_50(self):
        self.add_record("xxx", "yyy")
        rows = cPickle.loads(self.api.gloss("1", query="aaa xx yyy", minscore=".5"))
        assert len(rows) == 1, rows
        data = rows[0]
        assert data["source"] == u"xxx", data
        assert data["trans"] == u"yyy", data

    def test_simple_50_nomatch(self):
        self.add_record("xxx", "yyy")
        rows = cPickle.loads(self.api.gloss("1", query="I have x movies", minscore=".5"))
        assert rows == [], rows

    def test_added_records_100(self):

        self.add_record(u"spam", u"egg")

        rows = cPickle.loads(self.api.gloss("1", query="I have spam", minscore="1"))
        assert len(rows) == 1, rows
        [row] = rows
        assert row["source"] == "spam", row
        assert row["trans"] == "egg", row

    def test_db_plus_added_records_100(self):

        self.add_record("xxx", "yyy")
        self.add_record(u"spam", u"egg")

        rows = cPickle.loads(self.api.gloss("1", query="I have xxx spam", minscore="1"))
        assert len(rows) == 2, rows
        [row2, row1] = rows
        assert row1["source"] == "xxx", rows
        assert row1["trans"] == "yyy", rows
        assert row2["source"] == "spam", rows
        assert row2["trans"] == "egg", rows

    def test_added_records_50(self):

        self.add_record("xxxx", "egg")

        rows = cPickle.loads(self.api.gloss("1", query="I have xx books", minscore=".5"))
        assert len(rows) == 1, rows
        [row] = rows
        assert row["source"] == "xxxx", row
        assert row["trans"] == "egg", row
