#coding: UTF8
"""
Unit tests for the `repository` module

"""

import unittest
import datetime
import cStringIO as StringIO
import logging

from nose.tools import raises
from lxml import objectify

import fake_cherrypy
from fake_cherrypy import FakeSqlAlchemySession as FakeSession
import utils
from .. import main
from .. import model
from .. import search
from .. import cherrybase
from .. import presentation
from .. import settings
from .. import loc
from .. import repository
from data import GLOSS_1

repository.logger.setLevel(logging.DEBUG)

MEM_1 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by Felix v 1.2 -->
<memory>
    <head>
        <creator>Owner</creator>
        <created_on>2006/02/07 07:26:15</created_on>
        <creation_tool>Felix</creation_tool>
        <creation_tool_version>1.2</creation_tool_version>
        <num_records>1</num_records>
        <locked>false</locked>
        <is_memory>true</is_memory>
    </head>
    <records>
        <record>
            <id>11</id>
            <source><![CDATA[source 1]]></source>
            <trans><![CDATA[trans 1]]></trans>
            <date_created>2006/02/07 09:34:49</date_created>
            <last_modified>2006/02/07 09:34:49</last_modified>
            <reliability>0</reliability>
            <validated>false</validated>
            <ref_count>0</ref_count>
        </record>
    </records>
</memory>"""

MEM_2 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by Felix v 1.2 -->
<memory>
    <head>
        <creator>Owner</creator>
        <created_on>2006/02/07 07:26:15</created_on>
        <creation_tool>Felix</creation_tool>
        <creation_tool_version>1.2</creation_tool_version>
        <num_records>1</num_records>
        <locked>false</locked>
        <is_memory>true</is_memory>
    </head>
    <records>
        <record>
            <source><![CDATA[source 2]]></source>
            <trans><![CDATA[trans 2]]></trans>
            <date_created>2006/02/07 09:34:49</date_created>
            <last_modified>2006/02/07 09:34:49</last_modified>
            <reliability>0</reliability>
            <validated>false</validated>
            <ref_count>0</ref_count>
        </record>
    </records>
</memory>"""

MEM_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by Felix v 1.2 -->
<memory>
    <head>
        <creator>Owner</creator>
        <created_on>2006/02/07 07:26:15</created_on>
        <creation_tool>Felix</creation_tool>
        <creation_tool_version>1.2</creation_tool_version>
        <num_records>0</num_records>
        <locked>false</locked>
        <is_memory>true</is_memory>
    </head>
    <records>
    </records>
