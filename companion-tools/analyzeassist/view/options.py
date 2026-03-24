# coding: UTF8
"""
View module for Options dialog

"""
import logging
import wx
from AnalyzeAssist import broker
from wx.lib import sized_controls as sc
import wizard
from AnalyzeAssist.AppUtils import resource_file_name
from AnalyzeAssist import model
from segmenter import htmlseg

_ = model._
MAKE_ANALYSIS_PANEL = True
LOGGER = logging.getLogger(__name__)


def set_html_options(options=None):
    htmlprefs = options or model.get_html_seg_options()
    htmlseg.WANT_A_TITLE = htmlprefs.get("want_a_title")
    htmlseg.WANT_IMG_ALT = htmlprefs.get("want_img_alt")
    htmlseg.WANT_INPUT_VALUE = htmlprefs.get("want_input_value")
    htmlseg.WANT_META_DESCRIPTION = htmlprefs.get("want_meta_description")
    htmlseg.WANT_META_KEYWORDS = htmlprefs.get("want_meta_keywords")


class HtmlOptionsPanel(sc.SizedPanel):
    def __init__(self, parent):
        sc.SizedPanel.__init__(self, parent)

        wx.StaticText(self, -1, _("Select the types of tag attributes to include in analysis"))

        self.want_a_title = wx.CheckBox(self, -1, _("Include <a> - 'title' attribute"))
        self.want_img_alt = wx.CheckBox(self, -1, _("Include <img> - 'alt' attribute"))
        self.want_input_value = wx.CheckBox(self, -1, _("Include <input> - 'value' attribute"))
        self.want_meta_description = wx.CheckBox(self, -1, _("Include <meta> - 'description' attribute"))
        self.want_meta_keywords = wx.CheckBox(self, -1, _("Include <meta> - 'keywords' attribute"))

        htmlprefs = model.get_html_seg_options()

        self.want_a_title.Value = htmlprefs.get("want_a_title")
        self.want_img_alt.Value = htmlprefs.get("want_img_alt")
        self.want_input_value.Value = htmlprefs.get("want_input_value")
        self.want_meta_description.Value = htmlprefs.get("want_meta_description")
        self.want_meta_keywords.Value = htmlprefs.get("want_meta_keywords")

    def get_prefs(self):
        htmlprefs = {}
        htmlprefs["want_a_title"] = self.want_a_title.Value
        htmlprefs["want_img_alt"] = self.want_img_alt.Value
        htmlprefs["want_input_value"] = self.want_input_value.Value
        htmlprefs["want_meta_description"] = self.want_meta_description.Value
        htmlprefs["want_meta_keywords"] = self.want_meta_keywords.Value
        return htmlprefs


class AnalysisPanel(wx.Panel, wizard.PreferencesBase):
    """Segmentation panel in options dialog
    """

    def __init__(self, parent):
        self.init_base(parent)

    def init_base(self, parent):
        """This is so we can subclass and override for testing
        """

        wx.Panel.__init__(self, parent)


class OptionsDialog(sc.SizedDialog):
    """The options dialog
    """

    def __init__(self, parent):
        self.init_base(parent)
        self.layout()


    def init_base(self, parent):
        sc.SizedDialog.__init__(self,
                                parent,
                                -1,
                                _('AnalyzeAssist Options'),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.THICK_FRAME,
                                size=(550, 400))

    def initIcon(self):

        icon = wx.EmptyIcon()
        p = resource_file_name("AnalyzeAssist.ico")
        icon.LoadFile(p, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def layout(self):
        """Perform layout on the dialog widgets
        """

        pane = self.GetContentsPane()
        self.SetTitle(_("AnalyzeAssist Options"))

        self.notebook = wx.Notebook(pane)
        self.notebook.SetSizerProps(expand=True, proportion=1)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        self.segmenterPanel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.segmenterPanel, _("Segmentation"))

        if MAKE_ANALYSIS_PANEL:
            self.analysisPanel = AnalysisPanel(self.notebook)
            self.notebook.AddPage(self.analysisPanel, _("Analysis"))

        self.html_options_panel = HtmlOptionsPanel(self.notebook)
        self.notebook.AddPage(self.html_options_panel, _("HTML Files"))

        self.checkbox = wx.CheckBox(self.segmenterPanel,
                                    -1,
                                    _("Count number-only segments"))
        self.checkbox.SetToolTipString(_("Select to include number-only segments in analysis"))

        self.checkbox.Value = model.get_analyze_numbers()

        self.segmenterPanel.sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.StaticBox(self.segmenterPanel, -1, _("File segmenters:"))
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        classDict = broker.Request("segmenter classes")

        self.fgs = wx.FlexGridSizer(rows=len(classDict.keys()),
                                    cols=2,
                                    hgap=15,
                                    vgap=5)

        self.addControlRows(classDict, broker.Request("segmenter extensions"))

        self.fgs.AddGrowableCol(1)
        bsizer.Add(self.fgs, flag=wx.ALL | wx.EXPAND)

        vsz = self.segmenterPanel.sizer
        vsz.Add(bsizer, border=5, proportion=1, flag=wx.EXPAND)

        vsz.Add(wx.StaticText(self.segmenterPanel, -1, u" "))
        vsz.Add(self.checkbox, border=5)
        vsz.Add(wx.StaticText(self.segmenterPanel, -1, u" "))

        self.segmenterPanel.SetSizer(vsz)
        vsz.Fit(self.segmenterPanel)

        if MAKE_ANALYSIS_PANEL:
            self.analysisPanel.sizer = wx.BoxSizer(wx.VERTICAL)
            self.analysisPanel.SetSizer(self.analysisPanel.sizer)
            broker.Request("make analysis options page", self.analysisPanel)

        self.Fit()
        self.initIcon()

    def getExtensions(self):
        return [(x.Label, y.Value) for (x, y) in self.valuePairs]

    def addControlRows(self, classDict, extensionDict):
        self.valuePairs = []
        for i, key in enumerate(classDict.keys()):
            klass = classDict[key]
            extensions = extensionDict.get(key)
            if extensions:
                self.addControlRow(klass, extensions)

    def addControlRow(self, klass, extensions):
        staticControl = wx.StaticText(self.segmenterPanel,
                                      -1,
                                      str(klass()))
        staticControl.SetToolTipString(_("Extensions for files of type %s") % str(klass()))

        textControl = wx.TextCtrl(self.segmenterPanel,
                                  -1,
                                  extensions,
                                  size=(200, -1))

        self.valuePairs.append((staticControl, textControl))
        self.fgs.Add(staticControl)
        self.fgs.Add(textControl, flag=wx.EXPAND)

    def html_pefs(self):
        return self.html_options_panel.get_prefs()

    def analyze_numbers(self):

        return self.checkbox.Value


def getOptionsDialog():
    return OptionsDialog(broker.Request("frame"))


if __name__ == '__main__':  #pragma: no cover
    from AnalyzeAssist import model

    application = wx.PySimpleApp()

    # create instance of class MyFrame
    broker.Register("get_text", lambda: unicode(broker.CurrentData(), "utf-8"))
    window = OptionsDialog(None)
    window.ShowModal()
    window.Destroy()
