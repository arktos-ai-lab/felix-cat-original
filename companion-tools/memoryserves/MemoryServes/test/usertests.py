__author__ = 'Ryan'
import unittest

import fake_cherrypy
from .. import cherrybase
from .. import model
from .. import admin
from .. import settings

def add_user(name, password, role, ip):
        user_id = model.get_next_userid()
        user = model.User(name, role, password, ip, user_id)
        model.Data.users[user_id] = model.user2d(user)
        return model.Data.users[user_id]

class UserTestsDb(unittest.TestCase):
    def setUp(self):
        self.renderer = fake_cherrypy.FakeRenderer()
        admin.render = self.renderer.render
        cherrybase.cherrypy = admin.cherrypy = fake_cherrypy.FakeCherryPy()

        self.users = admin.Users()
        model.Data.users = {}

        settings.Settings.PREFERENCES = settings.get_default_prefs()

    def tearDown(self):
        model.Data.memories = {}
        model.Data.users = {}
        model.Data.log = []

    def add_user(self, name, password, role=u"user", ip="111.111.111.111"):
        return add_user(name, password, role, ip)
