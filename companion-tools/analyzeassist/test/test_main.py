# coding: UTF8
"""Unit test the main module
"""

from nose.tools import raises
from AnalyzeAssist import main


@raises(AssertionError)  # Ensure that the unit tests are running on this module...
def test_module():
    assert False


class AnalyzeAssistApp(main.AnalyzeAssistApp):
    def init_base(self, redirect, useBestVisual, clearSigInt):
        self.redirect = redirect
        self.useBestVisual = useBestVisual
        self.clearSigInt = clearSigInt

    def SetTopWindow(self, window):
        self.topwindow = window


broken_TestApp = '''
class TestApp:

    def setup(self):
        self.app = AnalyzeAssistApp()

    def testCreate(self):
        assert self.app.redirect == False
        assert self.app.useBestVisual == False
        assert self.app.clearSigInt == True

    def testOnInit(self):

        assert self.app.OnInit()

        assert "CenterOnScreen" in self.app.frame.calls, self.app.frame.calls
        assert "Show" in self.app.frame.calls, self.app.frame.calls
'''
