#encoding: UTF8
"""
Main module for Memory Serves Exporter.

This application downloads TMs and glossaries from a running Memory Serves instance.
Supply a connection string and a save location, and it will scrape the site for the records.
"""

import sys
import os
import traceback
import wx
import wx.lib.sized_controls as sc
from MemoryServesExporter import exportdata
from MemoryServesExporter import loc
import winpaths

__version__ = "1.0"
__author__ = 'Ryan Ginstrom'

def _(msg):
    """
    Localization stub.
    """
    return unicode(msg)


def msg_box(parent, title, message, style, wx_provider):
    """
    Display a generic message box.
    Wrap this so that we don't have to deal with the ShowModal/Destroy code.
    """
    dlg = wx_provider.MessageDialog(parent,
                                    title,
                                    message,
                                    wx_provider.OK | style
                           #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
    )
    dlg.ShowModal()
    dlg.Destroy()

def warning_msg(parent, message, title, wx_provider):
    """
    Display a warning message box.
    """
    msg_box(parent, title, message, wx_provider.ICON_EXCLAMATION, wx_provider)

def info_msg(parent, message, title, wx_provider):
    """
    Display an informational message box.
    """
    msg_box(parent, title, message, wx_provider.ICON_INFORMATION, wx_provider)

def is_valid_connection(conn_string):
    """
    Returns whether the string is a valid connection.
    To be valid, it must return valid MemoryServes TM info on URL connect.
    """
    source = exportdata.DataSource(conn_string)
    try:
        data = source.get_data()
    except Exception, e:
        return False
    if not isinstance(data, dict):
        return False
    if not "info" in data:
        return False
    return data["info"].startswith("http")

class MemoryExporterAbortException(Exception):
    """
    Use this to abort from the export operation.
    """
    pass

class ProgressCallback(object):
    def __init__(self, parent, provider):
        self.parent = parent
        self.provider = provider
        self.dlg = None
        self.max_value = 0
        self.current = 0
        self.running = False

    def initialize(self, max_value):
        self.max_value = max_value

        wxlib = self.provider
        self.dlg = wxlib.ProgressDialog(_("Exporting Memory Serves Repo"),
                             _("Initializing data..."),
                             maximum = self.max_value,
                             parent=self.parent,
                             style = wxlib.PD_CAN_ABORT
                                        | wxlib.PD_APP_MODAL
                                        | wxlib.PD_ELAPSED_TIME
                                        | wxlib.PD_REMAINING_TIME
                                        | wxlib.PD_AUTO_HIDE
        )
        self.running = True

    def update(self):
        self.current += 1
        update_val = min(self.current, self.max_value)
        msg = _("Exported %s of %s records") % (update_val, self.max_value)
        (keep_going, dontcare) = self.dlg.Update(update_val, msg)
        if not keep_going:
            raise MemoryExporterAbortException(_("User aborted export"))

    def finalize(self):
        if self.dlg and self.running:
            self.dlg.Destroy()
            self.running = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.dlg:
            self.dlg.Destroy()
            self.running = False



class MemoryExporterFrame(sc.SizedFrame):
    """
    The main program frame
    """

    def __init__(self, style):
        """
        Initialize the window
        """

        sc.SizedFrame.__init__(self,
                               None,
                               -1,
                               u"Memory Serves Exporter",
                               style=style)

        self.pane = self.GetContentsPane()

class MemoryExporterFrameController(object):
    """
    Wraps the window frame for dependency injection.
    """
    def __init__(self, frame, providers):
        """
        Set up frame window, bind events.
        """
        self.frame = frame
        self.providers = providers

        # initialize GUI control members
        self.connect_textbox = None
        self.test_btn = None
        self.filename_textbox = None
        self.browse_btn = None
        self.cancel_btn = None
        self.export_btn = None
        self.callback = None

        initialize_frame(self, self.frame.pane, self.providers.wx, self.providers.sc)

        self.frame.Bind(wx.EVT_BUTTON,
                        self.OnTestConnection,
                        self.test_btn)
        self.frame.Bind(wx.EVT_BUTTON,
                        self.OnBrowse,
                        self.browse_btn)
        self.frame.Bind(wx.EVT_BUTTON,
                        self.OnCancel,
                        self.cancel_btn)
        self.frame.Bind(wx.EVT_BUTTON,
                        self.OnExport,
                        self.export_btn)

        self.frame.SetMinSize((400, 300))
        self.frame.Fit()


    def OnTestConnection(self, event):
        """
        Test the connection string to make sure it is valid.
        """

        connection_string = self.connect_textbox.Value

        if is_valid_connection(connection_string):
            info_msg(self.frame,
                     _("Test Connection String"),
                     _("The connection string is valid."),
                     self.providers.wx)
        else:
            warning_msg(self.frame,
                        _("Test Connection String"),
                        _("The connection string is not valid."),
                        self.providers.wx)


    def get_wildcard(self):
        """
        The file dialog wildcard.
        """
        return "|".join([_("Felix Memory Files (*.ftm)|*.ftm"),
                             _("Felix Glossary Files (*.fgloss)|*.fgloss"),
                             _("XML Files (*.xml)|*.xml"),
                             _("All Files (*.*)|*.*")])

    def OnBrowse(self, event):
        """
        Browse for a file to save the TM/glossary to.
        """
        wxlib = self.providers.wx
        dlg = wxlib.FileDialog(
            self.frame,
            message=_("Save TM/Glossary to File"),
            defaultFile=self.filename_textbox.Value,
            wildcard=self.get_wildcard(),
            style=wxlib.SAVE | wxlib.CHANGE_DIR
        )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() != wxlib.ID_OK:
            dlg.Destroy()
            return

        self.filename_textbox.Value = dlg.GetPaths()[0]
        dlg.Destroy()


    def OnCancel(self, event):
        """
        User wants to quit.
        """

        self.frame.Close()

    def OnExport(self, event):
        """
        Export the connection string to the specified file.
        """
        filename = self.filename_textbox.Value
        try:
            out = open(filename, "w")
        except Exception, e:
            err_msg = _("Failed to open file %s:\n%s") % (filename, e)

            warning_msg(self.frame,
                        _("Export Failed"),
                        err_msg,
                        self.providers.wx)

            return

        conn_string = self.connect_textbox.Value
        if not is_valid_connection(conn_string):
            err_msg = _("Invalid connection string: %s") % conn_string

            warning_msg(self.frame,
                        _("Export Failed"),
                        err_msg,
                        self.providers.wx)
            return


        try:
            with ProgressCallback(self.frame, self.providers.wx) as callback:
                self.callback = callback
                exportdata.export(conn_string, out, self.callback)
                callback.finalize()
                num_records = callback.max_value
        except Exception, e:
            err_msg = _("Failed to export TM\n%s") % e

            warning_msg(self.frame,
                        _("Export Failed"),
                        err_msg,
                        self.providers.wx)

            return

        info_msg(self.frame,
                 _("Export Succeeded"),
                 _("Exported %s records to \n%s") % (num_records, filename),
                 self.providers.wx)