</memory>"""

class Source:
    def __init__(self, name, text):
        self.filename = name
        self.file = StringIO.StringIO(text)

class TestRepository(unittest.TestCase):
    def setUp(self):
        model.Data.memories = {}
        model.Data.next_id = 1

    def test_add_gloss1(self):
        source = Source("spam.xml", GLOSS_1)
        repo = repository.Repository(u"memory")
        repo.add_repo(source)
        # 10 records plus the memory
        assert len(model.Data.memories[1].mem["records"]) == 10, len(model.Data.memories[1].mem["records"])

    def test_add_mem1(self):
        text = MEM_1

        source = Source("egg.xml", text)
        repo = repository.Repository(u"memory")
        repo.add_repo(source)

        records = model.Data.memories[1].mem["records"]
        assert len(records) == 1, records
        record = records.values()[0]
        assert record.id == 1, record




class TestSetIsMemory(unittest.TestCase):
    def test_mem(self):
        item = model.TranslationMemory(dict(memtype=u"m", records={}))
        context = {}
        repository.set_is_memory(item, context)
        assert context["is_memory"] == "true", context

    def test_gloss(self):
        item = model.TranslationMemory(dict(memtype=u"g", records={}))
        context = {}
        repository.set_is_memory(item, context)
        assert context["is_memory"] == "false", context


class TestCreateDownloadFile(unittest.TestCase):
    def setUp(self):

        mem = model.Memory(u"TestCreateDownloadFile", u"m")
        mem.id = 1
        mem.records = []
        self.mem = model.TranslationMemory(model.mem2d(mem))

        repository.cherrypy.session = {}

    def test_empty(self):
        text = repository.create_download_file(self.mem)
        context = dict(version=model.VERSION,
                       created_on=self.mem.mem["created_on"])

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by MemoryServes v %(version)s -->
<memory>
<head>
<creator>Ryan</creator>
<created_on>%(created_on)s</created_on>
<creation_tool>MemoryServes</creation_tool>
<creation_tool_version>%(version)s</creation_tool_version>
<num_records>0</num_records>
<locked>false</locked>
<is_memory>true</is_memory>
</head>
<records>
</records>
</memory>

""" % context

        for a, e in zip(text.splitlines(), expected.splitlines()):
            assert a == e, (a, e)

    def test_one_record(self):
        source = u"English"
        trans = u"日本語"
        key = (source, trans)
        mem = self.mem.mem
        mem["records"][key] = model.MemoryRecord(source=source,
                                    trans=trans,
                                    id=1,
                                    context=u"日本語",
                                    date_created=mem["created_on"],
                                    last_modified=mem["created_on"],
                                    reliability=5,
                                    validated=True,
                                    ref_count=10
                                    )
        context = dict(version=model.VERSION,
                       created_on=mem["created_on"],
                       rec_date=mem["created_on"].strftime("%Y/%m/%d %H:%M:%S"))

        text = repository.create_download_file(self.mem)

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by MemoryServes v %(version)s -->
<memory>
<head>
<creator>Ryan</creator>
<created_on>%(created_on)s</created_on>
<creation_tool>MemoryServes</creation_tool>
<creation_tool_version>%(version)s</creation_tool_version>
<num_records>1</num_records>
<locked>false</locked>
<is_memory>true</is_memory>
</head>
<records>
    <record>
        <id>1</id>
        <source><![CDATA[English]]></source>
        <trans><![CDATA[日本語]]></trans>
        <context><![CDATA[日本語]]></context>
        <date_created>%(rec_date)s</date_created>
        <last_modified>%(rec_date)s</last_modified>
        <reliability>5</reliability>
        <validated>true</validated>
        <ref_count>10</ref_count>
    </record>
</records>
</memory>

""" % context

        for a, e in zip(text.splitlines(), expected.splitlines()):
            assert a == e, (a.decode("utf-8"), e.decode("utf-8"))

    def test_string_true(self):
        source = u"English"
        trans = u"日本語"
        key = (source, trans)
        mem = self.mem.mem
        self.mem.mem["records"][key] = model.MemoryRecord(source=source,
                                        trans=trans,
                                        id=1,
                                        context=u"日本語",
                                        date_created=mem["created_on"],
                                        last_modified=mem["created_on"],
                                        reliability=5,
                                        validated="False",
                                        ref_count=10
                                        )
        context = dict(version=model.VERSION,
                       created_on=mem["created_on"],
                       rec_date=mem["created_on"].strftime("%Y/%m/%d %H:%M:%S"))

        text = repository.create_download_file(self.mem)

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by MemoryServes v %(version)s -->
<memory>
<head>
<creator>Ryan</creator>
<created_on>%(created_on)s</created_on>
<creation_tool>MemoryServes</creation_tool>
<creation_tool_version>%(version)s</creation_tool_version>
<num_records>1</num_records>
<locked>false</locked>
<is_memory>true</is_memory>
</head>
<records>
    <record>
        <id>1</id>
        <source><![CDATA[English]]></source>
        <trans><![CDATA[日本語]]></trans>
        <context><![CDATA[日本語]]></context>
        <date_created>%(rec_date)s</date_created>
        <last_modified>%(rec_date)s</last_modified>
        <reliability>5</reliability>
        <validated>false</validated>
        <ref_count>10</ref_count>
    </record>
</records>
</memory>

""" % context

        for a, e in zip(text.splitlines(), expected.splitlines()):
            assert a == e, (a.decode("utf-8"), e.decode("utf-8"))


    def test_string_date(self):
        source = u"English"
        trans = u"日本語"
        key = (source, trans)
        mem = self.mem.mem
        mem["records"][key] = model.MemoryRecord(source=source,
                                        trans=trans,
                                        id=1,
                                        context=u"日本語",
                                        date_created="2009/01/01 01:01:01",
                                        last_modified=u"2009/02/02 02:02:02",
                                        reliability=5,
                                        validated=True,
                                        ref_count=10
                                        )
        context = dict(version=model.VERSION,
                       created_on=mem["created_on"])

        text = repository.create_download_file(self.mem)

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by MemoryServes v %(version)s -->
<memory>
<head>
<creator>Ryan</creator>
<created_on>%(created_on)s</created_on>
<creation_tool>MemoryServes</creation_tool>
<creation_tool_version>%(version)s</creation_tool_version>
<num_records>1</num_records>
<locked>false</locked>
<is_memory>true</is_memory>
</head>
<records>
    <record>
        <id>1</id>
        <source><![CDATA[English]]></source>
        <trans><![CDATA[日本語]]></trans>
        <context><![CDATA[日本語]]></context>
        <date_created>2009/01/01 01:01:01</date_created>
        <last_modified>2009/02/02 02:02:02</last_modified>
        <reliability>5</reliability>
        <validated>true</validated>
        <ref_count>10</ref_count>
    </record>
