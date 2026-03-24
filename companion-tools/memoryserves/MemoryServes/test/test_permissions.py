#!/usr/bin/env python

import unittest
from .. import api
from .. import settings
from .. import permissions
from .. import model
from nose.tools import raises

class TestGetUserRole(unittest.TestCase):
    def test_None(self):
        token = "foo"
        role = permissions.get_user_role(token)
        assert role == "anon", role

    def test_admin(self):
        user = dict(username="Joe", role="admin", token="foo")
        token = api.make_token()
        model.Data.logins[token] = user
        role = permissions.get_user_role(token)
        assert role == "admin", role

class TestUserHasPriv(unittest.TestCase):
    def test_False(self):
        prefs = dict(anon=dict(tm_create=False))
        assert not permissions.user_has_priv("anon", "tm_create", prefs)
    def test_True(self):
        prefs = dict(anon=dict(tm_create=True))
        assert permissions.user_has_priv("anon", "tm_create", prefs)
    def test_False_anon(self):
        prefs = dict(anon=dict(tm_create=False), admin=dict(tm_create=True))
        assert not permissions.user_has_priv("anon", "tm_create", prefs)
    def test_True_admin(self):
        prefs = dict(anon=dict(tm_create=False), admin=dict(tm_create=True))
        assert permissions.user_has_priv("admin", "tm_create", prefs)

class TestRequiresPriv(unittest.TestCase):
    def setUp(self):
        self.old_privs = settings.Settings.PREFERENCES
        self.api = api.Api()

    def tearDown(self):
        settings.Settings.PREFERENCES = self.old_privs
        model.Data.memories = {}
        model.Data.users = {}
        model.Data.log = []
        model.Data.logins = {}
        model.Data.next_id = 1

    @raises(permissions.NotAuthorizedError)
    def test_fail_admem(self):
        prefs = dict(user_privs=dict(anon=dict(tm_create=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.addmem()

    @raises(permissions.NotAuthorizedError)
    def test_fail_delmem(self):
        prefs = dict(user_privs=dict(anon=dict(tm_delete=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.delmem()

    @raises(permissions.NotAuthorizedError)
    def test_fail_info(self):
        prefs = dict(user_privs=dict(anon=dict(tm_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.info()

    @raises(permissions.NotAuthorizedError)
    def test_fail_rec_by_id(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.rec_by_id()

    @raises(permissions.NotAuthorizedError)
    def test_fail_getrange(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.getrange()

    @raises(permissions.NotAuthorizedError)
    def test_fail_gloss(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.gloss()

    @raises(permissions.NotAuthorizedError)
    def test_fail_delete(self):
        prefs = dict(user_privs=dict(anon=dict(rec_delete=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.delete()

    @raises(permissions.NotAuthorizedError)
    def test_fail_add(self):
        prefs = dict(user_privs=dict(anon=dict(rec_create=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.add()

    @raises(permissions.NotAuthorizedError)
    def test_fail_update(self):
        prefs = dict(user_privs=dict(anon=dict(rec_update=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.update()

    @raises(permissions.NotAuthorizedError)
    def test_fail_concordance(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.concordance()

    @raises(permissions.NotAuthorizedError)
    def test_fail_rconcordance(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.rconcordance()

    @raises(permissions.NotAuthorizedError)
    def test_fail_memsearch(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.memsearch()

    @raises(permissions.NotAuthorizedError)
    def test_fail_search(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.search()

    @raises(permissions.NotAuthorizedError)
    def test_fail_rsearch(self):
        prefs = dict(user_privs=dict(anon=dict(rec_read=False)))
        settings.Settings.PREFERENCES = prefs
        self.api.rsearch()

    @raises(permissions.NotAuthorizedError)
    def test_fail_admem_admin(self):
        prefs = dict(user_privs=dict(anon=dict(tm_create=False),
                                     admin=dict(tm_create=True)))
        settings.Settings.PREFERENCES = prefs
        self.api.addmem()

    def test_succeed_admem_admin(self):
        prefs = dict(user_privs=dict(anon=dict(tm_create=False),
                                     admin=dict(tm_create=True)))
        settings.Settings.PREFERENCES = prefs
        user = dict(username="Joe", role="admin", token="foo")
        token = api.make_token()
        model.Data.logins[token] = user
        values = dict(name="TestRequiresPriv.test_succeed_admem_admin",
                      memtype="m",
                      creator=u"Ryan",
                      token=token)
        self.api.addmem(**values)
