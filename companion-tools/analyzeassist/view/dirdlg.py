# -*- coding: utf8 -*-
"""
AddDirDialog class

"""
import logging
import wx
from wx.lib import sized_controls as sc
import glob
import os
from AnalyzeAssist import model
_ = model._

LOGGER = logging.getLogger(__name__)


def get_filters():
    return [_("All Files (*.*)"),
            _("MS Word (*.doc)"),
            _("MS Excel (*.xls, *.csv)"),
            _("MS PowerPoint (*.ppt)"),
            _("Text Files (*.txt)"),
            _("XML Files (*.xml)"),
            _("HTML Files (*.html, *.htm)"),
            _("PDF Files (*.pdf)"),
    ]


def get_filter_values():
    return dict(enumerate([["*.*"],
                           [".doc"],
                           [".xls", ".csv"],
                           [".ppt"],
                           [".txt"],
                           [".xml"],
                           [".html", ".htm"],
                           [".pdf"]]))


class AddDirDialog(sc.SizedDialog):
    def __init__(self, parent, initial_dir=u""):
        sc.SizedDialog.__init__(self,
                                parent,
                                wx.NewId(),
                                _("Add Directory"),
                                size=(700, 300),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        pane = self.GetContentsPane()
        pane.SetSizerType("grid", {"cols": 2})

        # first row
        dir_label = wx.StaticText(pane, -1, _("Directory: "))
        row = sc.SizedPanel(pane)
        row.SetSizerType("horizontal")
        row.SetSizerProps(expand=True)
        self.dir_edit = wx.TextCtrl(row, -1, initial_dir)
        browse = wx.Button(row, -1, _("Browse..."))
        browse.SetToolTipString(_("Browse for a folder to include"))
        self.Bind(wx.EVT_BUTTON,
                  self.OnBrowseDir,
                  browse)

        dir_label.SetSizerProps(halign="left")
        self.dir_edit.SetSizerProps(expand=True, proportion=1)
        browse.SetSizerProps(halign="right")

        prefs = model.get_preferences()

        # second row
        wx.StaticText(pane, -1, _("Files of type: "))
        self.filter = wx.ListBox(pane, wx.NewId(), (320, 50), (90, 120), get_filters(), wx.LB_EXTENDED)
        self.filter.SetSizerProps(expand=True, proportion=1)
        self.filter.SetSelection(0)

        # third row
        wx.StaticText(pane, -1, u"")
        self.recurse = wx.CheckBox(pane, wx.NewId(), _("Recurse subdirectories"))
        self.recurse.Value = bool(prefs.get("recurse_subdirs"))
        self.Bind(wx.EVT_CHECKBOX, self.OnRecurseChecked, self.recurse)
        self.recurse.SetToolTipString(_("Select this checkbox to include files in subfolders"))

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))
        self.MinSize = (500, 200)
        self.Fit()

        self.dir_edit.SetSelection(0, 0)
        self.dir_edit.SetFocus()

    def OnBrowseDir(self, event):
        LOGGER.debug("Browsing directory")
        dlg = wx.DirDialog(self,
                           _("Choose a directory:"),
                           style=wx.DD_DEFAULT_STYLE
                           # | wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            self.dir_edit.Value = dlg.GetPath()

        dlg.Destroy()

    def OnRecurseChecked(self, event):
        model.set_preference("recurse_subdirs", self.recurse.Value)

    def passes_filter(self, filename):
        selected = self.filter.GetSelections()
        if 0 in selected:
            return True

        values = get_filter_values()
        filter_vals = []
        for key, val in values.items():
            if key in selected:
                filter_vals.extend(val)
        ext = os.path.splitext(filename)[-1].lower()
        if not ext:
            return False
        return any(ext in x for x in filter_vals)

    def filter_filenames(self, filenames):
        return [x for x in filenames if self.passes_filter(x)]

    def get_files(self):
        print " ... retrieving files from dir dialog"
        if not self.dir_edit.Value:
            return []

        # recurse subdirs
        if self.recurse.Value:
            filenames = []
            for root, dirs, files in os.walk(self.dir_edit.Value):
                for name in files:
                    if self.passes_filter(name):
                        filename = os.path.join(root, name)
                        filenames.append(filename)
                wx.Yield()
            return filenames

        # Selected dir only
        filenames = glob.glob(os.path.join(self.dir_edit.Value, u"*"))
        return self.filter_filenames(filenames)


def main():
    app = wx.PySimpleApp()

    dlg = AddDirDialog(None)

    if dlg.ShowModal() == wx.ID_OK:
        print "Dialog completed successfully"
        for filename in dlg.get_files():
            print " ...", filename.encode("utf-8")
    else:
        print "Dialog was cancelled"

    dlg.Destroy()


if __name__ == "__main__":
    main()