</records>
</memory>

""" % context

        for a, e in zip(text.splitlines(), expected.splitlines()):
            assert a == e, (a.decode("utf-8"), e.decode("utf-8"))


    def test_empty_gloss(self):
        self.mem.mem["memtype"] = u"g"
        text = repository.create_download_file(self.mem)
        context = dict(version=model.VERSION,
                       created_on=self.mem.mem["created_on"])

        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by MemoryServes v %(version)s -->
<memory>
<head>
<creator>Ryan</creator>
<created_on>%(created_on)s</created_on>
<creation_tool>MemoryServes</creation_tool>
<creation_tool_version>%(version)s</creation_tool_version>
<num_records>0</num_records>
<locked>false</locked>
<is_memory>false</is_memory>
</head>
<records>
</records>
</memory>

""" % context

        for a, e in zip(text.splitlines(), expected.splitlines()):
            assert a == e, (a, e)


class TestCreateMemoryConfig1(unittest.TestCase):
    def setUp(self):
        repo = repository.Repository(u"memory")
        repo.session = FakeSession()
        data = dict(creator=u"spam",
                  normalize_case=True,
                  normalize_hira=True,
                  normalize_width=True,
                  created_on=u"2008/01/01 01:01:01",
                  source_language="Japanese",
                  target_language="English",
                  spammy_param=u"beans beans spam and egg")
        self.mem = repo.create_memory("foo.xml", data)

    def test_normalize_case(self):
        assert self.mem.mem["normalize_case"], self.mem.mem
    def test_normalize_hira(self):
        assert self.mem.mem["normalize_hira"], self.mem.mem
    def test_normalize_width(self):
        assert self.mem.mem["normalize_width"], self.mem.mem
    def test_creator(self):
        assert self.mem.mem["creator"] == u"spam", self.mem.mem
    def test_created_on(self):

        t = self.mem.mem["created_on"]

        assert t.year == 2008, t
        assert t.month == 1, t
        assert t.day == 1, t
        assert t.hour == 1, t
        assert t.minute == 1, t
        assert t.second == 1, t

    def test_source_language(self):
        assert self.mem.mem["source_language"] == u"Japanese", self.mem.mem
    def test_target_language(self):
        assert self.mem.mem["target_language"] == u"English", self.mem.mem
    def test_memtype(self):
        assert self.mem.mem["memtype"] == u"m", self.mem.mem

class TestCreateMemoryConfig2(unittest.TestCase):
    def setUp(self):
        repo = repository.Repository(u"glossary")
        repo.session = FakeSession()
        data = dict(creator=u"parrot",
                  normalize_case=False,
                  normalize_hira=False,
                  normalize_width=False,
                  source_language="Danish",
                  target_language="Welsh",
                  notes=u"this is a note",
                  spammy_param=u"nailed to the perch")
        self.mem = repo.create_memory("foo.xml", data)

    def test_normalize_case(self):
        assert not self.mem.mem["normalize_case"], self.mem
    def test_normalize_hira(self):
        assert not self.mem.mem["normalize_hira"], self.mem
    def test_normalize_width(self):
        assert not self.mem.mem["normalize_width"], self.mem
    def test_creator(self):
        assert self.mem.mem["creator"] == u"parrot", self.mem
    def test_created_on(self):
        assert str(self.mem.mem["created_on"]).startswith("201"), self.mem
    def test_source_language(self):
        assert self.mem.mem["source_language"] == u"Danish", self.mem
    def test_target_language(self):
        assert self.mem.mem["target_language"] == u"Welsh", self.mem
    def test_memtype(self):
        assert self.mem.mem["memtype"] == u"g", self.mem


