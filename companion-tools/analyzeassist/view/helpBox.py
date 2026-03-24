# coding: UTF8
"""
The Help viewer

Uses the same basic code as L{about.AboutBox}
"""
import logging
from AnalyzeAssist import broadcaster
import wx

from wx.lib import iewin

import os
from wx.lib import sized_controls as sc
from AnalyzeAssist.AppUtils import resource_file_name
from AnalyzeAssist import model
_ = model._

LOGGER = logging.getLogger(__name__)


class HelpBox(sc.SizedDialog):
    def __init__(self, parent, size=(500, 600)):

        sc.SizedDialog.__init__(self,
                                parent,
                                -1,
                                _('AnalyzeAssist Help'),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                                size=size)
        self.layout()

    def show_content(self, ie):
        basePath = os.path.join(module_path(), "help")
        helpPath = os.path.join(basePath, "en")
        ie.Navigate(os.path.join(helpPath, "index.html"))

    def layout(self):
        pane = self.GetContentsPane()

        self.ie = iewin.IEHtmlWindow(pane)
        self.ie.SetSizerProps(expand=True, proportion=1)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK))

        self.show_content(self.ie)
        self.ie.AddEventSink(self)

        self.set_icon()

    def set_icon(self):
        icon = wx.EmptyIcon()
        p = resource_file_name("AnalyzeAssist.ico")
        icon.LoadFile(p, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def BeforeNavigate2(self, this, pDisp, URL, Flags, TargetFrameName,
                        PostData, Headers, Cancel):
        url = URL[0]
        LOGGER.debug(u'Link clicked in help box: %s' % url)

        if u"#" in url:
            title = linkinfo.URL.split('#')[-1]
            broadcaster.Broadcast("event", title, linkinfo)
            Cancel[0] = True

        else:
            Cancel[0] = False


def get_help_box(frame):
    """Reponse to broker request for help box"""

    return HelpBox(frame)


def run_as_main():
    """
    Called when run as main -- demo help box
    """

    wx.PySimpleApp()

    # create instance of class MyFrame
    window = HelpBox(None)
    window.ShowModal()
    window.Destroy()


if __name__ == '__main__':  #pragma: no cover
    run_as_main()
