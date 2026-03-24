#coding: UTF8

import unittest
import simplejson

import mock
from sqlalchemy.orm import clear_mappers

import fake_cherrypy
from .. import site_records
from .. import model
from .. import dataloader
from .. import cherrybase

class EngineHolder:
    engine = None

def setUpModule():
    site_records.cherrypy = fake_cherrypy.FakeCherryPy()
    EngineHolder.engine = dataloader.get_engine(":memory:")

def tearDownModule():
    clear_mappers()


class SiteRecordsTester(unittest.TestCase):

    def addrecords(self, source, trans):
        records = model.Data.memories[1].mem["records"]

        for source, trans in zip(source.split(), trans.split()):
            record = model.MemoryRecord(source, trans)
            record.id = model.get_next_recid()
            record.memory_id = 1
            records[model.MAKE_KEY(dict(source=source, trans=trans))] = record

        return records.values()


class TestSetMemtype(SiteRecordsTester):
    def test_memory(self):
        mem = model.TranslationMemory(model.mem2d(model.Memory("foo", "m")))
        context = {}
        site_records.set_memtype(mem, context)
        assert context["dirname"] == "memories", context
        assert context["memtype"] == "Memory", context

    def test_glossary(self):
        mem = model.TranslationMemory(model.mem2d(model.Memory("foo", "g")))
        context = {}
        site_records.set_memtype(mem, context)
        assert context["dirname"] == "glossaries", context
        assert context["memtype"] == "Glossary", context

class TestRecordsFakeSession(SiteRecordsTester):
    def setUp(self):
        SiteRecordsTester.setUp(self)
        self.records = site_records.Records()
        cherrybase.cherrypy = site_records.cherrypy = fake_cherrypy.FakeCherryPy()
        model.Data.memories = {}
        mem = model.Memory(u"TestRecords", u"m")
        mem.id = 1
        model.Data.memories[1] = model.TranslationMemory(model.mem2d(mem))
        model.Data.next_id = 1

        record = model.MemoryRecord(u"foo", u"bar")

        record.id = model.get_next_recid()
        record.memory_id = 1
        model.Data.memories[1].add_record(record)

        self.renderer = fake_cherrypy.FakeRenderer()
        site_records.render = self.renderer.render

    def tearDown(self):
        SiteRecordsTester.tearDown(self)
        site_records.cherrypy.session = {}
        cherrybase.cherrypy.session = {}
        model.Data.memories = {}

    def test_view(self):
        self.records.view("1", "1")

        assert self.renderer.page == "records/view.html", self.renderer.page
        assert self.renderer.context["record"].id == 1, self.renderer.context

    def test_edit(self):
        self.records.edit("1", "1")

        assert self.renderer.page == "records/edit.html", self.renderer.page
        assert self.renderer.context["record"].id == 1, self.renderer.context

    def test_add(self):
        self.records.add("1")

        assert self.renderer.page == "records/add.html", self.renderer.page
        assert self.renderer.context["mem_name"] == "TestRecords", self.renderer.context

class TestRecordsDbOneTransPerSource(SiteRecordsTester):
    def setUp(self):
        model.MAKE_KEY = model.make_key_source

        SiteRecordsTester.setUp(self)
        self.records = site_records.Records()
        self.renderer = fake_cherrypy.FakeRenderer()
        site_records.render = self.renderer.render

        mem = model.Memory(u"TestRecords", u"m")
        mem.id = 1
        model.Data.memories = {1 : model.TranslationMemory(model.mem2d(mem)) }


    def tearDown(self):
        model.MAKE_KEY = model.make_key_both

        SiteRecordsTester.tearDown(self)
        model.Data.memories = {}

    def test_submitadd_dupe(self):

        [rec] = self.addrecords("spam", "egg")

        try:
            memid = rec.memory_id
            self.records.submitadd(str(memid), source="spam", trans="bar")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest.startswith("/records/view/1/"), details.dest
        else:
            assert False, "Should have thrown"

        expected = """<div class="success">
                                 Added record
                                 </div>""".split()
        actual = cherrybase.cherrypy.session["msgs"][-1].split()
        for e, a in zip(expected, actual):
            assert e == a, (e, a)

        records = model.Data.memories[1].mem["records"]
        assert len(records) == 1, records


    def test_delete_success_record_gone(self):

        [rec] = self.addrecords("spam", "egg")

        records = model.Data.memories[1].mem["records"]

        assert len(records) == 1, records

        try:
            memid = rec.memory_id
            recid = rec.id
            self.records.delete(str(memid), str(recid), next="spam")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect:
            pass

        assert len(records) == 0, records

