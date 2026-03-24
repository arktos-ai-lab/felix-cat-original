#!/usr/bin/env python
import unittest
from .. import api
from .. import model
from .. import settings
from fake_cherrypy import FakeCherryPy
from .. import cherrybase

class FakeTimer:
    def __init__(self, seconds, action):
        self.seconds = seconds
        self.action = action
    def start(self):
        self.action()

class ApiTester((unittest.TestCase)):
    ApiClass = api.Api

    def setUp(self):

        self.api = self.ApiClass()

        mem = model.Memory(u"ApiTester", u"m")
        mem.id = 1
        model.Data.memories = {1 : model.TranslationMemory(model.mem2d(mem))}
        model.Data.log = []
        model.Data.next_id = 1
        settings.Settings.PREFERENCES.update(settings.get_default_prefs())

        api.cherrypy = cherrybase.cherrypy = FakeCherryPy()

    def tearDown(self):
        model.Data.memories = {}
        model.Data.users = {}
        model.Data.log = []
        model.Data.logins = {}
        model.Data.next_id = 1

    def add_record(self, source, trans):

        mem = model.Data.memories[1]
        rec = model.MemoryRecord(source, trans)
        rec.id = model.get_next_recid()
        rec.memory_id = len(mem.mem["records"]) + 1
        mem.add_record(rec)

        return rec
