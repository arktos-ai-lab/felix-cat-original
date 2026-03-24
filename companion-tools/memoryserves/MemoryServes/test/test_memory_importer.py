#coding: UTF8
"""
Enter module description here.

"""

import unittest
from cStringIO import StringIO
import wx

import mock

from .. import MemoryImporter
from .. import model

class Holder:
    old_exists = None

class FakeChild(object):
    def __init__(self, tag, text):
        self.tag = tag
        self.text = text

class FakeElement(object):
    def __init__(self, children):
        self.children = children
    def getchildren(self):
        return self.children

class FakeRoot(object):
    def __init__(self, records):
        self.records = records

    def getiterator(self, tag):
        return self.records

class FakeDelayedResult(object):
    def __init__(self):
        self.consumer = None
        self.func = None
        self.wargs = None
        self.jobID = None

    def startWorker(self, consumer, func, wargs, jobID):
        self.consumer = consumer
        self.func = func
        self.wargs = wargs
        self.jobID = jobID

class TestFrame(unittest.TestCase):
    def setUp(self):
        self.wxlib = mock.MagicMock()
        self.sclib = mock.MagicMock()
        self.frame = MemoryImporter.MemoryImporterFrame(self.wxlib, self.sclib)
        MemoryImporter.load_model_data = lambda : None

    def test_on_close(self):
        self.frame.OnClose(None)
        self.sclib.SizedFrame().Close.assert_called_once_with()

    def test_update_head_memory(self):
        self.frame.head = {}
        for key in [x for (x,y) in MemoryImporter.FIELDS]:
            self.frame.info_controls[key].Value = "spam"
        self.frame.update_head()
        for key in [x for (x,y) in MemoryImporter.FIELDS if x != "memtype"]:
            assert self.frame.head[key] == "spam", (key, self.frame.head)
        assert self.frame.head["memtype"] == "m", self.frame.head

    def test_update_head_glossary(self):
        self.frame.head = {}
        self.frame.info_controls["memtype"].Value = "Glossary"
        self.frame.update_head()
        assert self.frame.head["memtype"] == "g", self.frame.head

    def test_OnImport(self):
        MemoryImporter.delayedresult = FakeDelayedResult()
        self.frame.head = {}
        self.frame.info_controls["memtype"].Value = "Memory"
        self.frame.OnImport(None)

        dr = MemoryImporter.delayedresult
        assert dr.consumer == self.frame._consume_results, dr.consumer
        assert dr.func == self.frame._import_memory, dr.func
        assert dr.wargs == (2,), dr.wargs
        assert dr.jobID == 2, dr.jobID


    def test_consume_results(self):

        self.frame._consume_results(FakeDelayedResult())
        assert True

    def test_OnBrowse_cancel(self):

        self.wxlib.FileDialog().ShowModal.return_value = wx.ID_CANCEL
        self.frame.OnBrowse(None)
        self.frame.statusbar.SetStatusText.assert_called_with("Cancelled file selection", 0)

    def test_OnBrowse_ok(self):

        self.wxlib.FileDialog().ShowModal.return_value = wx.ID_OK
        self.wxlib.FileDialog().GetPaths.return_value = ["spam"]
        self.frame.gather_info = lambda : None
        self.frame.OnBrowse(None)
        assert self.frame.filename == "spam", self.frame.filename
        assert self.frame.text_control.Value == "spam", self.frame.text_control.Value
        self.frame.statusbar.SetStatusText.assert_called_with("Loading file spam", 0)

    def test_gather_info(self):
        MemoryImporter.delayedresult = FakeDelayedResult()
        self.frame.gather_info()

        dr = MemoryImporter.delayedresult
        assert dr.consumer == self.frame._consume_results, dr.consumer
        assert dr.func == self.frame._gather_import, dr.func
        assert dr.wargs == (2,), dr.wargs
        assert dr.jobID == 2, dr.jobID


    def test__gather_import(self):
        tm = StringIO()
        print >> tm, """<?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE memory >
    <!-- Created by Align Assist v. 1.0 -->
    <memory>
        <head>
            <creator>Align Assist</creator>
            <created_on>2009/05/22 19:52:07</created_on>
            <creation_tool>Align Assist</creation_tool>
            <creation_tool_version>1.0</creation_tool_version>
            <num_records>0</num_records>
            <locked>false</locked>
            <is_memory>true</is_memory>
        </head>
    <records>
    </records>
    </memory>"""

        tm.seek(0)
        gfo = MemoryImporter.get_fileobj
        try:
            MemoryImporter.get_fileobj = lambda filename : tm

            self.frame.filename = "/test/spam.ftm"
            self.frame._gather_import(2)

            head = self.frame.head

            assert head["is_memory"], head
            assert head["memtype"] == "m", head
            assert head["name"] == "spam.ftm", head

            self.frame.statusbar.SetStatusText.assert_called_with("Ready to import file", 0)
        finally:
            MemoryImporter.get_fileobj = gfo

    def test__gather_import_glossary(self):
        tm = StringIO()
        print >> tm, """<?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE memory >
    <!-- Created by Align Assist v. 1.0 -->
    <memory>
        <head>
            <creator>Align Assist</creator>
            <created_on>2009/05/22 19:52:07</created_on>
            <creation_tool>Align Assist</creation_tool>
            <creation_tool_version>1.0</creation_tool_version>
            <num_records>0</num_records>
            <locked>false</locked>
            <is_memory>false</is_memory>
        </head>
    <records>
    </records>
    </memory>"""

        tm.seek(0)

        gfo = MemoryImporter.get_fileobj
        try:
            MemoryImporter.get_fileobj = lambda filename : tm

            self.frame.filename = "/test/spam.ftm"
            self.frame._gather_import(2)

            head = self.frame.head

            assert head["is_memory"] == "false", head
            assert head["memtype"] == "g", head
            self.frame.statusbar.SetStatusText.assert_called_with("Ready to import file", 0)

        finally:
            MemoryImporter.get_fileobj = gfo


class TestMainModuleStuff(unittest.TestCase):
    def test_get_fileobj(self):
        try:
            MemoryImporter.open = lambda x : x
            result = MemoryImporter.get_fileobj("foo")
            assert result == "foo", result
        finally:
            MemoryImporter.open = open

