'''
Tests the admin module
'''

import unittest

from nose.tools import raises
import mock

import fake_cherrypy
from .. import admin
from .. import settings
from .. import model
from .. import cherrybase
from .. import loc
from usertests import UserTestsDb

def disable_anon_privs():
    privs = settings.get_privs()
    anon = privs["anon"]
    for key in anon.keys():
        anon[key] = False

class TestUserById(UserTestsDb):
    def setUp(self):
        model.Data.users = {}
        UserTestsDb.setUp(self)

    def test_one_user(self):
        self.add_user(u"ryan", u"secret", u"admin")
        user = admin.user_by_id(model.Data.users.values(), 1)
        assert user["name"] == u"ryan", user
        assert user["id"] == 1, user

    def test_two_users(self):
        self.add_user(u"ryan", u"secret", u"admin")
        self.add_user(u"joe", u"user", u"secret")
        user = admin.user_by_id(model.Data.users.values(), 1)
        assert user["name"] == u"ryan", user
        assert user["id"] == 1, user

    def test_not_found(self):
        self.add_user(u"ryan", u"secret", u"admin")
        user = admin.user_by_id(model.Data.users.values(), 3)
        assert user is None, user

class TestUsers(UserTestsDb):
    def setUp(self):
        cherrybase.cherrypy = admin.cherrypy = fake_cherrypy.FakeCherryPy()
        self.users = admin.Users()
        self.renderer = fake_cherrypy.FakeRenderer()
        admin.render = self.renderer.render
        model.Data.users = {}

        UserTestsDb.setUp(self)

    def test_index_no_users_page(self):
        self.users.index()

        assert self.renderer.page == "users_index.html", self.renderer.page
        assert self.renderer.context["users"] == [], self.renderer.context

    def test_index_context(self):
        user = self.add_user(u"ryan", u"foo", u"admin", u"1.1.1.1")
        self.users.index()

        assert self.renderer.context["users"] == [user], self.renderer.context

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_add_not_admin(self):
        self.users.add()

    def test_add(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        self.users.add()
        del cherrybase.cherrypy.session["user"]
        assert self.renderer.page == "users_add.html", self.renderer.page

    def test_welcome(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        self.users.welcome()
        del cherrybase.cherrypy.session["user"]
        assert self.renderer.page == "users_welcome.html", self.renderer.page

    def test_index_no_users_page(self):
        try:
            self.users.submitwelcome(name="ryan", password="secret", confirm="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/", details
        else:
            assert False, "Should have thrown"

        user = model.Data.users[1]
        assert user["name"] == "ryan", user
        assert user["role"] == "admin", user
        assert user["password"] == model.make_hash(u"secret"), user

    def test_submitwelcome_no_name(self):
        try:
            self.users.submitwelcome(name="", password="secret", confirm="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/welcome", details
        else:
            assert False, "Should have thrown"

    def test_submitwelcome_no_password(self):
        try:
            self.users.submitwelcome(name="secret", password="", confirm="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/welcome", details
        else:
            assert False, "Should have thrown"

    def test_index_passwords_dont_match(self):
        try:
            self.users.submitwelcome(name="secret", password="public", confirm="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/welcome", details
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 Passwords did not match
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][0].split())

        assert expected == actual, (expected, actual)

    def test_logout(self):
        adminuser = self.add_user(u"George", u"secret", u"admin", ip="foo")
        cherrybase.cherrypy.session["user"] = adminuser

        try:
            self.users.logout(next="spam")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "spam", details.dest
        else:
            assert False, "Should have thrown"

    def test_view(self):
        user = self.add_user(u"ryan", u"foo", u"admin", u"1.1.1.1")
        self.users.view("1")

        assert self.renderer.page == "users_view.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: View User ryan", context
        assert context["viewuser"] == user, context

    def test_login(self):
        self.users.login(next="foo")

        assert self.renderer.page == "login.html", self.renderer.page
        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Log in", context
        assert context["next"] == "foo", context

    def test_submitlogin_nouser(self):
        try:
            self.users.submitlogin(next="foo", name="ryan", password="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/login/?next=foo", details
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 User name or password incorrect.
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][-1].split())

        assert expected == actual, (expected, actual)

    def test_submitlogin_passwords_dontmatch(self):
        self.add_user(u"ryan", u"admin", u"foo", u"1.1.1.1")

        try:
            self.users.submitlogin(next="foo", name="ryan", password="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/login/?next=foo", details
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 User name or password incorrect.
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][-1].split())

        assert expected == actual, (expected, actual)

    def test_submitlogin_passwords_match(self):
        user = self.add_user(u"ryan", u"secret", u"admin", u"1.1.1.1")

        print "user:", user
        try:
            self.users.submitlogin(next="foo", name="ryan", password="secret")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect:
            pass
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="success">
                             Welcome, ryan.
                             </div>""".split())
        session = admin.cherrypy.session
        actual = " ".join(session["msgs"][-1].split())

        assert expected == actual, (expected, actual)

        assert session["user"]["name"] == user["name"], (user, session)

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_permissions_not_admin(self):
        privs = settings.get_privs()
        anon = privs["anon"]
        for key in anon.keys():
            anon[key] = False
        self.users.permissions()

    def test_permissions(self):
        self.add_user(u"ryan", u"foo", u"admin", u"1.1.1.1")
        self.users.permissions()
        assert self.renderer.page == "users_permissions.html", self.renderer.page

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_submit_permissions_not_admin(self):
        privs = settings.get_privs()
        anon = privs["anon"]
        for key in anon.keys():
            anon[key] = False
        self.users.submitpermissions(**privs)

    def test_submit_permissions(self):
        privs = settings.get_privs()
        user = self.add_user(u"ryan", u"foo", u"admin", u"1.1.1.1")
        cherrybase.cherrypy.session["user"] = user
        try:
            self.users.submitpermissions(**privs)
        except fake_cherrypy.FakeCherryPy.HTTPRedirect:
            msg = "".join(msg for msg in cherrybase.cherrypy.session["msgs"])
            assert "Configured user preferences" in msg, msg


class TestUsersSubmitAdd(UserTestsDb):

    def test_not_admin(self):
        try:
            self.users.submitadd(name="ryan", password="secret", confirm="secret", role="user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/", details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 You must be an admin to add a user.
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][0].split())
        print "expected:", expected
        print "actual:  ", actual
        assert expected == actual, (expected, actual)

    def test_passwords_dont_match(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        try:
            self.users.submitadd(name=u"ted", password=u"public", confirm=u"secret", role=u"user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/add", details
        else:
            assert False, "Should have thrown"

    def test_success(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        try:
            self.users.submitadd(name=u"ted", password=u"secret", confirm=u"secret", role=u"user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            print details, details.dest
            assert details.dest == "/users/view/2", details
        else:
            assert False, "Should have thrown"

        cherrybase.cherrypy.session = {}

        user = model.Data.users[2]
        assert user["name"] == u"ted", user
        assert user["role"] == u"user", user

class TestUsersSubmitEdit(UserTestsDb):
    def test_not_logged_in(self):

        cherrybase.cherrypy.session = {}
        user = self.add_user(u"Fred", u"secret", u"secret")

        try:
            self.users.submitedit(str(user["id"]), name="ryan", password="secret", confirm="secret", role="user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/", details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 You must be logged in to edit account info.
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][0].split())
        print "expected:", expected
        print "actual:  ", actual
        assert expected == actual, (expected, actual)


    def test_not_admin(self):
        plainuser = self.add_user(u"George", u"secret", u"user")
        cherrybase.cherrypy.session["user"] = plainuser

        user = self.add_user(u"Fred", u"secret", u"user")

        try:
            self.users.submitedit(str(user["id"]), name="ryan", password="secret", confirm="secret", role="user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/", details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 You must be an admin to edit another user's account.
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][0].split())
        print "expected:", expected
        print "actual:  ", actual
        assert expected == actual, (expected, actual)

    def test_not_admin_switch_to_admin(self):
        plainuser = self.add_user(u"George", u"secret", u"user")
        cherrybase.cherrypy.session["user"] = plainuser

        try:
            self.users.submitedit(str(plainuser["id"]),
                                  name="ryan",
                                  password="secret",
                                  confirm="secret",
                                  role="admin")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/", details.dest
        else:
            assert False, "Should have thrown"

        expected = " ".join("""<div class="error">
                                 You cannot change your role to admin.
                                 </div>""".split())
        actual = " ".join(admin.cherrypy.session["msgs"][0].split())
        print "expected:", expected
        print "actual:  ", actual
        assert expected == actual, (expected, actual)


    def test_passwords_dont_match(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        user = self.add_user(u"Fred", u"public", u"secret", u"admin")

        try:
            self.users.submitedit(str(user["id"]), name=u"ted", password=u"public", confirm=u"secret", role=u"user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/edit/%(id)s" % user, details.dest
        else:
            assert False, "Should have thrown"

    def test_success(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        user = self.add_user(u"Fred", u"secret", u"secret")

        try:
            self.users.submitedit(str(user["id"]), name=u"ted", password=u"secret", confirm=u"secret", role=u"user")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/view/%(id)s" % user, details
        else:
            assert False, "Should have thrown"

        cherrybase.cherrypy.session = {}

        editeduser = model.Data.users[user["id"]]
        assert editeduser["name"] == u"ted", editeduser
        assert editeduser["role"] == u"user", editeduser


class TestUsersDb(UserTestsDb):

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_edit_not_admin(self):

        edituser = self.add_user(u"Fred", u"secret", u"user")
        user = self.add_user(u"Fred", u"user", u"secret")
        cherrybase.cherrypy.session["user"] = user
        self.users.edit(str(edituser["id"]))

    def test_edit(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        user = self.add_user(u"Fred", u"secret", u"admin")

        self.users.edit(str(user["id"]))
        del cherrybase.cherrypy.session["user"]
        assert self.renderer.page == "users_edit.html", self.renderer.page
        actual = self.renderer.context["edituser"]
        assert actual == user, (actual, user)

    def test_edit_not_logged_in(self):
        self.add_user(u"George", u"secret", u"admin")
        user = self.add_user(u"Fred", u"secret", u"admin")

        try:
            self.users.edit(str(user["id"]))
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            assert details.dest == "/users/", details.dest
        else:
            assert False, "Should have thrown"

    def test_delete_not_admin(self):
        disable_anon_privs()
        try:
            self.users.delete("1")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            expected = "User role anon not authorized for privilege site_admin"
            actual = " ".join(admin.cherrypy.session["msgs"][0].split())
            assert expected in actual, actual
            assert details.dest == "/users/login/?next=/users", details.dest
        else:
            assert False, "Should have thrown"

    def test_delete(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser

        assert len(model.Data.users) == 1, model.Data.users

        try:
            self.users.delete("1")
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            cherrybase.cherrypy.session = {}
            assert len(model.Data.users) == 0, model.Data.users
            assert details.dest == "/users/", details.dest
        else:
            assert False, "Should have thrown"


class TestLog(UserTestsDb):
    def setUp(self):
        self.log = admin.Log()
        UserTestsDb.setUp(self)

    def test_index(self):
        self.log.index()
        assert self.renderer.page == "log_index.html", self.renderer.page

    def test_clear(self):
        log1 = model.Log(u"foo")
        log1.id = 1
        log2 = model.Log(u"bar")
        log2.id = 2
        model.Data.log = [model.log2d(log1), model.log2d(log2)]

        admin_user = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = admin_user
        try:
            self.log.clear()
        except fake_cherrypy.FakeCherryPy.HTTPRedirect, details:
            print details
            assert model.Data.log == [], model.Data.log
        else:
            assert False, "Should have thrown here"

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_clear_not_admin(self):
        self.log.clear()

    @raises(fake_cherrypy.FakeCherryPy.HTTPRedirect)
    def test_clear_raises(self):
        adminuser = self.add_user(u"George", u"secret", u"admin")
        cherrybase.cherrypy.session["user"] = adminuser
        self.log.clear()

    def test_errorlog_page(self):
        fake_getter = lambda filename : "log text\n"
        with mock.patch("MemoryServes.loc.get_log_file_text", fake_getter):
            self.log.errorlog()

        assert self.renderer.page == "log_error.html", self.renderer.page

    def test_errorlog_context(self):
        fake_getter = lambda filename : "log text\n"
        with mock.patch("MemoryServes.loc.get_log_file_text", fake_getter):
            self.log.errorlog()

        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Server Error Log", context

    def test_serverlog_page(self):
        fake_getter = lambda filename : "log text\n"
        with mock.patch("MemoryServes.loc.get_log_file_text", fake_getter):
            self.log.serverlog()

        assert self.renderer.page == "log_server.html", self.renderer.page

    def test_serverlog_context(self):
        fake_getter = lambda filename : "log text\n"
        with mock.patch("MemoryServes.loc.get_log_file_text", fake_getter):
            self.log.serverlog()

        context = self.renderer.context
        assert context["title"] == "Memory Serves :: Server Access Log", context

class TestSetPrivs(unittest.TestCase):
    def setUp(self):
        self.privs = settings.get_privs()

    def tearDown(self):
        settings.Settings.PREFERENCES.update(settings.get_default_prefs())

    def test_empty(self):
        data = {}
        admin.set_privs(self.privs, data)
        assert not self.privs['admin']['tm_create']
        for role in self.privs.keys():
            for action in self.privs[role].keys():
                assert not self.privs[role][action], (role, action)

    def test_set_one(self):
        data = {'admin.tm_create' : 'on'}
        admin.set_privs(self.privs, data)
        assert self.privs['admin']['tm_create']
        for role in self.privs.keys():
            for action in self.privs[role].keys():
                if role != 'admin' or action != 'tm_create':
                    assert not self.privs[role][action], (role, action)

    def test_set_two(self):
        data = {'guest.rec_create' : 'on',
                'admin.tm_create' : 'on'}
        admin.set_privs(self.privs, data)
        assert self.privs['guest']['rec_create']
        assert self.privs['admin']['tm_create']
        for role in self.privs.keys():
            for action in self.privs[role].keys():
                if role not in ('admin', 'guest') or action not in ('tm_create', 'rec_create'):
                    assert not self.privs[role][action], (role, action)


class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.admin = admin.Admin()
        cherrybase.cherrypy = admin.cherrypy = fake_cherrypy.FakeCherryPy()
        self.renderer = fake_cherrypy.FakeRenderer()
        admin.render = self.renderer.render

    def test_index(self):
        self.admin.index()
        assert self.renderer.page == "admin_index.html", self.renderer.page
