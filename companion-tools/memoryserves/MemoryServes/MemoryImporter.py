#coding: UTF8
"""
Utility for importing memory files to Memory Serves server

"""
import os
import urllib2
import traceback
import logging


def set_up_logging(loc, logging):
    """
    Configures logging according to whether we are frozen.

    When the app is not frozen, set level to debug.
    """

    if loc.we_are_frozen():
        format = '%(asctime)-15s %(name)s %(message)s'
        message_file = loc.get_log_file("memory_importer.log")
        logging.basicConfig(filename=message_file, format=format)

    else:
        format = '%(asctime)-15s %(name)s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=format)

import loc
set_up_logging(loc, logging)

import wx
import wx.lib.sized_controls as sc
import wx.lib.delayedresult as delayedresult

from mem_parser import get_root, get_head, get_records
import model
import settings
import dataloader
from gui import window

__version__ = "1.1"
__author__ = "Ryan Ginstrom"
__license__ = "MIT"

FIELDS = [("name", u"Name:"),
          ("memtype", u"Type:"),
          ("creator", u"Created by:"),
          ("created_on", u"Created on:"),
          ("modified_by", u"Modified by:"),
          ("modified_on", u"Last modified:"),
          ("client", u"Client:"),
          ("source_language", u"Source language:"),
          ("target_language", u"Target language:"),
          ("notes", u"Notes:"),
          ("num_records", u"Record count:")]

def get_fileobj(filename):
    return open(filename)


def load_model_data():
    dataloader.load_data(None)


