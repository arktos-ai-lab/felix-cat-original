#encoding: UTF8
#!/usr/bin/env python

import unittest
import datetime
import cStringIO as StringIO

from lxml import objectify
import cherrypy
from nose.tools import raises

import utils
import fake_cherrypy
from .. import main
from .. import globalsearch as gs
from .. import model
from .. import cherrybase

from .. import settings


class TestGlobalSearch(unittest.TestCase):
    def setUp(self):
        cherrybase.cherrypy = gs.cherrypy = fake_cherrypy.FakeCherryPy()

        self.repo = gs.GlobalSearch()

        self.renderer = fake_cherrypy.FakeRenderer()
        self.old_render = gs.render
        gs.render = self.renderer.render

        mem = model.Memory(u"test", u"m")
        mem.id = 1
        self.mem = model.TranslationMemory(model.mem2d(mem))
        assert self.mem.mem["id"] == 1, self.mem.mem
        model.Data.memories[1] = self.mem

    def tearDown(self):
        gs.cherrypy.session = {}
        cherrybase.cherrypy.session = {}
        gs.render = self.old_render

    def add_record(self, source, trans, **kwds):
        rec = model.Record(source, trans, **kwds)
        if "last_modified" not in kwds:
            rec.last_modified=datetime.datetime.now()
        mem = model.Data.memories[1]
        rec.memory_id = mem.mem["id"]
        mem.add_record(rec)
        return rec

    def test_searchdownload_empty(self):
        gs.render = self.old_render
        content = self.repo.download(["does not exist"])

        headers = gs.cherrypy.response.headers
        assert headers['Content-Type'] == 'application/xml', headers
        assert headers['Content-Length'] == len(content), headers

        tree = objectify.parse(StringIO.StringIO(content))
        root = tree.getroot()

        mem = model.Data.memories[1].mem
        assert root.head.creator.text == u"Ryan-PC", root.head.creator.text
        assert root.head.created_on.text == str(mem["created_on"]), root.head.created_on.text
        assert root.head.creation_tool.text == u"MemoryServes", root.head.creation_tool.text
        assert root.head.creation_tool_version.text == model.VERSION, root.head.creation_tool_version.text
        assert root.head.num_records.text == u"0", root.head.num_records.text
        assert root.head.locked.text == u"false", root.head.locked.text
        assert root.head.is_memory.text == u"true", root.head.is_memory.text
        print dir(root.records)
        assert root.records.getchildren() == [], root.records


    def test_search_download_two_records_one_match(self):
        gs.render = self.old_render

        rec1 = self.add_record(u"xxx", u"yyy")
        rec2 = self.add_record(u"aaa", u"bbb")
        rec2.id = 2

        content = self.repo.download(["xxx"])

        headers = gs.cherrypy.response.headers
        assert headers['Content-Type'] == 'application/xml', headers
        assert headers['Content-Length'] == len(content), headers

        tree = objectify.parse(StringIO.StringIO(content))
        root = tree.getroot()

        assert root.head.creator.text == u"Ryan-PC", root.head.creator.text
        assert len(root.records) == 1, root.records


    def test_search_help(self):

        self.repo.search_help()

        assert self.renderer.page == "search/help.html", self.renderer.page

    ##############
    # index
    ##############

    def test_mem_missing(self):
        record = self.add_record(u"spam", u"egg")
        record.memory_id = 100
        self.repo.index("1", "source:spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    # source
    def test_source_yes(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.index("1", "source:spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_source_yes_3_words(self):
        record = self.add_record(u"spam and eggs", u"egg")
        self.repo.index("1", "source:spam and eggs")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_source_no(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.index("1", "source:egg")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # trans
    def test_trans_yes(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.index("1", "trans:egg")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_trans_no(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.index("1", "trans:spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # context
    def test_context_yes(self):
        record = self.add_record(u"spam", u"egg", context=u"I heart foo baby!")
        self.repo.index("1", "context:foo")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.context == record.context, (actual, record)

    def test_context_no(self):
        record = self.add_record(u"spam", u"egg", context=u"I heart bar baby!")
        self.repo.index("1", "context:spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # created-by
    def test_created_by_yes(self):
        record = self.add_record(u"spam", u"egg", created_by=u"I heart foo baby!")
        self.repo.index("1", "created-by:foo")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.created_by == record.created_by, (actual, record)

    def test_created_by_no(self):
        record = self.add_record(u"spam", u"egg", created_by=u"I heart bar baby!")
        self.repo.index("1", "created-by:spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.created-by

    # created-before
    def test_created_before_yes(self):
        record1 = self.add_record(u"spam", u"egg", date_created=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", date_created=datetime.datetime(2009, 1, 1))
        self.repo.index("1", "created-before:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.date_created == record1.date_created, (actual, record1)

    def test_created_before_yes_slashes(self):
        record1 = self.add_record(u"spam", u"egg", date_created=datetime.datetime(2007, 1, 1))
        self.repo.index("1", "created-before:2008/10/1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.date_created == record1.date_created, (actual, record1)

    def test_created_before_no(self):
        self.add_record(u"foo", u"bar", date_created=datetime.datetime(2009, 1, 1))
        self.repo.index("1", "created-before:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # created-after
    def test_created_after_yes(self):
        record1 = self.add_record(u"spam", u"egg", date_created=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", date_created=datetime.datetime(2009, 1, 1))
        self.repo.index("1", "created-after:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record2.source, (actual, record2)
        assert actual.trans == record2.trans, (actual, record2)
        assert actual.date_created == record2.date_created, (actual, record2)

    def test_created_after_no(self):
        self.add_record(u"foo", u"bar", date_created=datetime.datetime(2007, 1, 1))
        self.repo.index("1", "created-after:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # modified-by
    def test_modified_by_yes(self):
        record = self.add_record(u"spam", u"egg", modified_by=u"I heart foo baby!")
        self.repo.index("1", "modified-by:foo")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.modified_by == record.modified_by, (actual, record)

    def test_modified_by_no(self):
        record = self.add_record(u"spam", u"egg", modified_by=u"I heart bar baby!")
        self.repo.index("1", "modified-by:spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.modified-by

    # modified-before
    def test_modified_before_yes(self):
        record1 = self.add_record(u"spam", u"egg", last_modified=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2009, 1, 1))
        self.repo.index("1", "modified-before:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.last_modified == record1.last_modified, (actual, record1)

    def test_modified_before_yes_slashes(self):
        record1 = self.add_record(u"spam", u"egg", last_modified=datetime.datetime(2007, 1, 1))
        self.repo.index("1", "modified-before:2008/10/1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.last_modified == record1.last_modified, (actual, record1)

    def test_modified_before_no(self):
        self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2009, 1, 1))
        self.repo.index("1", "modified-before:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # modified-after
    def test_modified_after_yes(self):
        record1 = self.add_record(u"spam", u"egg", last_modified=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2009, 1, 1))
        self.repo.index("1", "modified-after:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record2.source, (actual, record2)
        assert actual.trans == record2.trans, (actual, record2)
        assert actual.last_modified == record2.last_modified, (actual, record2)

    def test_modified_after_no(self):
        rec = self.add_record(u"foo", u"bar")
        rec.last_modified = datetime.datetime(2007, 1, 1)
        self.repo.index("1", "modified-after:2008-10-1")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability
    def test_reliability_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.index("1", "reliability:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_no(self):
        record = self.add_record(u"spam", u"egg", reliability=1)
        self.repo.index("1", "reliability:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-gt
    def test_reliability_gt_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=5)
        self.repo.index("1", "reliability-gt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_gt_no(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.index("1", "reliability-gt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-gte
    def test_reliability_gte_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=5)
        self.repo.index("1", "reliability-gte:5")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_gte_no(self):
        record = self.add_record(u"spam", u"egg", reliability=3)
        self.repo.index("1", "reliability-gte:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-lt
    def test_reliability_lt_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=3)
        self.repo.index("1", "reliability-lt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_lt_no(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.index("1", "reliability-lt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-lte
    def test_reliability_lte_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.index("1", "reliability-lte:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_lte_no(self):
        record = self.add_record(u"spam", u"egg", reliability=5)
        self.repo.index("1", "reliability-lte:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # validated
    def test_validated_true_yes(self):
        record = self.add_record(u"spam", u"egg", validated=True)
        self.repo.index("1", "validated:true")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.validated == record.validated, (actual, record)

    def test_validated_true_no(self):
        record = self.add_record(u"spam", u"egg", validated=False)
        self.repo.index("1", "validated:true")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_validated_false_yes(self):
        record = self.add_record(u"spam", u"egg", validated=False)
        self.repo.index("1", "validated:false")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.validated == record.validated, (actual, record)

    def test_validated_false_no(self):
        record = self.add_record(u"spam", u"egg", validated=True)
        self.repo.index("1", "validated:false")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context["records"]

    # refcount
    def test_refcount_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.index("1", "refcount:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=1)
        self.repo.index("1", "refcount:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-gt
    def test_refcount_gt_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=5)
        self.repo.index("1", "refcount-gt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_gt_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.index("1", "refcount-gt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-gte
    def test_refcount_gte_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=5)
        self.repo.index("1", "refcount-gte:5")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_gte_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=3)
        self.repo.index("1", "refcount-gte:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-lt
    def test_refcount_lt_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=3)
        self.repo.index("1", "refcount-lt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_lt_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.index("1", "refcount-lt:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-lte
    def test_refcount_lte_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.index("1", "refcount-lte:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_lte_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=5)
        self.repo.index("1", "refcount-lte:4")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_source_and_trans(self):
        record = self.add_record(u"spam", u"egg")
        fake1 = self.add_record(u"foo", u"egg")
        fake2 = self.add_record(u"spam", u"bar")
        self.repo.index("1", "source:spam", queryfilters=["trans:egg"])

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_no_matches(self):

        self.repo.index("1", "spam", ["egg"])

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_string_qf_to_list(self):
        self.repo.index("1", "spam", "egg")

        queryfilters = self.renderer.context["queryfilters"]
        expected = [{'removelink': u'?queryfilters=spam', 'term': u'egg'}, {'removelink': u'?queryfilters=egg', 'term': u'spam'}]
        assert queryfilters == expected, queryfilters
        assert isinstance(queryfilters[0], dict), queryfilters

    def test_1_match_string_qf(self):
        record = self.add_record(u"spam", u"egg")

        self.repo.index("1", "spam", ["egg"])

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_one_match_list_queryfilter(self):
        record = self.add_record(u"spam foo", u"egg")

        self.repo.index("1", "spam", "foo egg".split())

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_both(self):
        record = self.add_record(u"spam", u"egg")

        self.repo.index("1", "spam", ["egg"])

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_no_queryfilter(self):
        record = self.add_record(u"spam", u"egg")

        self.repo.index("1", "spam")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_japanese_no_queryfilter(self):
        record = self.add_record(u"日本語", u"英語")

        self.repo.index("1", "日本語")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_japanese(self):
        record = self.add_record(u"日本語", u"英語")

        self.repo.index(page="1", tofind="日本語", queryfilters=["英語"])

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_empty_string(self):
        self.add_record(u"spam", u"egg")
        self.repo.index("1", "")

        assert self.renderer.page == "search/globalsearch.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context


    def test_replace(self):
        self.repo.replace("1")

        assert self.renderer.page == "search/globalreplace.html", self.renderer.page
        context = self.renderer.context
        assert context["replacefrom"] == u"", context

    def test_replace_queryfilters(self):
        self.repo.replace(["foo"])

        assert self.renderer.page == "search/globalreplace.html", self.renderer.page
        context = self.renderer.context
        assert context["queryfilters"] == [{'removelink': u'', 'term': u'foo'}], context["queryfilters"]

    def test_replace_find(self):
        records = model.Data.memories[1].mem["records"]
        key1 = model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))
        records[key1] = model.MemoryRecord(source=u"foo",
                                         trans=u"bar",
                                         id=1)
        self.repo.replace_find("source:*", "XXX")

        assert self.renderer.page == "search/globalreplace.html", self.renderer.page
        context = self.renderer.context

        assert context["result"].source == u"XXX", context["result"].source
        assert context["result"].trans == u"bar", context["result"].trans
        assert context["result"].source_cmp == u"xxx", context["result"].source_cmp
        assert context["result"].id == 1, context["result"].id

        assert context["found"] == records[key1], context["found"]

    def test_replace_find_with_queryfilters(self):
        records = model.Data.memories[1].mem["records"]
        key = model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))
        records[key] = model.MemoryRecord(source=u"foo",
                                         trans=u"bar",
                                         id=1)
        key2 = model.MAKE_KEY(dict(source=u"foo", trans=u"spam"))
        records[key2] = model.MemoryRecord(source=u"foo",
                                         trans=u"spam",
                                         id=2)
        self.repo.replace_find("source:*", "XXX", queryfilters=["trans:spam"])

        assert self.renderer.page == "search/globalreplace.html", self.renderer.page
        context = self.renderer.context

        assert context["result"].source == u"XXX", context["result"].source
        assert context["result"].trans == u"spam", context["result"].trans
        assert context["result"].source_cmp == u"xxx", context["result"].source_cmp
        assert context["result"].id == 2, context["result"].id

        assert context["found"] == records[key2], context["found"]

    def test_replace_replace(self):
        rec1 = self.add_record(u"foo", u"bar")
        rec2 = self.add_record(u"spam", u"egg")
        rec2.id = 3

        self.repo.replace_replace("source:*", "XXX", nth_item="3")

        assert self.renderer.page == "search/globalreplace.html", self.renderer.page
        mem = model.Data.memories[1]
        found = mem.mem["records"][(u"XXX", u"egg")]
        assert len(mem.mem["records"]) == 2, records

        assert found.source == u"XXX", found
        assert found.trans == u"egg", found

    def test_replace_replace_to_dup(self):
        self.add_record(u"XXX", u"bar")
        rec2 = self.add_record(u"spam", u"bar")
        rec2.id = 3

        self.repo.replace_replace("source:*", "XXX", nth_item="3")

        assert self.renderer.page == "search/globalreplace.html", self.renderer.page
        mem = model.Data.memories[1]
        found = mem.mem["records"][(u"XXX", u"bar")]
        assert len(mem.mem["records"]) == 1, records

        assert found.source == u"XXX", found
        assert found.trans == u"bar", found

        message = self.renderer.context["msg"]
        assert "There was another record with the" in message, message

    def test_replace_replace_not_found(self):
        self.add_record(u"foo", u"bar")
        self.add_record(u"spam", u"egg")

        try:
            self.repo.replace_replace("source:does_not_exist", "XXX", nth_item="3")
        except Exception, details:
            assert details.dest == "/globalsearch/replace/", details
        else:
            assert False, "Should have redirected when not found"

    def test_replace_all(self):
        self.add_record(u"foo", u"bar")
        rec2 = self.add_record(u"spam", u"egg")
        rec2.id = 3

        try:
            self.repo.replace_all("source:*", "XXX")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/globalsearch/replace/", details.dest
        else:
            assert False, "Should have thrown"

        records = model.Data.memories[1].mem["records"]

        assert len(records) == 2, records
        rec1 = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"bar"))]
        rec2 = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"egg"))]

        assert rec1.source == u"XXX", rec1
        assert rec2.source == u"XXX", rec2

        assert rec1.trans == u"bar", rec1
        assert rec2.trans == u"egg", rec2

    def test_replace_all_no_mem(self):
        self.add_record(u"foo", u"bar")
        rec2 = self.add_record(u"spam", u"egg")
        rec2.memory_id = 100

        try:
            self.repo.replace_all("source:*", "XXX")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/globalsearch/replace/", details.dest
        else:
            assert False, "Should have thrown"

        records = model.Data.memories[1].mem["records"]

        assert len(records) == 2, records
        rec1 = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"bar"))]
        rec2 = records[model.MAKE_KEY(dict(source=u"spam", trans=u"egg"))]

        assert rec1.source == u"XXX", rec1
        assert rec2.source == u"spam", rec2

        assert rec1.trans == u"bar", rec1
        assert rec2.trans == u"egg", rec2

    def test_replace_all_with_queryfilters(self):
        rec1 = self.add_record(u"foo", u"bar")
        rec2 = self.add_record(u"foo", u"spam")
        rec2.id = 2

        try:
            self.repo.replace_all("source:*", "XXX", queryfilters=["trans:spam"])
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/globalsearch/replace/", details.dest
        else:
            assert False, "Should have thrown"

        records = model.Data.memories[1].mem["records"]

        rec1 = records[model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))]
        rec2 = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"spam"))]

        assert rec1.source == u"foo", rec1
        assert rec2.source == u"XXX", rec2

        assert rec1.trans == u"bar", rec1
        assert rec2.trans == u"spam", rec2


    def test_replace_all_delete(self):
        records = model.Data.memories[1].mem["records"]
        self.add_record(u"foo", u"bar")
        self.add_record(u"foo", u"spam")

        try:
            self.repo.replace_all("source:foo", "action:delete")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/globalsearch/replace/", details.dest
        else:
            assert False, "Should have thrown"

        assert len(records) == 0, records

    def test_replace_all_delete_no_mem(self):
        records = model.Data.memories[1].mem["records"]
        self.add_record(u"foo", u"bar")
        rec2 = self.add_record(u"foo", u"spam")
        rec2.memory_id = 100

        try:
            self.repo.replace_all("source:foo", "action:delete")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/globalsearch/replace/", details.dest
        else:
            assert False, "Should have thrown"

        assert len(records) == 1, records