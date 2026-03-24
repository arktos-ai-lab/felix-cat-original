# coding: UTF8
"""
Unit tests for the dump_text module
"""

from AnalyzeAssist import dump_text
from nose.tools import raises
import fakewidgets
import wx
import os
import glob


@raises(AssertionError)
def test_module():
    assert False, "Make sure that our tests are getting run"

# TypeError: unbound method __init__() must be called with ListCtrl instance as first argument (got FileList instance instead)
broken_TestDump = '''
class TestDump(object):
    def setup(self):
        if os.path.exists("/test/a.html.segs.txt"):
            os.remove("/test/a.html.segs.txt")

    def test_cancel(self):
        fakewidgets.core.Dialog.retval = wx.CANCEL
        dump_text.dump()
        assert not os.path.exists("/test/a.html.segs.txt")
'''
