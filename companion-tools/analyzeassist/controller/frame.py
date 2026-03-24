# coding: UTF8
"""
Frame controller

Listens for events from the frame window, and handles them appropriately.

"""
import logging

from AnalyzeAssist import broadcaster
from AnalyzeAssist import broker
from AnalyzeAssist.broker import BrokerRequestHandler
import os
from AnalyzeAssist.broadcaster import EventHandlerFunction as EventHandler
import wx
from AnalyzeAssist.AppUtils import module_path, get_local_app_data_folder
from AnalyzeAssist.view import about
import wx.lib.dialogs
from AnalyzeAssist.view import update_checker
from datetime import date
from AnalyzeAssist import model
from AnalyzeAssist.view import options
from AnalyzeAssist.view import helpBox

LOGGER = logging.getLogger(__name__)


@BrokerRequestHandler("license file")
def get_license_filename():
    """
    Gets the license agreement filename, depending on the GUI language
    """

    language = model.get_language()

    if language == "Japanese":
        licfile = "MITLicenseJ.txt"
    else:
        licfile = "MITLicense.txt"

    filename = os.path.join(get_local_app_data_folder(), licfile)
    if not os.path.exists(filename):
        modfile = os.path.join(module_path(), licfile)
        if os.path.exists(modfile):
            shutil.copy(modfile, filename)
    return filename


# Help menu
@EventHandler("event", "on_about")
def on_about():
    """
    Handles the on_about broadcast by showing the About dialog
    """

    about_box = about.get_about_box(broker.Request("frame"))
    about_box.ShowModal()
    about_box.Destroy()


@EventHandler("event", "on_license")
def on_license():
    """
    Handles the on_license broadcast by showing the License dialog
    """

    license_filename = broker.Request('license file')
    license_text = unicode(open(license_filename, "r").read(), "utf8")
    frame = broker.Request("frame")
    dlg = wx.lib.dialogs.ScrolledMessageDialog(frame,
                                               license_text,
                                               _("AnalyzeAssist License"))
    dlg.ShowModal()
    dlg.Destroy()


@EventHandler("event", "on_help")
def on_help():
    """
    Shows help for the program
    """

    LOGGER.debug("Showing help for AnalyzeAssist")

    help_box = helpBox.get_help_box(broker.Request("frame"))
    help_box.Show()


@EventHandler("event", "onAAHomePage")
def on_aa_homepage():
    """
    Launches the AnalyzeAssist website
    """

    import webbrowser

    webbrowser.open("http://www.ginstrom.com/AnalyzeAssist/")


# Tools menu
@EventHandler("event", "on_check_updates")
def on_check_updates():
    """
    Checks online for updates
    """

    LOGGER.debug("Checking for updates at user request")

    update_checker.check_updates(model.get_preferences())

    model.set_last_update(date.today())


# Tools menu
@EventHandler("event", "on_options")
def on_options():
    """
    Shows the Options dialog
    """

    options_dialog = options.getOptionsDialog()
    result = options_dialog.ShowModal()

    if result == wx.ID_OK:
        LOGGER.debug("User set application preferences")
        extensions = dict(options_dialog.getExtensions())
        LOGGER.debug("extensions: %s" % extensions)

        broadcaster.Broadcast("event",
                              "extension handlers changed",
                              extensions)

        prefs = options_dialog.analysisPanel.getAnalysisPreferences()
        match_ranges, fuzzy_options = prefs
        broadcaster.Broadcast("match ranges", "changed", match_ranges)
        model.set_fuzzy_options(fuzzy_options)

        analyze_numbers = options_dialog.analyze_numbers()
        model.set_analyze_numbers(analyze_numbers)
        html_prefs = options_dialog.html_pefs()
        model.set_html_seg_options(html_prefs)
        options.set_html_options(html_prefs)

    options_dialog.Destroy()


# File menu
@EventHandler(source='wizard', title='completed')
def on_analysis_wiz_complete():
    """
    Performs analysis after Analysis wizard completes
    """

    LOGGER.debug("Performing analysis...")
    broadcaster.Broadcast(source='analysis', title='wizard')


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
