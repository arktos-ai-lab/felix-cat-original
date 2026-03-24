# coding: UTF8
"""
Dialog to check for updates for Analyze Assist
"""
import os
import urllib2
import webbrowser
import socket
import urllib
import logging

import winsound
import wx
import wx.lib.sized_controls as sc
import winpaths

from AnalyzeAssist import model

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200

LOGGER = logging.getLogger(__name__)
APPNAME = u"AnalyzeAssist"
VERSION_URL = "http://ginstrom.com/AnalyzeAssist/version.txt"
_ = model._


class FailedToConnectDialog(sc.SizedDialog):
    def __init__(self, prefs):
        sc.SizedDialog.__init__(self,
                                prefs.get("parent"),
                                size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP)

        self.Title = _("Connection Failed")
        self.prefs = prefs

        pane = self.GetContentsPane()
        static_failed = wx.StaticText(pane, -1, _("Failed to connect to the Analyze Assist website."))
        static_failed.Font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        static_failed.ForegroundColour = 'Red'

        wx.StaticText(pane, -1, u"")

        static_settings = wx.StaticText(pane, -1, _("Current Settings:"))
        static_settings.Font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD)

        self.proxy_static = wx.StaticText(pane, -1, _("HTTP Proxy: %s") % prefs.get("http_proxy"))
        self.proxy_static.Font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)

        input_button = wx.Button(pane, -1, _("Set HTTP Proxy"))
        self.Bind(wx.EVT_BUTTON, self.on_input, input_button)

        self.pac_static = wx.StaticText(pane, -1, _("PAC File: %s") % prefs.get("pac_file"))
        self.pac_static.Font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)

        browse_button = wx.Button(pane, -1, _("Browse for PAC File..."))
        self.Bind(wx.EVT_BUTTON, self.on_browse, browse_button)
        wx.StaticText(pane, -1, u"")

        retry_static = wx.StaticText(pane, -1, _("Click [Retry], or click [Cancel] to abort."))
        retry_static.Font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL)

        sizer = self.CreateStdDialogButtonSizer(wx.YES | wx.CANCEL)
        sizer.AffirmativeButton.Label = _("Retry")
        sizer.CancelButton.Label = _("Abort")
        self.SetButtonSizer(sizer)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnInit, self)

        self.Fit()

    def on_input(self, event):
        LOGGER.debug("Entering proxy value...")
        dlg = wx.TextEntryDialog(
            self, _("Type the HTTP proxy value"),
            _("Enter HTTP Proxy"))

        dlg.SetValue(self.prefs.get("http_proxy") or "")

        if dlg.ShowModal() == wx.ID_OK:
            self.prefs["http_proxy"] = dlg.GetValue() or None
            LOGGER.debug("New proxy value: %s" % self.prefs["http_proxy"])
            self.proxy_static.Label = _("HTTP Proxy: %s") % self.prefs.get("http_proxy")
        dlg.Destroy()

    def on_browse(self, event):
        LOGGER.debug("Browsing for PAC file...")
        dlg = wx.FileDialog(
            self,
            message=_("Select Files"),
            defaultFile="",
            wildcard=_("All Files (*.*)|*.*"),
            style=wx.OPEN | wx.CHANGE_DIR)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python file_list of files that were selected.
            path = dlg.GetPath()

            self.prefs["pac_file"] = path or None
            LOGGER.debug("New PAC file value: %s" % self.prefs["pac_file"])
            self.pac_static.Label = _("PAC File: %s") % self.prefs.get("pac_file")

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

    def OnInit(self, event):
        self.SetFocus()
        winsound.MessageBeep(winsound.MB_ICONASTERISK)


class AskToCheckDialog(sc.SizedDialog):
    def __init__(self, parent, ask_about_updates=False):
        sc.SizedDialog.__init__(self,
                                parent,
                                size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP)

        self.Title = _("Check for Updates")

        pane = self.GetContentsPane()
        message = wx.StaticText(pane, -1, _("Would you like to check online for updates?"))

        message = wx.StaticText(pane, -1, u"\n\n")
        self.dontask = checkbox = wx.CheckBox(pane, -1, _("Don't ask me again"))
        self.dontask.Value = ask_about_updates
        sizer = self.CreateStdDialogButtonSizer(wx.YES | wx.CANCEL)
        sizer.AffirmativeButton.Label = _("Check")
        sizer.CancelButton.Label = _("Don't Check")
        self.SetButtonSizer(sizer)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnInit, self)

        self.Fit()

    def OnInit(self, event):
        self.SetFocus()