def initialize_frame(window, pane, wx_provider, sc_provider):
    # connect string
    create_connection_string_row(window, pane, wx_provider)
    # spacer
    wx_provider.StaticText(pane, -1, u"")
    # save to string
    create_save_row(window, pane, wx_provider)
    # spacer
    wx_provider.StaticText(pane, -1, u"")
    # export buttons
    create_export_button_row(window, pane, wx_provider, sc_provider)


def create_connection_string_row(window, pane, wx_provider):
    connect_label = wx_provider.StaticText(pane, wx.NewId(), _("Connection String"))
    connect_label.ToolTip = wx_provider.ToolTip(_("The Memory Serves connection string for the TM or glossary"))
    window.connect_textbox = wx_provider.TextCtrl(pane)
    window.connect_textbox.SetSizerProps(expand=True)
    window.test_btn = wx_provider.Button(pane, wx_provider.NewId(), _("&Test Connection"))
    window.test_btn.SetSizerProps(halign="right")

def create_save_row(window, pane, wx_provider):
    save_label = wx_provider.StaticText(pane, wx_provider.NewId(), _("Save to File"))
    save_label.ToolTip = wx_provider.ToolTip(_("Export the TM or glossary to this file"))
    window.filename_textbox = wx_provider.TextCtrl(pane)
    window.filename_textbox.SetSizerProps(expand=True)
    window.browse_btn = wx_provider.Button(pane, wx.NewId(), _("&Browse..."))
    window.browse_btn.SetSizerProps(halign="right")

def create_export_button_row(window, pane, wx_provider, sc_provider):
    button_row = sc_provider.SizedPanel(pane)
    button_row.SetSizerType("horizontal")
    button_row.SetSizerProps(expand=True, halign="right", valign="bottom", proportion=1)
    button_spacer = sc_provider.SizedPanel(button_row)
    button_spacer.SetSizerProps(expand=True, proportion=1)
    window.cancel_btn = wx_provider.Button(button_row, wx.NewId(), _("Close"))
    window.cancel_btn.SetSizerProps(halign="right", valign="bottom")
    window.export_btn = wx_provider.Button(button_row, wx.NewId(), _("&Export"))
    window.export_btn.SetSizerProps(halign="right", valign="bottom")


class MemoryExporterApp(wx.App):
    """
    The App class for our application
    """

    def __init__(self, redirect=True,
                    filename="log.txt",
                    useBestVisual=False,
                    clearSigInt=True):

        wx.App.__init__(self,
                        redirect,
                        filename,
                        useBestVisual,
                        clearSigInt)

    def OnInit(self):
        """
        Initialize the app
        """

        return initialize_app(self, MemoryExporterFrame, wx, sc)

class Providers(object):
    """
    Wraps our wx libraries
    """
    def __init__(self, wx_provider, sc_provider):
        self.wx = wx_provider
        self.sc = sc_provider

def initialize_app(app, frame_class, wx_provider, sc_provider):
    """
    Initialize the application object
    """
    style = (wx.DEFAULT_FRAME_STYLE |
             wx.SUNKEN_BORDER |
             wx.CLIP_CHILDREN)
    frame = frame_class(style)
    providers = Providers(wx_provider, sc_provider)
    MemoryExporterFrameController(frame, providers)
    frame.CenterOnScreen()
    app.SetTopWindow(frame)
    frame.Show()

    return True

def set_up_log():
    log_folder = os.path.join(winpaths.get_local_appdata(), "MemoryServesExporter")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    logfile = os.path.join(log_folder, "log.txt")
    sys.stdout = open(logfile, "w")


def main(app_class):
    """
    Call when run as main
    """

    # set up the log
    if loc.we_are_frozen():
        set_up_log()
    # create app and start main loop
    memory_app = app_class(False)
    memory_app.MainLoop()

if __name__ == '__main__': # pragma: no cover
    main(MemoryExporterApp)
