# coding: UTF8
"""
The main module

This is the main module for the AnalyzeAssist GUI front end.
It basically sticks a GUI on top of the analyze_files utility,
plus gives a GUI interface to the preference settings.

Since each module registers itself with
the broadcaster/broker on import, we must ensure the various modules are pulled
in here, so they will register themselves properly. (Otherwise, we will get
"no provider" errors, etc.)

"""
import logging

import wx
import model
import view
from view import frame
from view import options

__version__ = model.VERSION
__author__ = "Ryan Ginstrom"
logging.basicConfig(format="%(levelname)s: %(asctime)s : %(name)s(%(lineno)s): %(message)s",
                    level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

_ = model._
frame.__version__ = model.VERSION
FrameClass = view.frame.Frame

# =============================
# class AnalyzeAssistApp
# =============================
class AnalyzeAssistApp(wx.App):
    """The App class for our application"""

    def __init__(self, redirect=False,
                 use_best_visual=False,
                 clear_sig_int=True):
        self.init_base(redirect, use_best_visual, clear_sig_int)
        self.frame = None

    def init_base(self, redirect, use_best_visual, clear_sig_int):
        """Overridden in fake version"""

        wx.App.__init__(self,
                        redirect,
                        "log.txt",
                        use_best_visual,
                        clear_sig_int)

    def OnInit(self):
        """Initialize the app

        It would be nice at some point to remember the frame's size/position, and
        restore it on startup.
        """

        self.frame = FrameClass(parent=None,
                                title=_("AnalyzeAssist"),
                                size=(600, 550))
        self.frame.Size = (600, 550)
        self.frame.CenterOnScreen()
        self.SetTopWindow(self.frame)

        self.frame.Show()

        return True


def main():
    """Run if called as the main script"""

    # redirect output if we are frozen
    LOGGER.debug("*** Launching AnalyzeAssist ***")

    options.set_html_options()

    app = AnalyzeAssistApp()

    app.MainLoop()

# =============================
# main caller
# =============================
if __name__ == '__main__':  #pragma: no cover
    main()