class RepoTester(unittest.TestCase):

    def setUp(self):
        cherrybase.cherrypy = repository.cherrypy = fake_cherrypy.FakeCherryPy()
        self.repo = self.classtype()
        self.renderer = fake_cherrypy.FakeRenderer()
        self.old_render = repository.render
        repository.render = self.renderer.render

        self.mem = utils.init_db(u"RepoTester", self.memtype)

    def tearDown(self):
        repository.cherrypy.session = {}
        cherrybase.cherrypy.session = {}
        repository.render = self.old_render

    def adduser(self, name, password, confirm, role=u"user"):
        user = model.User(name, password, confirm, role)
        userid = model.get_next_userid()
        user.id = userid
        model.Data.users[userid] = model.user2d(user)
        return model.Data.users[userid]

    def add_record(self, source, trans, **kwds):
        rec = model.MemoryRecord(source, trans, **kwds)
        if "last_modified" not in kwds:
            rec.last_modified=datetime.datetime.now()
        mem = model.Data.memories[1]
        rec.memory_id = mem.mem["id"]
        mem.add_record(rec)
        return rec


class TestMerge(RepoTester):
    memtype = u"m"
    classtype = repository.Memories

    def test_has_privs(self):
        self.repo.merge("1")
        assert self.renderer.page == "merge.html", self.renderer.page

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_memory_missing(self):
        self.repo.merge("11")

