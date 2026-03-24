# coding: UTF8
"""
Enter module description here.

"""

import wx
import wx.grid
import wx.aui
import wx.lib.sized_controls as sc
import winpaths
import sys
import simplemapi
import os
import glob

__version__ = "1.1"

APP_NAME = "ShowLogs"

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 400


class LogViewer(sc.SizedDialog):
    def __init__(self, parent):
        sc.SizedDialog.__init__(self,
                                parent,
                                size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.Title = "Analyze Assist Log Viewer"
        self.SetMinSize(self.GetSize())

        pane = self.GetContentsPane()
        self.nb = wx.aui.AuiNotebook(pane)
        self.nb.SetSizerProps(expand=True, proportion=3)

        datapath = os.path.join(winpaths.get_local_appdata(), u"AnalyzeAssist")
        self.logfiles = sorted(glob.glob(os.path.join(datapath, u"*.log")))
        for logfile in self.logfiles:
            grid = wx.grid.Grid(self.nb)
            basename = os.path.basename(logfile)
            basename = os.path.splitext(basename)[0]
            self.nb.AddPage(grid, u" ".join([x.title() for x in basename.split(u"_")]))

            lines = open(logfile).readlines()
            grid.CreateGrid(len(lines), 3)
            for col, colname in enumerate(("Severity",
                                           "Time",
                                           "Message")):
                grid.SetColLabelValue(col, colname)

            err_color = "#FFCCCC"
            colors = dict(INFO="#CCFFCC",
                          DEBUG="#CCFFCC",
                          WARN="yellow",
                          ERROR=err_color)

            last_color = colors["INFO"]

            for row, line in enumerate(lines):
                try:
                    severity, timestamp, msg = line.split("\t")
                except ValueError:
                    severity, timestamp = u"", u""
                    msg = line
                grid.SetCellValue(row, 0, severity)
                grid.SetCellValue(row, 1, timestamp)
                grid.SetCellValue(row, 2, msg.decode("utf-8"))

                attr = wx.grid.GridCellAttr()
                if severity:
                    color = colors.get(severity, last_color)
                else:
                    color = colors.get("INFO", last_color)
                attr.SetBackgroundColour(color)

                if color == err_color:
                    attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

                last_color = color

                grid.SetRowAttr(row, attr)

                first_col_widths = grid.GetColSize(0) + grid.GetColSize(1) + 150
                grid.SetColSize(2, WINDOW_WIDTH - first_col_widths)

        # layout
        sizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        sizer.CancelButton.Label = "Cancel"
        sizer.AffirmativeButton.Label = "Send"
        self.SetButtonSizer(sizer)

        self.Fit()

        self.Bind(wx.EVT_INIT_DIALOG, self.OnInit, self)

    def OnInit(self, event):
        self.SetFocus()


def main(parent=None):
    app = wx.PySimpleApp()
    dlg = LogViewer(parent)
    if dlg.ShowModal() == wx.ID_OK:
        subject = "AnalyzeAssist Logs"
        try:
            version = os.path.join(winpaths.get_local_appdata(),
                                   u"AnalyzeAssist",
                                   u"version.txt")
            lines = open(version).readlines()
            keyval_pairs = (line.split("=") for line in lines)
            data = dict([(key.strip(), val.strip()) for key, val in keyval_pairs])
            subject = subject + " (ver. %s)" % data["version"]
        except IOError:
            print "No version info"

        body = "Sending AnalyzeAssist logs to support"
        attach = ";".join(dlg.logfiles)
        try:
            simplemapi.SendMail('support@felix-cat.com',
                                subject,
                                body,
                                attach)
        except:
            print "Failed to send logs"
    else:
        print "Cancel"
    dlg.Destroy()


if __name__ == "__main__":
    last = sys.argv[-1]
    langs = dict(en="en", English="en",
                 jp="jp", Japanese="jp")
    if last in langs:
        loc.language.change_language(langs[last])
    main()