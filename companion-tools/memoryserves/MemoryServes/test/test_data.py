#!/usr/bin/env python

import unittest
from .. import data
import win32api

class TestData(unittest.TestCase):
    def test_user_name(self):
        assert data.USER_NAME == "Ryan", data.USER_NAME

    def test_bad_username(self):
        def raise_func():
            raise Exception("foo")
        old_get = data.win32api.GetUserName
        data.win32api.GetUserName = raise_func
        reload(data)
        assert data.USER_NAME == u"Default", data.USER_NAME
        data.win32api.GetUserName = old_get
        reload(data)