class TestMemories(RepoTester):
    memtype = u"m"
    classtype = repository.Memories

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_edit_not_admin(self):
        self.repo.edit("1")

    def test_searchdownload_empty(self):
        repository.render = self.old_render
        content = self.repo.searchdownload("1", ["does not exist"])

        headers = repository.cherrypy.response.headers
        assert headers['Content-Type'] == 'application/xml', headers
        assert headers['Content-Length'] == len(content), headers

        print content
        tree = objectify.parse(StringIO.StringIO(content))
        root = tree.getroot()

        mem = model.Data.memories[1].mem
        assert root.head.creator.text == u"Ryan-PC", root.head.creator.text
        assert root.head.creation_tool.text == u"MemoryServes", root.head.creation_tool.text
        assert root.head.creation_tool_version.text == model.VERSION, root.head.creation_tool_version.text
        assert root.head.num_records.text == u"0", root.head.num_records.text
        assert root.head.locked.text == u"false", root.head.locked.text
        assert root.head.is_memory.text == u"true", root.head.is_memory.text
        assert root.records.getchildren() == [], root.records


    def test_searchdownload_two_records_one_match(self):
        repository.render = self.old_render

        records = model.Data.memories[1].mem["records"]
        records[model.MAKE_KEY(dict(source=u"xxx", trans=u"uuu"))] = model.MemoryRecord(source=u"xxx",
                                         trans=u"yyy",
                                         id=1)
        records[model.MAKE_KEY(dict(source=u"aaa", trans=u"bbb"))] = model.MemoryRecord(source=u"aaa",
                                         trans=u"bbb",
                                         id=2)

        content = self.repo.searchdownload("1", ["xxx"])

        headers = repository.cherrypy.response.headers
        assert headers['Content-Type'] == 'application/xml', headers
        assert headers['Content-Length'] == len(content), headers

        tree = objectify.parse(StringIO.StringIO(content))
        root = tree.getroot()

        assert root.head.creator.text == u"Ryan-PC", root.head.creator.text
        assert len(root.records) == 1, root.records


    def test_edit(self):
        adminuser = self.adduser(u"George", u"admin", u"secret")
        cherrybase.cherrypy.session["user"] = adminuser

        self.repo.edit("1")

        del cherrybase.cherrypy.session["user"]
        assert self.renderer.page == "edit_repo.html", self.renderer.page

    def test_browse(self):

        self.repo.browse("1", "1")

        assert self.renderer.page == "browse.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_browse_with_records(self):
        mem = model.Data.memories[1].mem
        rec1 = model.MemoryRecord(u"foo", u"bar")
        mem["records"][(rec1.source, rec1.trans)] = rec1

        self.repo.browse("1", "1")
        assert self.renderer.page == "browse.html", self.renderer.page
        assert self.renderer.context["records"] == [rec1], self.renderer.context

    def test_search_with_records(self):
        mem = model.Data.memories[1].mem
        rec1 = model.MemoryRecord(u"foo", u"bar")
        mem["records"][(rec1.source, rec1.trans)] = rec1

        self.repo.search("1", "1", "foo")
        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [rec1], self.renderer.context

    def test_view(self):

        self.repo.view("1")

        assert self.renderer.page == "view.html", self.renderer.page

    def test_view_doesnt_exist(self):

        try:
            self.repo.view("2")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/", details.dest
        else:
            assert False, "Should have thrown"

        message = repository.cherrypy.session["msgs"][0]
        assert "Memory with id 2 not found" in message, message
        assert '<div class="ui-state-error ui-corner-all"' in message, message

    def test_index(self):

        self.repo.index()

        assert self.renderer.page == "memories/index.html", self.renderer.page

    def test_create(self):

        self.repo.create()

        assert self.renderer.page == "create_repo.html", self.renderer.page

    def test_delete_not_admin(self):
        try:
            self.repo.delete("1")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/view/1", details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 You must be an admin to delete memories.
                                 </div>""".split())
        actual = " ".join(repository.cherrypy.session["msgs"][0].split())
        assert expected == actual, (expected, actual)

    def test_delete(self):
        adminuser = self.adduser(u"George", u"admin", u"secret")
        cherrybase.cherrypy.session["user"] = adminuser

        try:
            self.repo.delete("1")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/", details.dest
        else:
            assert False, "Should have thrown"

        log = model.Data.log[-1]
        assert log["message"] == "Deleted memory RepoTester", log
        assert log["severity"] == "info", log
        assert log["user"] == "George", log

        expected = " ".join("""<div class="success">
                                 Deleted memory RepoTester (id: 1)
                                 </div>""".split())
        actual = " ".join(repository.cherrypy.session["msgs"][0].split())
        assert expected == actual, (expected, actual)

    def test_submittmx_default(self):

        self.repo.submittmx(str(self.mem.id), "Default", "Japanese")
        assert self.renderer.page == "download_tmx.html", self.renderer.page

    def test_submittmx(self):

        self.repo.submittmx(str(self.mem.id), "English", "Japanese")

        headers = repository.cherrypy.response.headers
        assert headers['filename'] == 'application/xml', headers
        disp =  'attachment; filename=RepoTester.tmx'
        assert headers['Content-Disposition'] == disp, headers


    def test_submitedit(self):

        try:
            self.repo.submitedit(str(self.mem.id), name=u"FRANK", creator="GOD")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/view/%s" % self.mem.id, details.dest
        else:
            assert False, "Should have thrown"

        cherrybase.cherrypy.session = {}

        mem = model.Data.memories[1].mem
        assert mem["name"] == u"FRANK", mem
        assert mem["creator"] == u"GOD", mem


    def test_submitcreate(self):

        info = dict(name=u"SUBMITCREATE",
                 client=u"TEST",
                 source_language=u"SOURCE_TEST",
                 target_language=u"TARGET_TEST",
                 notes=u"NOTES")

        model.Data.memories[500] = {}

        try:
            self.repo.submitcreate(**info)
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/view/501", details.dest
        else:
            assert False, "Should have thrown"

        assert 501 in model.Data.memories, model.Data.memories.keys()

        expected = " ".join("""<div class="success">
                                 Created memory SUBMITCREATE
                                 </div>""".split())
        actual = " ".join(repository.cherrypy.session["msgs"][0].split())
        assert expected == actual, (expected, actual)

        cherrybase.cherrypy.session = {}

        mem = model.Data.memories[501].mem
        assert mem["name"] == u"SUBMITCREATE", mem
        assert mem["client"] == u"TEST", mem
        assert mem["source_language"] == u"SOURCE_TEST", mem
        assert mem["target_language"] == u"TARGET_TEST", mem
        assert mem["notes"] == u"NOTES", mem
        assert mem["id"] == 501, mem

    def test_add(self):
        self.repo.add()

        assert self.renderer.page == "memories/add.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Memories :: Add New", context

    def test_add_bad_mem(self):
        self.repo.add("foo")

        assert self.renderer.page == "memories/add.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Memories :: Add New", context
        assert "Failed to add memory: 'str' object has no attribute 'filename'" in context["msg"], context

    def test_add_with_mem(self):
        text = MEM_EMPTY

        source = Source("egg.xml", text)
        self.repo.add(source)

        assert self.renderer.page == "memories/add.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Memories :: Add New", context
        assert "egg.xml" in context["msg"], context

    def test_search_help(self):
        self.repo.search_help()

        assert self.renderer.page == "search/help.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Search Help :: Memory Serves", context

    def test_replace(self):
        self.repo.replace("1")

        assert self.renderer.page == "search/replace.html", self.renderer.page
        context = self.renderer.context
        assert context["replacefrom"] == u"", context

    def test_replace_queryfilters(self):
        self.repo.replace("1", ["foo"])

        assert self.renderer.page == "search/replace.html", self.renderer.page
        context = self.renderer.context
        assert context["queryfilters"] == [{'removelink': u'', 'term': u'foo'}], context["queryfilters"]

    def test_replace_find(self):
        records = model.Data.memories[1].mem["records"]
        records[model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))] = model.MemoryRecord(source=u"foo",
                                         trans=u"bar",
                                         id=1)
        self.repo.replace_find("1", "source:*", "XXX")

        assert self.renderer.page == "search/replace.html", self.renderer.page
        context = self.renderer.context

        assert context["result"].source == u"XXX", context["result"].source
        assert context["result"].trans == u"bar", context["result"].trans
        assert context["result"].source_cmp == u"xxx", context["result"].source_cmp
        assert context["result"].id == 1, context["result"].id

        assert context["found"] == records[model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))], context["found"]


    def test_replace_find_with_queryfilters(self):
        records = model.Data.memories[1].mem["records"]
        records[model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))] = model.MemoryRecord(source=u"foo",
                                         trans=u"bar",
                                         id=1)
        records[model.MAKE_KEY(dict(source=u"foo", trans=u"spam"))] = model.MemoryRecord(source=u"foo",
                                         trans=u"spam",
                                         id=2)
        self.repo.replace_find("1", "source:*", "XXX", queryfilters=["trans:spam"])

        assert self.renderer.page == "search/replace.html", self.renderer.page
        context = self.renderer.context

        assert context["result"].source == u"XXX", context["result"].source
        assert context["result"].trans == u"spam", context["result"].trans
        assert context["result"].source_cmp == u"xxx", context["result"].source_cmp
        assert context["result"].id == 2, context["result"].id

        assert context["found"] == records[model.MAKE_KEY(dict(source=u"foo", trans=u"spam"))], context["found"]

    def test_replace_replace(self):
        records = model.Data.memories[1].mem["records"]
        records[model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))] = model.MemoryRecord(source=u"foo",
                                         trans=u"bar",
                                         id=1)
        records[model.MAKE_KEY(dict(source=u"spam", trans=u"egg"))] = model.MemoryRecord(source=u"spam",
                                         trans=u"egg",
                                         id=3,
                                         last_modified=datetime.datetime.now())
        self.repo.replace_replace("1", "source:*", "XXX", nth_item="3")

        assert self.renderer.page == "search/replace.html", self.renderer.page
        found = records[(u"XXX", u"egg")]
        assert len(records) == 2, records

        assert found.source == u"XXX", found
        assert found.trans == u"egg", found

    def test_replace_replace_to_dup(self):
        records = model.Data.memories[1].mem["records"]
        records[model.MAKE_KEY(dict(source=u"XXX", trans=u"bar"))] = model.MemoryRecord(source=u"XXX",
                                         trans=u"bar",
                                         id=1)
        records[model.MAKE_KEY(dict(source=u"spam", trans=u"bar"))] = model.MemoryRecord(source=u"spam",
                                         trans=u"bar",
                                         id=3,
                                         last_modified=datetime.datetime.now())
        self.repo.replace_replace("1", "source:spam", "XXX", nth_item="3")

        assert self.renderer.page == "search/replace.html", self.renderer.page
        assert len(records) == 1, records
        found = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"bar"))]

        assert found.source == u"XXX", found
        assert found.trans == u"bar", found

        message = self.renderer.context["msg"]
        assert "There was another record with the" in message, message


    def test_replace_replace_no_mem(self):
        """
        Make sure we through the right error if the memory isn't found
        """

        try:
            self.repo.replace_replace("2", "source:*", "XXX", nth_item="3")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/", details.dest
        else:
            assert False, "Should have thrown"

        message = repository.cherrypy.session["msgs"][0]
        assert "Memory with id 2 not found" in message, message

    def test_replace_replace_not_found(self):
        """
        Make sure we through the right error if the memory isn't found
        """
        records = model.Data.memories[1].mem["records"]
        records[model.MAKE_KEY(dict(source=u"foo", trans=u"bar"))] = model.MemoryRecord(source=u"foo",
                                         trans=u"bar",
                                         id=1)
        records[model.MAKE_KEY(dict(source=u"spam", trans=u"egg"))] = model.MemoryRecord(source=u"spam",
                                         trans=u"egg",
                                         id=3,
                                         last_modified=datetime.datetime.now())

        try:
            self.repo.replace_replace("1", "source:*", "XXX", nth_item="4")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/replace/1", details.dest
        else:
            assert False, "Should have thrown"

        message = repository.cherrypy.session["msgs"][0]
        assert "No more records found with these criteria" in message, message

    def test_replace_all(self):
        records = model.Data.memories[1].mem["records"]

        self.add_record(u"foo", u"bar")
        rec2 = self.add_record(u"spam", u"egg")
        rec2.id = 3

        try:
            self.repo.replace_all("1", "source:*", "XXX")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/replace/1", details.dest
        else:
            assert False, "Should have thrown"

        assert len(records) == 2, records
        rec1 = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"bar"))]
        rec2 = records[model.MAKE_KEY(dict(source=u"XXX", trans=u"egg"))]

        assert rec1.source == u"XXX", rec1
        assert rec2.source == u"XXX", rec2

        assert rec1.trans == u"bar", rec1
        assert rec2.trans == u"egg", rec2


    def test_replace_all_with_queryfilters(self):
        records = model.Data.memories[1].mem["records"]
        self.add_record(u"foo", u"bar")
        self.add_record(u"foo", u"spam")

        try:
            self.repo.replace_all("1", "source:*", "XXX", queryfilters=["trans:spam"])
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/replace/1", details.dest
        else:
            assert False, "Should have thrown"

        assert len(records) == 2, records
        rec1 = records[(u"foo", u"bar")]
        rec2 = records[(u"XXX", u"spam")]

        assert rec1.source == u"foo", rec1
        assert rec2.source == u"XXX", rec2

        assert rec1.trans == u"bar", rec1
        assert rec2.trans == u"spam", rec2

    def test_replace_delete(self):
        records = model.Data.memories[1].mem["records"]
        self.add_record(u"foo", u"bar")
        self.add_record(u"foo", u"spam")

        try:
            self.repo.replace_all("1", "source:foo", "action:delete")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/memories/replace/1", details.dest
        else:
            assert False, "Should have thrown"

        assert len(records) == 0, records


class TestDownload(RepoTester):

    memtype = u"m"
    classtype = repository.Memories

    def setUp(self):
        RepoTester.setUp(self)

        mem = model.Memory(u"TestDownload", u"m")
        mem.id = 1
        model.Data.memories[1] = model.TranslationMemory(model.mem2d(mem))
        repository.render = self.old_render

    def test_empty(self):
        content = self.repo.download("1")

        headers = repository.cherrypy.response.headers
        assert headers['Content-Type'] == 'application/xml', headers
        assert headers['Content-Length'] == len(content), headers

        mem = model.Data.memories[1].mem
        context = dict(version=model.VERSION,
                       created_on=mem["created_on"])
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE memory >
<!-- Created by MemoryServes v %(version)s -->
<memory>
<head>
<creator>Ryan</creator>
<created_on>%(created_on)s</created_on>
<creation_tool>MemoryServes</creation_tool>
<creation_tool_version>%(version)s</creation_tool_version>
<num_records>0</num_records>
<locked>false</locked>
<is_memory>true</is_memory>
</head>
<records>
</records>
</memory>""" % context

        for e, a in zip(expected.splitlines(), content.splitlines()):
            assert e == a, (e, a)

