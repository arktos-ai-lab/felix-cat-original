#encoding: UTF8

import unittest
import datetime

import mock

import fake_cherrypy
import utils
from .. import model
from .. import dataloader
from sqlalchemy.orm import clear_mappers
from .. import globalsearch as gs
from .. import legacy
from .. import main
from .. import cherrybase

class EngineHolder:
    engine = None
    SessionClass = None


def setUpModule():
    EngineHolder.SessionClass = dataloader.make_session_class(EngineHolder.engine)


def tearDownModule():
    clear_mappers()


class TestParseTime(unittest.TestCase):
    def test_datetime(self):
        """
        A datetime object is returned as-is
        """
        expr = datetime.datetime(1999, 9, 9, 9, 9, 9)
        actual = legacy.parse_time(expr)
        expected = expr
        assert actual == expected, actual

    def test_unicode(self):
        """
        A unicode string is parsed into a datetime object.
        """
        expr = u"1998/1/1 5:6:7"
        actual = legacy.parse_time(expr)
        expected = datetime.datetime(1998, 1, 1, 5, 6, 7)
        assert actual == expected, actual

    def test_bogus(self):
        """
        A bogus string returns the get_now function output
        """
        expr = u"foo"
        actual = legacy.parse_time(expr)
        assert isinstance(actual, datetime.datetime)


class TestParseValidated(unittest.TestCase):
    def test_true(self):
        validated = "true"
        actual = legacy.parse_validated(validated)
        assert actual is True, actual

    def test_True(self):
        validated = "True"
        actual = legacy.parse_validated(validated)
        assert actual is True, actual

    def test_false(self):
        validated = "false"
        actual = legacy.parse_validated(validated)
        assert actual is False, actual

    def test_False(self):
        validated = "False"
        actual = legacy.parse_validated(validated)
        assert actual is False, actual

    def test_FalseActual(self):
        validated = False
        actual = legacy.parse_validated(validated)
        assert actual is False, actual

    def test_TrueActual(self):
        validated = True
        actual = legacy.parse_validated(validated)
        assert actual is True, actual

    def test_foo(self):
        validated = "foo"
        actual = legacy.parse_validated(validated)
        assert actual is True, actual


class TestLoadMemoriesLegacy(unittest.TestCase):

    def setUp(self):
        EngineHolder.engine = dataloader.get_engine(":memory:")
        EngineHolder.SessionClass = dataloader.make_session_class(EngineHolder.engine)

    def tearDown(self):
        clear_mappers()

    def test_load_memories(self):
        """
        Load memories (with their records) from the database
        """
        session = EngineHolder.SessionClass()
        mem = model.Memory(u"foo", u"m")
        session.add(mem)
        session.flush()

        dataloader.load_memories(session)

        assert mem.id == 1, mem.id
        assert model.Data.memories[1].mem["name"] == u"foo", model.Data.memories