class TestRecordsDb(SiteRecordsTester):
    def setUp(self):
        SiteRecordsTester.setUp(self)
        self.records = site_records.Records()
        self.renderer = fake_cherrypy.FakeRenderer()
        site_records.render = self.renderer.render

        mem = model.Memory(u"TestRecords", u"m")
        mem.id = 1
        model.Data.memories = {1 : model.TranslationMemory(model.mem2d(mem)) }

    def tearDown(self):
        SiteRecordsTester.tearDown(self)
        model.Data.memories = {}

    # ===============
    def test_submitadd_success(self):

        [rec] = self.addrecords("spam", "egg")

        try:
            memid = rec.memory_id
            self.records.submitadd(str(memid), source="foo", trans="bar")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest.startswith("/records/view/1/"), details.dest
        else:
            assert False, "Should have thrown"

        expected = """<div class="success">
                                 Added record
                                 </div>""".split()
        actual = cherrybase.cherrypy.session["msgs"][-1].split()
        for e, a in zip(expected, actual):
            assert e == a, (e, a)

    def test_editinplace_record(self):

        [rec] = self.addrecords("spam", "egg")

        memid = rec.memory_id
        recid = rec.id
        data = simplejson.loads(self.records.editinplace(str(memid),
                                        str(recid),
                                        source="foo",
                                        trans="bar"))

        assert data["source"] == u"foo", data
        assert data["trans"] == u"bar", data
        assert data["last_modified"] == str(rec.last_modified), data

    def test_editinplace_message(self):

        [rec] = self.addrecords("spam", "egg")

        memid = rec.memory_id
        recid = rec.id
        data = simplejson.loads(self.records.editinplace(str(memid),
                                        str(recid),
                                        source="foo",
                                        trans="bar"))

        expected = """<div class="success">
                                 Edited record with id %d
                                 </div>""" % recid
        actual = data["message"].splitlines()
        for e, a in zip(expected.splitlines(), actual):
            assert e.strip() == a.strip(), (e.strip(), a.strip())


    def test_submitedit_success(self):

        [rec] = self.addrecords("spam", "egg")

        try:
            memid = rec.memory_id
            recid = rec.id
            self.records.submitedit(str(memid), str(recid), source="foo", trans="bar")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/records/view/1/%s" % rec.id, details.dest
        else:
            assert False, "Should have thrown"

        expected = """<div class="success">
                                 Edited record
                                 </div>""".split()
        actual = cherrybase.cherrypy.session["msgs"][-1].split()
        for e, a in zip(expected, actual):
            assert e == a, (e, a)

    def test_submitedit_todup(self):

        [rec, dup] = self.addrecords("spam foo", "egg bar")

        try:
            memid = rec.memory_id
            recid = rec.id
            self.records.submitedit(str(memid), str(recid), source="foo", trans="bar")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/records/view/1/%s" % rec.id, details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="success">
                                 Edited record
                                 </div>""".split())
        actual = " ".join(cherrybase.cherrypy.session["msgs"][-1].split())
        print "expected:", expected
        print "actual:  ", actual
        assert expected == actual

    def test_delete_success(self):

        [rec] = self.addrecords("spam", "egg")

        try:
            memid = rec.memory_id
            recid = rec.id
            self.records.delete(str(memid), str(recid), next="spam")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "spam", details.dest
        else:
            assert False, "Should have thrown"

        actual = cherrybase.cherrypy.session["msgs"][-1]
        assert "Deleted record" in actual, actual


    def test_delete_success_record_gone(self):

        [rec] = self.addrecords("spam", "egg")

        records = model.Data.memories[1].mem["records"]

        assert len(records) == 1, records

        try:
            memid = rec.memory_id
            recid = rec.id
            self.records.delete(str(memid), str(recid), next="spam")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect:
            pass

        assert len(records) == 0, records

    def test_delete_memory_doesnt_exist(self):

        [rec] = self.addrecords("spam", "egg")

        try:
            self.records.delete(str(rec.memory_id+1), str(rec.id), next="spam")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "spam", details.dest
        else:
            assert False, "Should have thrown"

        actual = cherrybase.cherrypy.session["msgs"][-1]
        assert "Memory/Glossary not found" in actual, actual

    def test_delete_record_doesnt_exist(self):

        [rec] = self.addrecords("spam", "egg")

        try:
            self.records.delete(str(rec.memory_id), str(rec.id+1), next="spam")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "spam", details.dest
        else:
            assert False, "Should have thrown"

        actual = cherrybase.cherrypy.session["msgs"][-1]
        assert "Record not found" in actual, actual