class TestDownloadTmx(RepoTester):

    memtype = u"m"
    classtype = repository.Memories

    def setUp(self):
        RepoTester.setUp(self)

        mem = model.Memory(u"TestDownload", u"m")
        mem.id = 1
        model.Data.memories[1] = model.TranslationMemory(model.mem2d(mem))
        repository.render = self.old_render

    def test_no_langs(self):
        repository.render = self.old_render
        content = self.repo.download_tmx("1")

        assert """<td><label for="target">Translation Language</label></td>""" in content, content


    def test_empty(self):
        mem = model.Data.memories[1].mem
        mem["source_language"] = "EN"
        mem["target_language"] = "JA"

        content = self.repo.download_tmx("1")
        print content

        headers = repository.cherrypy.response.headers
        assert headers['Content-Type'] == 'application/xml', headers
        assert headers['Content-Length'] == len(content), headers

        context = dict(version=model.VERSION,
                       created_on=mem["created_on"])
        expected = """<?xml version='1.0' encoding='utf-8'?>
<tmx version="1.4">
  <header creationtoolversion="1.0.0" datatype="html" segtype="sentence" adminlang="EN-US" srclang="EN" o-tmf="Felix" creationtool="Felix"/>
  <body/>
</tmx>
""" % context

        for e, a in zip(expected.splitlines(), content.splitlines()):
            assert e == a, (e, a)


