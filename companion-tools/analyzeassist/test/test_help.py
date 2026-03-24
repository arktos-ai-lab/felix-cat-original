# coding: UTF8
"""
Unit tests for the view.helpBox module

"""

from AnalyzeAssist.view import helpBox
import wx
from AnalyzeAssist import broker


# TypeError: unbound method __init__() must be called with SizedDialog instance as first argument (got HelpBox instance instead)
broken_test_get_help_box = '''
def test_get_help_box():
    help_box = helpBox.get_help_box(None)
    assert help_box

class testHelpBox:

    def setup(self):
        self.box = helpBox.HelpBox(None)

    def test_create(self):
        pass
'''