def get_this_version_info():
    localapp = winpaths.get_local_appdata()
    appdata_folder = os.path.join(localapp, APPNAME)
    filename = os.path.join(appdata_folder, u"version.txt")
    return linestodata(open(filename))


def linestodata(lines):
    valpairs = (line.split("=") for line in lines)
    return dict((key.strip(), val.strip()) for key, val in valpairs)


def fetchurl(pac, url):
    return urllib.urlopen(url)


def isproxyalive(proxy):
    host_port = proxy.split(":")
    if len(host_port) != 2:
        error('Proxy host is not defined as host:port')
        return False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    try:
        s.connect((host_port[0], int(host_port[1])))
    except Exception, e:
        LOGGER.exception('Proxy %s is not accessible' % proxy)
        return False
    s.close()
    return True


def failed_message(prefs):
    dlg = FailedToConnectDialog(prefs)
    if dlg.ShowModal() == wx.ID_YES:
        LOGGER.debug("Retry with new proxy/pac info")
        prefs["abcdef"] = True
        data = get_latest_version_info(prefs)
    else:
        LOGGER.debug("User canceled web connection")
        data = None
    dlg.Destroy()
    return data


DEBUG_KEY = "abcdef"


def get_latest_version_info(prefs):
    """
    Retrieve the version text file from the server
    """

    if prefs.get("http_proxy"):
        try:
            proxies = dict(http=prefs["http_proxy"])
            return linestodata(urllib.urlopen(VERSION_URL, proxies=proxies))
        except:
            LOGGER.exception("Failed to get URL with assigned proxy")
            return failed_message(prefs)

    if prefs.get("pac_file"):
        try:
            return linestodata(fetchurl(prefs["pac_file"], VERSION_URL))
        except:
            logg_err("Failed to get URL with assigned PAC file")
            del prefs["pac_file"]
            return failed_message(prefs)

    LOGGER.debug("Downloading version file")
    try:
        fp = urllib2.urlopen(VERSION_URL)
        return linestodata(fp)
    except:
        LOGGER.exception("Failed to open URL '%s'" % VERSION_URL)
        return linestodata(failed_message(prefs))


def latest_is_newer(this, latest):
    this_version = this["version"]
    latest_version = latest["version"]
    tbits, lbits = this_version.split("."), latest_version.split(".")
    for a, b in zip(tbits, lbits):
        if int(a) < int(b):
            return True
        elif int(a) > int(b):
            return False
    return len(tbits) < len(lbits)


def check_updates(prefs):
    """
    Check onnline for updates.
    If there are no updates, inform the user if we're interactive.
    If there is an update, ask user to go to download page.
    """

    this = get_this_version_info()
    latest = get_latest_version_info(prefs)
    if not latest:
        warn("Failed to retrieve latest version information")
        return
    if not latest_is_newer(this, latest):
        if prefs["ask_about_updates"]:
            dlg = wx.MessageDialog(None, _("Version %s is the latest version") % this["version"],
                                   _("Analyze Assist Update Check"),
                                   wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP
                                   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
            )
            dlg.ShowModal()
            dlg.Destroy()
        return

    LOGGER.debug("There is a newer version: %s" % latest["version"])
    ask_to_download(latest, prefs)


def ask_to_download(latest, prefs):
    line1 = _("There is a new version of Analyze Assist: %s") % latest["version"]
    message = "\n".join([line1,
                         _("Visit download page?")])
    dlg = wx.MessageDialog(None, message,
                           _("Analyze Assist Update Check"),
                           wx.YES | wx.NO | wx.ICON_INFORMATION | wx.STAY_ON_TOP
                           #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
    )
    if dlg.ShowModal() == wx.ID_YES:
        webbrowser.open(_("http://ginstrom.com/AnalyzeAssist/"))
    dlg.Destroy()


def ask_permission(parent, props):
    """
    Ask user for permission to make online check
    """
    LOGGER.debug("Asking user for permission to go online")
    dlg = AskToCheckDialog(parent, not props["ask_about_updates"])
    if dlg.ShowModal() == wx.ID_YES:
        LOGGER.debug("Use says to check for updates.")
        props["check_updates"] = True
        props["parent"] = parent
        check_updates(props)
    else:
        LOGGER.debug("User says not to check for updates")
        props["check_updates"] = False
    props["ask_about_updates"] = not dlg.dontask.Value


