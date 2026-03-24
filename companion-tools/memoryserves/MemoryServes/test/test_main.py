#coding: UTF8
"""
Unit tests for the `main` module

"""

import unittest

import fake_cherrypy
from .. import main
from .. import model
from .. import search
from .. import cherrybase
from .. import presentation
from .. import settings
from .. import loc


class FakeThreading:
    class Timer:
        seconds = None
        action = None
        def __init__(self, seconds, action):
            FakeThreading.Timer.seconds = seconds
            FakeThreading.Timer.action = action
        def start(self):
            pass


class TestAdminPrefs(unittest.TestCase):
    def setUp(self):
        cherrybase.cherrypy = main.cherrypy = fake_cherrypy.FakeCherryPy()
        self.app = main.MemoryServesApp()
        self.renderer = fake_cherrypy.FakeRenderer()
        main.render = self.renderer.render

        self.old_serialize_prefs = settings.serialize_prefs
        self.old_get_prefs = settings.get_prefs
        self.prefs = {}
        settings.serialize_prefs = self.serialize_prefs
        settings.get_prefs = self.get_prefs

    def tearDown(self):
        settings.serialize_prefs = self.old_serialize_prefs
        settings.get_prefs = self.old_get_prefs
        main.cherrypy.session = {}
        cherrybase.cherrypy.session = {}
        main.render = presentation.render

    def serialize_prefs(self, prefs):
        self.prefs = prefs
    def get_prefs(self):
        return self.prefs

    def test_edit(self):
        prefs = dict(case=0,
                     width=1,
                     hira=0,
                     data_folder=r"C:\\")
        try:
            self.app.editprefs(**prefs)
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/", details.dest
        else:
            assert False, "Should have thrown"

        assert not self.prefs["normalize_case"], self.prefs
        assert self.prefs["normalize_width"], self.prefs
        assert not self.prefs["normalize_hira"], self.prefs

        expected = " ".join("""<div class="success">
                                 Changed preferences
                                 </div>""".split())
        actual = " ".join(main.cherrypy.session["msgs"][0].split())
        assert expected == actual, (expected, actual)

    def test_preferences(self):

        self.app.preferences()
        assert self.renderer.page == "preferences.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Preferences", context


class TestConfigureApplication(unittest.TestCase):
    def setUp(self):

        self.server = fake_cherrypy.FakeCherryPy()
        main.configure_application(self.server, fake_cherrypy.FakeSqlAlchemySession)

    def tearDown(self):
        pass

    def test_mounted(self):
        mounted = self.server.tree.mounted
        assert mounted["path"] == "/", mounted
        assert isinstance(mounted["app"], main.MemoryServesApp), mounted
        assert mounted["config"]['/favicon.ico']['tools.staticfile.on'] == True, mounted

    def test_server(self):
        assert self.server.response.timeout == 1200, self.server.response.timeout
        assert self.server.server.socket_timeout == 120, self.server.server.socket_timeout


class TestMemoryServesApp(unittest.TestCase):

    def setUp(self):
        cherrybase.cherrypy = main.cherrypy = fake_cherrypy.FakeCherryPy()
        self.app = main.MemoryServesApp()
        self.renderer = fake_cherrypy.FakeRenderer()
        main.render = self.renderer.render
        model.Data.users = {}

    def tearDown(self):
        main.cherrypy.session = {}
        cherrybase.cherrypy.session = {}
        main.render = presentation.render

    def test_index_user(self):

        user = model.User(u"ryan", u"admin", u"secret")
        user.id = 1
        model.Data.users[1] = model.user2d(user)
        self.app.index()

        assert self.renderer.page == "index.html", self.renderer.page
        context = self.renderer.context
        expected = "%s:%s" % (settings.get_host(), settings.get_port())

        assert context["connection"] == expected, context
        prefs = settings.get_prefs()
        for key in prefs:
            assert context[key] == prefs[key], (context, prefs)

    def test_index_nouser(self):
        try:
            self.app.index()
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/welcome", details.dest
        else:
            assert False, "Should have thrown"

    def test_help(self):

        self.app.help()
        assert self.renderer.page == "help.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Help", context


class TestAdminExit(unittest.TestCase):
    def setUp(self):
        cherrybase.cherrypy = main.cherrypy = fake_cherrypy.FakeCherryPy()
        self.app = main.MemoryServesApp()
        self.renderer = fake_cherrypy.FakeRenderer()
        main.render = self.renderer.render

        self.old_threading = main.threading
        main.threading = FakeThreading()

    def tearDown(self):
        main.threading = self.old_threading
        main.cherrypy.session = {}
        cherrybase.cherrypy.session = {}
        main.render = presentation.render
        model.Data.memories = {}
        model.Data.users = {}
        model.Data.log = []

    def adduser(self, name, password, confirm, role=u"user"):
        user = model.User(name, password, confirm, role)
        userid = model.get_next_userid()
        user.id = userid
        model.Data.users[userid] = model.user2d(user)
        return model.Data.users[userid]

    def test_backdoor(self):
        model.SHOULD_QUIT = False
        self.app.backdoor()
        assert self.renderer.page == "exit.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Quit", context
        assert model.SHOULD_QUIT

    def test_exit_not_admin(self):
        try:
            self.app.exit()
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/", details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 You must be an admin to exit the program.
                                 </div>""".split())
        actual = " ".join(main.cherrypy.session["msgs"][0].split())
        assert expected == actual, (expected, actual)

    def test_exit(self):
        model.SHOULD_QUIT = False
        adminuser = self.adduser(u"George", u"admin", u"secret")
        cherrybase.cherrypy.session["user"] = adminuser

        self.app.exit()
        assert self.renderer.page == "exit.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Quit", context
        assert model.SHOULD_QUIT

