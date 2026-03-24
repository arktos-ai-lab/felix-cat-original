# coding: UTF8
"""
Unit tests for Options dialog

"""

from AnalyzeAssist.view import options
import wx


class AnalysisPanel(options.AnalysisPanel):
    def init_base(self, parent):
        self.segExtensionTextCtrl = wx.TextCtrl()
        self.saveDirTextCtrl = wx.TextCtrl()
        self.extractSegsCheck = wx.CheckBox(Value=False)
        self.match_rangesTextCtrl = wx.TextCtrl()
        self.browse_button = wx.Button(None, u"Browse...")


class TestAnalysisPanel:
    def setup(self):
        self.panel = AnalysisPanel(None)
        self.panel.extractSegsCheck.Value = False

    def testCreate(self):
        pass

    def test_onExtractSegs(self):
        self.panel.extractSegsCheck.Value = False
        self.panel.onExtractSegs(None)
        assert self.panel.segExtensionTextCtrl.Enabled == False
        assert self.panel.saveDirTextCtrl.Enabled == False

        self.panel.extractSegsCheck.Value = True
        self.panel.onExtractSegs(None)
        assert self.panel.segExtensionTextCtrl.Enabled == True
        assert self.panel.saveDirTextCtrl.Enabled == True

        self.panel.extractSegsCheck.Value = False
        self.panel.onExtractSegs(None)
        assert self.panel.segExtensionTextCtrl.Enabled == False
        assert self.panel.saveDirTextCtrl.Enabled == False


    def test_getAnalysisPreferences(self):
        self.panel.extractSegsCheck.Value = True
        self.panel.segExtensionTextCtrl.Value = "foo"
        self.panel.saveDirTextCtrl.Value = "dir"
        self.panel.match_rangesTextCtrl.Value = "bar"

        fuzzy_options = dict(extension="foo",
                             directory="dir",
                             extract=True)

        prefs = self.panel.getAnalysisPreferences()
        expected = ("bar", fuzzy_options)
        assert prefs == expected, (prefs, expected)

    def test_getAnalysisPreferencesFalse(self):
        self.panel.segExtensionTextCtrl.Value = "foo"
        self.panel.match_rangesTextCtrl.Value = "bar"
        self.panel.saveDirTextCtrl.Value = "dir"
        self.panel.extractSegsCheck.Value = False

        ranges, actual_options = self.panel.getAnalysisPreferences()
        fuzzy_options = dict(extension="foo",
                             directory="dir",
                             extract=False)

        assert ranges == "bar", ranges
        assert actual_options == fuzzy_options, (actual_options, fuzzy_options)


broken_TestOptions = '''
class TestOptions:
    def setup(self):
        self.dlg = options.OptionsDialog(None)

    def testCreate(self):
        assert self.dlg.Title == u"AnalyzeAssist Options", self.dlg.Title

    def testaddControlRow(self):

        before = len(self.dlg.valuePairs)

        self.dlg.addControlRow(wordseg.Segmenter, "foo")

        after = len(self.dlg.valuePairs)

        assert before+1 == after, (before, after)

        static, text = self.dlg.valuePairs[-1]

        assert static.Label == "MS Word"
        assert text.Value == "foo"

    def testaddControlRows(self):

        classDict = {}
        extensionsDict = {}

        classDict["word"] = wordseg.Segmenter
        classDict["excel"] = excelseg.Segmenter

        extensionsDict["word"] = "*.doc"
        extensionsDict["excel"] = "*.xls"

        self.dlg.addControlRows(classDict, extensionsDict)

        assert len(self.dlg.valuePairs) == 2

        values = [(x.Label,y.Value) for (x,y) in self.dlg.valuePairs]

        assert ("MS Word", "*.doc") in values, values
        assert ("MS Excel", "*.xls") in values, values

    def testGetExtensions(self):

        classDict = {}
        extensionsDict = {}

        classDict["word"] = wordseg.Segmenter
        classDict["excel"] = excelseg.Segmenter

        extensionsDict["word"] = "*.doc"
        extensionsDict["excel"] = "*.xls"

        self.dlg.addControlRows(classDict, extensionsDict)

        assert len(self.dlg.valuePairs) == 2

        values = self.dlg.getExtensions()

        assert ("MS Word", "*.doc") in values, values
        assert ("MS Excel", "*.xls") in values, values
        assert len(values) == 2

    def test_get_extract_data(self):

        values = self.dlg.analysisPanel.getAnalysisPreferences()[1]

        assert "extension" in values, values
        assert "directory" in values, values
        assert "extract" in values, values

    def test_get_extract_data_values(self):

        self.dlg.analysisPanel.segExtensionTextCtrl.Value = "extension"
        self.dlg.analysisPanel.saveDirTextCtrl.Value = "directory"
        self.dlg.analysisPanel.extractSegsCheck.Value = True

        values = self.dlg.analysisPanel.getAnalysisPreferences()[1]

        assert values["extension"] == "extension", values
        assert values["directory"] == "directory", values
        assert values["extract"] == True, values
'''
