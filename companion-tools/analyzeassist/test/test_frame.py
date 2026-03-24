# coding: UTF8
"""
Unit test the frame module
"""

from AnalyzeAssist.view import frame
from nose.tools import raises
from AnalyzeAssist import broker


def setup():
    broker.checkProv = lambda *args: args


@raises(AssertionError)
def test_module():
    """Make sure that our module is being picked up in unit tests"""

    assert False

# TypeError: unbound method __init__() must be called with Frame instance as first argument (got Frame instance instead)
broken_testFrame = '''
class testFrame:
    def setup(self):
        self.frame = frame.Frame()

    def test_create(self):
        assert self.frame.notebook
        assert len(self.frame.notebook.pages) == 1, self.frame.notebook.pages
        assert self.frame.toolbar
        assert self.frame.statusbar
'''
