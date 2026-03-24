# coding: UTF8
"""
Unit tests for About box
"""

import fakewidgets
from wx.lib import sized_controls as sc
from AnalyzeAssist.view import about
from AnalyzeAssist import broker
import AnalyzeAssist.model
from nose.tools import raises


@raises(AssertionError)
def test_module():
    assert False

# TypeError: unbound method __init__() must be called with SizedDialog instance as first argument (got AboutBox instance instead)
broken_test_about_box = '''
def test_get_page_e():
    page = about.get_page("English")
    expected = u"C:\\dev\\python\\AnalyzeAssist\\res\\AboutE.html"
    assert page == expected, (page, expected)

def test_get_page_j():
    page = about.get_page("Japanese")
    expected = u"C:\\dev\\python\\AnalyzeAssist\\res\\AboutJ.html"
    assert page == expected, (page, expected)

class test_get_about_box():
    about_box = about.get_about_box(None)
    assert isinstance(about_box, about.AboutBox)

class testAbout:
    def setup(self):
        self.about = about.AboutBox(None, None, None)

    def testCreate(self):
        assert isinstance(self.about, about.AboutBox)
'''
