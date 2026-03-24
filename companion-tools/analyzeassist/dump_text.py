# coding: UTF8
"""
A simple GUI frontend for the extract_segments command-line utility.
"""
import logging

import wx

import extract_segments
import filepicker
import AppUtils

LOGGER = logging.getLogger(__name__)


def get_paths():
    """Retrieves the names of the files to count.

    We put this in a separate method so we can override when testing.
    """

    dlg = filepicker.FilePickerDialog(None, _("Pick Files to Dump"))

    paths = []
    # Show the dialog and retrieve the user response. If it is the OK response,
    # process the data.
    if dlg.ShowModal() == wx.ID_OK:
        # This returns a Python file_list of files that were selected.
        paths = dlg.get_files()

    # Destroy the dialog. Don't do this until you are done with it!
    # BAD things can happen otherwise!
    dlg.Destroy()

    return paths


def dump():
    app = wx.PySimpleApp(redirect=AppUtils.we_are_frozen(), filename="log.txt")
    paths = list(get_paths())

    LOGGER.debug(paths)

    if paths:
        extract_segments.extract(".segs.txt", paths)

        wx.MessageBox(_("Finished extracting text.\nLook in the file folder for the extracted files."), _("Dump Text"))


if __name__ == "__main__":
    dump()
