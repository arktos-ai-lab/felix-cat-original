#coding: UTF8
"""
Enter module description here.

"""

import unittest
import socket
import datetime
import time

import fake_cherrypy
from .. import model
from .. import cherrybase


class TestGetUserRole(unittest.TestCase):
    def test_no_user(self):
        session = {}
        actual = cherrybase.get_user_role(session)
        expected = "anon"

        assert actual == expected, actual

    def test_user_admin(self):
        session = {"user" : {"role" : "admin"}}
        actual = cherrybase.get_user_role(session)
        expected = "admin"

        assert actual == expected, actual


def test_log_mem_failure():
    model.Data.log = []
    cherrybase.log_mem_failure(1)
    log = model.Data.log
    assert len(log) == 1, model.Data.log
    assert log[0]["message"] == "Memory with id: 1 not found", log


def setUpModule():
    cherrybase.cherrypy = fake_cherrypy.FakeCherryPy()

class FakeUser:
    def __init__(self, name=None):
        self.name = name


class TestToDate(unittest.TestCase):
    def test_plain(self):
        thedate = "2009/10/10 11:11:11"
        actual = cherrybase.to_date(thedate)
        assert actual == unicode(thedate), (actual, thedate)

    def test_uni(self):
        thedate = u"2009/10/10 11:11:11"
        actual = cherrybase.to_date(thedate)
        assert actual == thedate, (actual, thedate)

    def test_datetime(self):
        thedate = u"2009/10/10 11:11:11"
        actual = cherrybase.to_date(datetime.datetime(2009, 10, 10, 11, 11, 11))
        assert actual == thedate, (actual, thedate)

    def test_time(self):
        thedate = u"2009/10/10 11:11:11"
        thetime = time.localtime()
        actual = cherrybase.to_date(thetime)
        assert actual.startswith(str(thetime.tm_year)), actual


class TestMessages(unittest.TestCase):
    def setUp(self):
        cherrybase.cherrypy = fake_cherrypy.FakeCherryPy()

    def test_add_plain(self):
        cherrybase.cherrypy.session["msgs"] = []
        cherrybase.add_message("message")
        msgs = cherrybase.cherrypy.session["msgs"]
        assert msgs == ["message"], cherrybase.cherrypy.session

    def test_add_fresh(self):
        cherrybase.add_message("message")
        msgs = cherrybase.cherrypy.session["msgs"]
        assert msgs == ["message"], cherrybase.cherrypy.session

    def test_get_plain(self):
        cherrybase.add_message("spam")
        cherrybase.add_message("eggs")
        msg = cherrybase.get_messages()
        assert msg == "spam\neggs", msg
        msgs = cherrybase.get_messages()
        assert not msgs, msgs


class TestInitContext(unittest.TestCase):
    def test_logged_in(self):
        context = cherrybase.init_context()
        assert not context["logged_in"], context

class TestReplacer(unittest.TestCase):
    def test_empty(self):
        text = u""
        replaced = cherrybase.replacer(text)
        assert text == u"", text
    def test_normal(self):
        text = u"foo"
        replaced = cherrybase.replacer(text)
        assert replaced == u"foo", replaced
    def test_tab(self):
        text = u"\t"
        replaced = cherrybase.replacer(text)
        assert replaced == u"&#9;", replaced
    def test_japanese(self):
        text = u"日本語"
        replaced = cherrybase.replacer(text)
        assert replaced == u"日本語", replaced

class TestLog(unittest.TestCase):

    def setUp(self):
        model.Data.log = []

    def test_info(self):
        message = u"You have been infoed"
        cherrybase.log_info(message)

        assert len(model.Data.log) == 1, model.Data.log

        log = model.Data.log[0]
        assert log["message"] == message, log
        assert log["severity"] == u"info", log

    def test_warn(self):
        message = u"You have been warned"
        cherrybase.log_warning(message)

        assert len(model.Data.log) == 1, model.Data.log

        log = model.Data.log[0]
        assert log["message"] == message, log
        assert log["severity"] == u"warn", log

    def test_error(self):
        message = u"You have been errored"
        cherrybase.log_error(message)

        assert len(model.Data.log) == 1, model.Data.log

        log = model.Data.log[0]
        assert log["message"] == message, log
        assert log["severity"] == u"error", log


class TestGetUserName(unittest.TestCase):
    def test_nosession(self):
        assert cherrybase.get_username() == u"Ryan-PC", cherrybase.get_username()

    def test_session_user(self):
        user = model.User(u"Fred", u"user", u"secret")
        user.id = 1
        user = model.user2d(user)
        session = dict(user=user)
        actual = cherrybase.get_username(session)
        assert actual == u"Fred", actual

    def test_session_no_user_ip_match(self):
        """
        Ensure that the username for a non-logged-in user is the same as the computer name.
        """

        ip = socket.gethostbyname(socket.gethostname())
        session = dict(ip=ip)
        actual = cherrybase.get_username(session)
        assert actual == u"Ryan", actual

    def test_session_no_user_ip_match_username_set(self):
        """
        Ensure that when we retrieve the username and there is no session, the computer name is set as the username.
        """

        ip = socket.gethostbyname(socket.gethostname())
        session = dict(ip=ip)
        cherrybase.get_username(session)
        assert session["username"] == u"Ryan", session

    def test_session_nouser_ip_nomatch(self):
        ip = "1.1.1.1"
        session = dict(ip=ip)
        actual = cherrybase.get_username(session)
        assert actual == u"Ryan-PC", actual

    def test_session_nouser_ip_nomatch_username_set(self):
        ip = "1.1.1.1"
        session = dict(ip=ip)
        cherrybase.get_username(session)
        assert session["username"] == u"Ryan-PC", session


    def test_session_has_username(self):
        session = dict(username=u"Betty")
        actual = cherrybase.get_username(session)
        assert actual == u"Betty", actual