class TestGlossaries(RepoTester):
    memtype = u"g"
    classtype = repository.Glossaries

    def test_browse(self):

        self.repo.browse("1", "1")

        assert self.renderer.page == "browse.html", self.renderer.page

    def test_view(self):

        self.repo.view("1")

        assert self.renderer.page == "view.html", self.renderer.page

    def test_index(self):

        self.repo.index()

        assert self.renderer.page == "glossaries/index.html", self.renderer.page


    def test_add(self):
        self.repo.add()

        assert self.renderer.page == "glossaries/add.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Glossaries :: Add New", context

    def test_create_add_msg(self):
        item = dict(name=u"foo",
                    memtype=u"g",
                    id=1)
        head = dict(a=1, b=2, c=3)
        message = self.repo.create_add_msg(item, head)
        assert "Added" in message, message


class TestMergeUpload(RepoTester):
    memtype = u"m"
    classtype = repository.Memories

    def test_add_mem1(self):
        text = MEM_1

        source = Source("egg.xml", text)
        repo = repository.Repository(u"memory")
        repo.title_string = "foo"
        self.add_record("foo", "bar")

        try:
            repo.submitmerge("1", source)
        except:
            pass
        else:
            assert False, "Failed to redirect after merge"

        records = model.Data.memories[1].mem["records"]
        assert len(records) == 2, records


