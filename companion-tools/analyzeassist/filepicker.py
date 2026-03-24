# -*- coding: utf8 -*-
"""
dialog to pick files to count
"""

import wx
from wx.lib import sized_controls as sc
from AnalyzeAssist.view import filelist
import os
import model

_ = model._

filelist.FileList.columns = [_("File Name"),
                             _("Path")]


def get_wildcard():
    return '|'.join([_("All Files (*.*)|*.*"),
                     _("MS Word (*.doc)|*.doc"),
                     _("MS Excel (*.xls;*.csv)|*.xls;*.csv"),
                     _("MS PowerPoint (*.ppt)|*.ppt"),
                     _("Text Files (*.txt)|*.txt"),
                     _("XML Files (*.xml)|*.xml"),
                     _("HTML Files (*.html;*.htm)|*.html;*.htm"),
                     _("PDF Files (*.pdf)|*.pdf"),
    ])


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        """Respond to dropped files"""

        print "Dropped", len(filenames), "files"

        dirs = []
        for filename in filenames:
            if os.path.isdir(filename):
                dirs.append(filename)
            else:
                self.window.add_file(filename)

        self.window.Refresh()

        for dirname in dirs:
            dlg = dirdlg.AddDirDialog(self.window, dirname)

            if dlg.ShowModal() == wx.ID_OK:
                for filename in dlg.get_files():
                    self.window.add_file(filename)

            dlg.Destroy()

        self.window.file_list.color_items()


class FilePickerDialog(sc.SizedDialog):
    def __init__(self, parent, title=None):
        print "\nCreated FilePickerDialog"
        if not title:
            title = _("Pick Files to Count")
        sc.SizedDialog.__init__(self, parent,
                                -1,
                                title,
                                size=(700, 300),
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.panel = self.GetContentsPane()
        self.panel.SetSizerType("vertical")

        # file list
        wx.StaticText(self.panel, label=_("Select Files"))
        self.file_list = filelist.FileList(self.panel)
        self.file_list.SetSizerProps(expand=True, proportion=1)

        drop_target = MyFileDropTarget(self)
        self.file_list.SetDropTarget(drop_target)

        # buttons
        button_panel = sc.SizedPanel(self.panel)
        button_panel.SetSizerType("horizontal")
        button_panel.SetSizerProps(expand=True)

        self.add_file_btn = wx.Button(button_panel, -1, _("&Add File(s)"))
        self.add_folder_btn = wx.Button(button_panel, wx.NewId(), _("Add &Folder"))
        self.remove_btn = wx.Button(button_panel, wx.NewId(), _("&Remove"))
        self.remove_btn.Enabled = False

        self.init_button_events()

        sizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        print sizer
        sizer.CancelButton.Label = _("Cancel")
        sizer.AffirmativeButton.Label = _("OK")
        self.SetButtonSizer(sizer)

        # Begin layout
        self.MinSize = (500, 400)
        self.Fit()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED,
                  self.OnItemSelected,
                  self.file_list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                  self.OnItemDeselected,
                  self.file_list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                  self.OnItemActivated,
                  self.file_list)

    def OnItemSelected(self, evt):
        self.remove_btn.Enabled = True

    def OnItemDeselected(self, evt):
        self.remove_btn.Enabled = bool(self.file_list.get_selected_items())

    def OnItemActivated(self, evt):
        self.remove_btn.Enabled = True

    def add_file(self, path):
        self.file_list.add_file(path)
        wx.Yield()

    def get_files(self):
        filenames = set()
        for item in self.file_list.get_files():
            filenames.add(item)
        return (x for x in filenames)

    def OnAddFile(self, event):
        """The user has clicked the [Add File(s)] button"""

        print "  [Add File(s)] button clicked"
        dlg = wx.FileDialog(
            self,
            message=_("Select Files"),
            defaultFile="",
            wildcard=get_wildcard(),
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            for path in dlg.GetPaths():
                self.add_file(path)

        dlg.Destroy()

        self.file_list.color_items()

    def OnAddFolder(self, event):
        print "  [Add Folder] button clicked"
        dlg = dirdlg.AddDirDialog(self)

        if dlg.ShowModal() == wx.ID_OK:
            for filename in dlg.get_files():
                self.add_file(filename)

        dlg.Destroy()
        self.file_list.color_items()

    def OnRemove(self, event):
        print "  [Remove] button clicked"
        for item in self.file_list.get_selected_items():
            self.file_list.DeleteItem(item)
        self.file_list.color_items()

    def init_button_events(self):
        self.Bind(wx.EVT_BUTTON,
                  self.OnAddFile,
                  self.add_file_btn)
        self.Bind(wx.EVT_BUTTON,
                  self.OnAddFolder,
                  self.add_folder_btn)
        self.Bind(wx.EVT_BUTTON,
                  self.OnRemove,
                  self.remove_btn)


def main():
    app = wx.PySimpleApp()

    dlg = FilePickerDialog(None)

    if dlg.ShowModal() == wx.ID_OK:
        print "Dialog completed successfully"
        for filename in dlg.get_files():
            print " ...", filename.encode("utf-8")
    else:
        print "Dialog was cancelled"

    dlg.Destroy()


if __name__ == "__main__":
    main()
