# coding: UTF8
"""
An subclass of wx.ListCtrl for displaying a list of files with icons.
Windows only.

Most of the list control code gleaned from the excellent wxpython demo.

Image code taken from this post by Mark Hammond:
http://mail.python.org/pipermail/python-win32/2005-March/003071.html

MIT license.
"""

__author__ = "Ryan Ginstrom"
__version__ = "0.1"

import wx
import wx.lib.mixins.listctrl as list_mixin
import sys, glob
import os
import locale
import urlparse

from win32com.shell import shell, shellcon
from win32con import FILE_ATTRIBUTE_NORMAL
from win32con import FILE_ATTRIBUTE_DIRECTORY
from AnalyzeAssist import model
_ = model._


def info_to_icon(info):
    hicon, iicon, attr, display_name, type_name = info

    # Get the bitmap
    icon = wx.EmptyIcon()
    icon.SetHandle(hicon)

    return icon


def get_folder_icon(filepath, flags):
    retval, info = shell.SHGetFileInfo(filepath,
                                       FILE_ATTRIBUTE_DIRECTORY,
                                       flags)
    # non-zero on success
    assert retval
    return info_to_icon(info)


def get_closed_folder_icon(filepath):
    flags_closed = shellcon.SHGFI_SMALLICON | \
                   shellcon.SHGFI_ICON | \
                   shellcon.SHGFI_USEFILEATTRIBUTES

    return get_folder_icon(filepath, flags_closed)


def get_open_folder_icon(filepath):
    flags_open = shellcon.SHGFI_SMALLICON | \
                 shellcon.SHGFI_OPENICON | \
                 shellcon.SHGFI_ICON | \
                 shellcon.SHGFI_USEFILEATTRIBUTES

    return get_folder_icon(filepath, flags_open)


def get_folder_icons(filepath):
    closed_icon = get_closed_folder_icon(filepath)
    open_icon = get_open_folder_icon(filepath)

    return closed_icon, open_icon


def extension_to_icon(extension):
    """dot is mandatory in extension"""

    flags = shellcon.SHGFI_SMALLICON | \
            shellcon.SHGFI_ICON | \
            shellcon.SHGFI_USEFILEATTRIBUTES

    retval, info = shell.SHGetFileInfo(extension,
                                       FILE_ATTRIBUTE_NORMAL,
                                       flags)
    # non-zero on success
    assert retval
    return info_to_icon(info)


def extension_to_bitmap(extension):
    return wx.BitmapFromIcon(extension_to_icon(extension))


if __name__ == "__main__":
    from AnalyzeAssist import model


class FileList(wx.ListCtrl, list_mixin.ColumnSorterMixin):
    """Subclass of list control that shows a list of files with
    their file icons"""

    columns = ["Name", "Path"]
    odd_color = (0xe0, 0xe8, 0xff)

    def __init__(self, parent, id=-1, size=(-1, -1)):
        """style must be wx.LC_REPORT for now"""
        style = wx.LC_REPORT
        wx.ListCtrl.__init__(self, parent, id, style=style, size=size)

        self.il = None  # The image list
        self.init_base()

        self._ext_images = {}
        self._item_data = {}
        self._filenames = []

        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click, self)
        list_mixin.ColumnSorterMixin.__init__(self, len(FileList.columns))

    def on_col_click(self, event):
        wx.CallAfter(self.color_items)

    def GetListCtrl(self):
        return self

    def init_base(self):
        """Put this in a method so we can subclass
        and override for testing"""

        for col, text in enumerate(self.columns):
            self.InsertColumn(col, text)

        for i in range(len(self.columns)):
            self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)

        # Create a 16x16 image list to store our icons
        self.il = wx.ImageList(16, 16, True)

    def get_image_id(self, extension):
        """Get the img_id in the image list for the extension.
        Will add the image if not there already"""

        # Caching
        if extension in self._ext_images:
            return self._ext_images[extension]

        bmp = extension_to_bitmap(extension)

        index = self.il.Add(bmp)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self._ext_images[extension] = index

        return index

    def get_files(self):
        filenames = []
        for i in range(self.GetItemCount()):
            index = self.GetItemData(i)
            filenames.append(self._filenames[index])
        return filenames

    def add_file(self, filename):
        """Add the filenames to the list, and returns the item index"""

        full_path = os.path.abspath(filename)

        # Add the icon
        is_url = filename.startswith("http")

        if is_url:
            scheme, net, path, query, fragment = urlparse.urlsplit(filename)
            base = scheme + "://" + net
            file_part = filename[len(base):]
            path_part = filename

            self._filenames.append(filename)
        else:
            path_part, file_part = os.path.split(full_path)
            self._filenames.append(full_path)

        if is_url:
            extension = ".html"
        else:
            extension = os.path.splitext(filename)[-1].lower()
        img_id = self.get_image_id(extension)

        # Add the file and path names
        index = self.InsertStringItem(sys.maxint, file_part, img_id)
        self.SetStringItem(index, 1, path_part)
        self.SetItemData(index, len(self._filenames) - 1)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        self._item_data[index] = [file_part, path_part]
        return index

    def color_items(self):
        odd_color = FileList.odd_color
        for i in range(self.ItemCount):
            if i % 2:
                self.SetItemBackgroundColour(i, "white")
            else:
                self.SetItemBackgroundColour(i, odd_color)

    def GetColumnSorter(self):
        """
        Returns a callable object to be used for comparing
        column values when sorting.
        """
        return self.__ColumnSorter

    def __ColumnSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self._item_data[key1][col]
        item2 = self._item_data[key2][col]

        cmpVal = locale.strcoll(unicode(item1).lower(),
                                unicode(item2).lower())

        # If the items are equal then pick something else to make
        # the sort value unique
        if cmpVal == 0:
            other_cols = {0: 1, 1: 0}
            other_col = other_cols.get(col, 0)
            item1 = self._item_data[key1][other_col]
            item2 = self._item_data[key2][other_col]

            cmpVal = locale.strcoll(unicode(item1).lower(),
                                    unicode(item2).lower())

        if ascending:
            return cmpVal
        else:
            return -cmpVal

    def get_selected_items(self):
        """
        Gets the selected items for the list control.
        Select returned as a list of indices,
        low to high.
        """
        selection = []
        current = -1
        while True:
            next = self.GetNextSelected(current)
            if next == -1:
                return list(reversed(selection))

            selection.append(next)
            current = next

    def GetNextSelected(self, current):
        """return subsequent selected items, or -1 when no more"""
        return self.GetNextItem(current,
                                wx.LIST_NEXT_ALL,
                                wx.LIST_STATE_SELECTED)


class DemoFrame(wx.Frame):
    """A frame for demo purposes"""

    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          u"File List Demo",
                          size=(600, 400))

        self.file_list = FileList(self)

        # add the rows
        for filename in sorted(glob.glob("*.*")):
            self.file_list.add_file(filename)

        self.file_list.color_items()


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))

    app = wx.PySimpleApp(redirect=False, useBestVisual=True)
    frame = DemoFrame()
    frame.Show()
    app.MainLoop()
