# coding: UTF8
"""
Unit tests for wizard module

"""

import wx
from AnalyzeAssist.view import wizard
from nose.tools import raises
from AnalyzeAssist import broker
from test_utilities import Bunch
import AnalyzeAssist.model
import fakewidgets


@raises(AssertionError)
def test_module():
    """Make sure that our module is being picked up in unit tests"""
    assert False


def mockGetText():
    msg = broker.CurrentData()
    return unicode(msg, "utf-8")


def test_makePageTitle():
    dlg = wx.Dialog(None)
    sizer = wizard.makePageTitle(dlg, "spam")
    assert sizer.items[0].Label == "spam", sizer.items[0].Label


class WizPageFileListBase(wizard.WizPageFileListBase):
    def get_wildcard(self):
        return '|'.join([_("All Files (*.*)|*.*"),
                         _("MS Word (*.doc)|*.doc"),
                         _("MS Excel (*.xls;*.csv)|*.xls;*.csv"),
                         _("MS PowerPoint (*.ppt)|*.ppt"),
                         _("Text Files (*.txt)|*.txt"),
                         _("XML Files (*.xml)|*.xml"),
                         _("HTML Files (*.html;*.htm)|*.html;*.htm"),
        ])


broken_TestWizePageFileListBase = """
class TestWizePageFileListBase:

    def setup(self):
        self.page = WizPageFileListBase(None, "foo", "bar")

    def testCreate(self):
        pass

    def testMakeremove_button(self):

        self.page.makeremove_button()
        assert self.page.remove_button.Enabled == False
        assert self.page.remove_button.Label == _("&Remove")

    def testMakeList(self):

        self.page.makeList()
        assert self.page.file_list.Enabled == True

    def testLayout(self):

        self.page.layout("spam", "eggs")
        title = self.page.sizer.items[0].Label
        assert title == "spam", title

        subtitle = self.page.sizer.items[2].Label
        assert subtitle == "eggs", subtitle

    def testBindEvents(self):

        self.page.bindEvents()

    def testRemoveNone(self):

        self.page.OnRemove(wx.Event())

    def testOnItemDeselected(self):

        self.page.OnItemDeSelected(wx.Event())
        assert self.page.remove_button.Enabled == False

    def testOnItemSelected(self):

        assert self.page.remove_button.Enabled == False
        self.page.OnItemSelected(wx.Event())
        assert self.page.remove_button.Enabled == True

    def test_OnBrowse(self):

        fakewidgets.core.FileDialog.paths = []

        self.page.wildcard = '|'.join(["All Files (*.*)|*.*",
                              "MS Word (*.doc)|*.doc"])

        self.page.OnBrowse(None)

        assert self.page.file_list.ItemData == []
        assert self.page.file_list.GetFirstSelected() == -1

    def test_OnBrowse_withFiles(self):

        fakewidgets.core.FileDialog.paths = ["c:\\test\\a.doc"]

        self.page.wildcard = '|'.join(["All Files (*.*)|*.*",
                              "MS Word (*.doc)|*.doc"])

        self.page.OnBrowse(None)

        actual = list(self.page.files)
        assert actual == ["c:\\test\\a.doc"], actual
"""

broken_TestWizPageFiles = """
class TestWizPageFiles:
    def setup(self):
        self.page = wizard.WizPageFiles(None)


    def testMakebrowse_button(self):

        self.page.makebrowse_button()
        assert self.page.browse_button.Enabled == True
        assert self.page.browse_button.Label == _("&Browse...")

class TestWizPageMemories:
    def setup(self):
        self.page = wizard.WizPageMemories(None)


    def testMakebrowse_button(self):

        self.page.makebrowse_button()
        assert self.page.browse_button.Enabled == True
        assert self.page.browse_button.Label == _("&Browse...")

class TestWizPagePreferences:
    def setup(self):
        self.page = wizard.WizPagePreferences(None)

    def test_onExtractSegs(self):

        self.page.extractSegsCheck.Value = False
        self.page.onExtractSegs(None)
        assert self.page.segExtensionTextCtrl.Enabled == False
        assert self.page.saveDirTextCtrl.Enabled == False

        self.page.extractSegsCheck.Value = True
        self.page.onExtractSegs(None)
        assert self.page.segExtensionTextCtrl.Enabled == True
        assert self.page.saveDirTextCtrl.Enabled == True

        self.page.extractSegsCheck.Value = False
        self.page.onExtractSegs(None)
        assert self.page.segExtensionTextCtrl.Enabled == False
        assert self.page.saveDirTextCtrl.Enabled == False


    def test_getAnalysisPreferences(self):

        self.page.extractSegsCheck.Value = True
        self.page.segExtensionTextCtrl.Value = "foo"
        self.page.saveDirTextCtrl.Value = "dir"
        self.page.match_rangesTextCtrl.Value = "bar"

        fuzzy_options = dict(extension="foo",
                             directory="dir",
                             extract=True)

        prefs = self.page.getAnalysisPreferences()
        expected = ("bar", fuzzy_options)
        assert  prefs == expected, (prefs, expected)

    def test_getAnalysisPreferencesFalse(self):

        self.page.segExtensionTextCtrl.Value = "foo"
        self.page.match_rangesTextCtrl.Value = "bar"
        self.page.saveDirTextCtrl.Value = "dir"
        self.page.extractSegsCheck.Value = False

        ranges, actual_options = self.page.getAnalysisPreferences()
        fuzzy_options = dict(extension="foo",
                             directory="dir",
                             extract=False)

        assert ranges == "bar", ranges
        assert actual_options == fuzzy_options, (actual_options,fuzzy_options)

    def test_on_browse(self):

        fakewidgets.core.DirDialog.path = 'c:\\Test'
        fakewidgets.core.Dialog.retval = wx.ID_OK
        self.page.OnBrowse(None)
        assert self.page.saveDirTextCtrl.Value.lower() == "c:\\test", self.page.saveDirTextCtrl.Value
"""