class TestMakeTmx(RepoTester):
    memtype = u"m"
    classtype = repository.Memories

    def test_simple(self):
        item = dict(name="foo",
                    source_language=u"Japanese",
                    target_language=u"English",
                    records={})

        content = self.repo.make_tmx_download(item)
        assert content, content

    def test_two_records(self):
        rec1 = model.MemoryRecord(u"rec1", u"rec1")
        rec2 = model.MemoryRecord(u"rec2", u"rec2")
        records = dict(((r.source, r.trans),r) for r in (rec1, rec2))
        item = dict(name="foo",
                    source_language=u"Japanese",
                    target_language=u"English",
                    records=records)

        content = self.repo.make_tmx_download(item)

        memory = objectify.fromstring(content)
        assert len(memory.body.tu) == 2, memory.body.tu

    def test_headers(self):

        item = dict(name="foo",
                    source_language=u"Japanese",
                    target_language=u"English",
                    records={})

        content = self.repo.make_tmx_download(item)

        headers = repository.cherrypy.response.headers
        assert headers['filename'] == 'application/xml', headers
        disp =  'attachment; filename=foo.tmx'
        assert headers['Content-Disposition'] == disp, headers

    #def test_japanese_name(self):
    #    item = dict(name=u"日本語",
    #                source_language=u"Japanese",
    #                target_language=u"English",
    #                records={})
    #
    #    content = self.repo.make_tmx_download(item)
    #    assert content


class TestReflectOneTrans(unittest.TestCase):
    def setUp(self):
        self.old_maker = model.MAKE_KEY
    def tearDown(self):
        model.MAKE_KEY = self.old_maker

    def test_True(self):
        model.MAKE_KEY = None
        repository.reflect_one_trans(True)
        assert model.MAKE_KEY == model.make_key_source, model.MAKE_KEY

    def test_False(self):
        model.MAKE_KEY = None
        repository.reflect_one_trans(False)
        assert model.MAKE_KEY == model.make_key_both, model.MAKE_KEY