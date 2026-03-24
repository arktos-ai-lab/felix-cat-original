# coding: UTF8
"""
The About box

Displays the about page in an IE window.

"""
import logging
from AnalyzeAssist import broker
from AnalyzeAssist import broadcaster
import wx

from wx.lib import iewin

from wx.lib import sized_controls as sc
from AnalyzeAssist.AppUtils import resource_file_name
from AnalyzeAssist import model
_ = model._

ICON_FILENAME = "AnalyzeAssist.ico"
JAPANESE_PAGE = "AboutJ.html"
ENGLISH_PAGE = "AboutE.html"
LOGGER = logging.getLogger(__name__)


class AboutBox(sc.SizedDialog):
    """The About dialog for the AnalyzeAssist application.
    
    Shows an About page in an iewin.IEHtmlWindow.
    Parses link clicks with hash ("#") symbols, and generates
    broadcaster events from them. (Thus, <a href="#on_help">Show Help</a>
    would generate the same event as the Help menu/toolbar command
    """

    def __init__(self, parent, page_file, icon_file=None):
        self.ie = None
        sc.SizedDialog.__init__(self,
                                parent,
                                -1,
                                _('About AnalyzeAssist'),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                                size=(500, 400))

        self.layout(page_file)

        if icon_file:
            self.init_icon(icon_file)

    def init_icon(self, icon_file):
        """Loads the program icon into the dialog"""

        icon = wx.EmptyIcon()
        icon.LoadFile(icon_file, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def layout(self, page_file):
        """Performs the layout of GUI widgets"""

        pane = self.GetContentsPane()

        self.ie = iewin.IEHtmlWindow(pane)
        self.ie.SetSizerProps(expand=True, proportion=1)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK))

        self.ie.Navigate(page_file)

        self.ie.AddEventSink(self)

    def BeforeNavigate2(self, this, pDisp, URL, Flags, TargetFrameName,
                        PostData, Headers, Cancel):
        debug(u'BeforeNavigate2: %s' % URL[0])
        Cancel[0] = OnBeforeNavigate2(URL[0])


def OnBeforeNavigate2(URL):
    """Hook link click events"""
    debug(u"Link clicked in About dialog: %s" % URL)

    if '#' in URL:
        title = URL.split('#')[-1]
        broadcaster.Broadcast("event", title, URL)
        return True
    return False


def get_page(language):
    """Get the about page for the specified language"""

    if language == "Japanese":
        return resource_file_name(JAPANESE_PAGE)
    else:
        return resource_file_name(ENGLISH_PAGE)


def get_about_box(frame):
    """Broker provider of AboutBox instance"""

    icon_file = resource_file_name(ICON_FILENAME)
    page_file = get_page(broker.Request("language"))
    return AboutBox(frame, page_file, icon_file)


if __name__ == '__main__':  #pragma: no cover
    from AnalyzeAssist import model

    application = wx.PySimpleApp()

    broker.Register("get_text", lambda: unicode(broker.CurrentData(), "utf-8"))
    window = get_about_box(None)
    window.ShowModal()
    window.Destroy()

    application.MainLoop()