class MemoryImporterFrame(window.WrappedWindow):
    def __init__(self, wxlib, sclib):
        self.wxlib = wxlib
        self.sclib = sclib
        style = (wx.DEFAULT_FRAME_STYLE |
                 wx.SUNKEN_BORDER |
                 wx.CLIP_CHILDREN)
        width, height = 600, 500
        logging.debug("Initializing frame")
        frame = sclib.SizedFrame(None, -1, u"Memory Importer", size=(width, height),
                                 style=style)
        window.WrappedWindow.__init__(self, frame)

        pane = self.GetContentsPane()
        pane.SetSizerType("vertical")

        label = self.wxlib.StaticText(pane, -1, u"Select a Memory or Glossary File")
        font = self.wxlib.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL)
        label.SetFont(font)

        row_one = self.sclib.SizedPanel(pane)
        row_one.SetSizerType("horizontal")
        row_one.SetSizerProps(expand=True)

        self.text_control = self.wxlib.TextCtrl(row_one)
        self.text_control.SetSizerProps(expand=True, proportion=3)
        self.browse_button = self.wxlib.Button(row_one, -1, u"&Browse")
        self.browse_button.ToolTip = self.wxlib.ToolTip(u"Select the TM file")
        self.browse_button.SetSizerProps(halign="right")
        self.Bind(wx.EVT_BUTTON,
                  self.OnBrowse,
                  self.browse_button)

        self.import_button = self.wxlib.Button(pane, -1, u"&Import")
        self.import_button.Enabled = False
        self.Bind(wx.EVT_BUTTON,
                  self.OnImport,
                  self.import_button)

        label = self.wxlib.StaticText(pane, -1, u"TM Info")
        font = self.wxlib.Font(15, self.wxlib.SWISS, self.wxlib.NORMAL, self.wxlib.NORMAL)
        font.Weight = wx.BOLD
        label.SetFont(font)

        info_panel = self.sclib.SizedPanel(pane)
        info_panel.SetSizerType("form")
        info_panel.SetSizerProps(expand=True)

        self.info_controls = {}
        for key, name in FIELDS:
            self.wxlib.StaticText(info_panel, -1, name)
            self.info_controls[key] = self.wxlib.TextCtrl(info_panel, -1)
            self.info_controls[key].SetSizerProps(expand=True)

        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-5, -5])
        self.statusbar.SetStatusText(u"Ready", 0)
        self.statusbar.SetStatusText(u"Memory Importer v %s" % __version__, 1)

        self.init_menu()

        self.Fit()
        self.SetMinSize(self.GetSize())

        self.jobID = 1

        self.root = None
        self.head = None
        self.filename = None

    def init_menu(self):
        """Create the menu"""

        menu_bar = self.wxlib.MenuBar()
        file_menu = self.wxlib.Menu()
        menu_bar.Append(file_menu, "&File")

        menu_items = {}
        # file menu
        menu_items[self.OnBrowse] = file_menu.Append(self.wxlib.NewId(),
                                                     u"&Open\tCtrl+O",
                                                     u"Select a memory file")

        file_menu.AppendSeparator()

        menu_items[self.OnClose] = file_menu.Append(self.wxlib.NewId(),
                                                    u"&Exit",
                                                    u"Exit Memory Importer")

        for key, item in menu_items.items():
            self.Bind(self.wxlib.EVT_MENU, key, item)

        self.SetMenuBar(menu_bar)

    def OnClose(self, event):
        self.Close()

    def update_head(self):
        mem_value = self.info_controls["memtype"].Value
        if mem_value:
            memtype = mem_value.lower()[0]
        else:
            memtype = "m"

        if memtype == u"g":
            self.head["memtype"] = memtype
        else:
            self.head["memtype"] = u"m"

        fields = [(key, name) for key, name in FIELDS if key != "memtype"]
        for key, name in fields:
            self.head[key] = self.info_controls[key].Value

    def OnImport(self, event):

        self.import_button.Enabled = False
        self.update_head()
        self.jobID += 1
        delayedresult.startWorker(self._consume_results,
                                  self._import_memory,
                                  wargs=(self.jobID,),
                                  jobID=self.jobID)

    def _import_memory(self, jobID):
        """
        Import the memory in a different thread, so the
        UI will stay responsive.
        """

        try:
            logging.debug("_import_memory: Loading data...")
            self.statusbar.SetStatusText(u"Loading data...", 0)
            load_model_data()

            self.head.update(settings.get_prefs())

            mem = model.TranslationMemory(self.head)
            memid = model.get_next_memid()
            mem.id = memid
            mem.mem["records"] = {}
            mem.mem['id'] = memid
            model.Data.memories[memid] = mem

            num_records = self.head["num_records"]
            records = mem.mem["records"]

            for i, record in enumerate(get_records(self.root)):
                if not i % 10:
                    msg = u"Record %s of %s" % (i, num_records)
                    self.statusbar.SetStatusText(msg, 0)

                rec = model.MemoryRecord(**record)
                key = model.MAKE_KEY(dict(source=rec.source, trans=rec.trans))
                rec.id = model.get_next_recid()
                rec.memory_id = memid
                # converting record to dict
                records[key] = model.rec2d(rec)

            self.statusbar.SetStatusText(u"Committing changes...", 0)

            dataloader.do_save()

            self.statusbar.SetStatusText(u"Finished importing %(name)s" % self.head, 0)

        except Exception, details:
            self.statusbar.SetStatusText(u"Error: %s" % details, 0)

        self.import_button.Enabled = True
        return jobID

    def _consume_results(self, delayedResult):
        pass

    def OnBrowse(self, event):
        logging.debug("Browsing for TM file")
        dlg = self.wxlib.FileDialog(
            self.window, message="Select TM or Glossary File",
            defaultFile="",
            wildcard='|'.join(["Memory Files |*.ftm;*.fgloss;*.xml",
                               "All Files (*.*)|*.*"]),
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            self.filename = dlg.GetPaths()[0]
            self.text_control.Value = self.filename
            self.text_control.SetInsertionPointEnd()

            self.browse_button.Enabled = False

            self.statusbar.SetStatusText(u"Loading file %s" % self.filename, 0)

            self.gather_info()

        else:
            logging.debug("Cancelled source file selection")
            self.statusbar.SetStatusText("Cancelled file selection", 0)

    def gather_info(self):
        self.jobID += 1
        delayedresult.startWorker(self._consume_results,
                                  self._gather_import,
                                  wargs=(self.jobID,),
                                  jobID=self.jobID)

    def _gather_import(self, jobID):

        self.statusbar.SetStatusText(u"Gathering file information...", 0)

        try:

            for key, item in self.info_controls.iteritems():
                item.Value = u""

            tm = get_fileobj(self.filename)
            self.root = get_root(tm)
            self.head = get_head(self.root)

            if self.head["is_memory"].lower() == "true":
                self.head["memtype"] = "m"
                self.info_controls["memtype"].Value = "Memory"
            else:
                self.head["memtype"] = "g"
                self.info_controls["memtype"].Value = "Glossary"
            self.head["name"] = os.path.split(self.filename)[-1]

            fields = [(key, name) for key, name in FIELDS if key != "memtype"]
            for key, name in fields:
                self.info_controls[key].Value = self.head.get(key) or u""

            self.statusbar.SetStatusText(u"Ready to import file", 0)
            self.import_button.Enabled = True

        except Exception, details:
            logging.exception("Error gathering import")
            self.statusbar.SetStatusText(u"Error: %s" % details, 0)

        finally:
            self.browse_button.Enabled = True

        return jobID


def main():
    """
    Run when file is called as main
    """

    logging.info("Launching Memory Importer application.")

    url = "http://%s:%s/" % (settings.get_host(), settings.get_port())
    try:
        urllib2.urlopen(url)
    except:
        logging.debug("Creating main window")
        app = wx.App(False)

        frame = MemoryImporterFrame(wx, sc)
        frame.CenterOnScreen()
        frame.Show()
        app.MainLoop()

    else:
        logging.warn("Memory Serves is running. Exiting Memory Importer.")
        app = wx.App()

        msg = 'Please quit from Memory Serves before running this application'
        dlg = wx.MessageDialog(None,
                               msg,
                               'Memory Importer',
                               wx.OK | wx.ICON_WARNING
        )
        dlg.ShowModal()
        dlg.Destroy()


# =============================
# main caller
# =============================
if __name__ == '__main__': # pragma nocover
    main()
