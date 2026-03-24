#coding: UTF8
"""
Script to clear users from MemoryServes database

"""
__version__ = "1.0"
__author__ = "Ryan Ginstrom"
__progname__ = "Clear Users"

import sys
from ctypes import windll, c_int, c_wchar_p
import urllib2
import logging

import win32con

import settings
import loc
import model
import dataloader

_user32 = windll.user32

NULL = c_int(0)


def MessageBox( message, title, parent=NULL, flags=win32con.MB_OK):
    """
    Wraps the MessageBoxW function

    flags:
        - Button options
            - MB_OK / MB_OKCANCEL / MB_ABORTRETRYINGORE / MB_YESNOCANCEL
              MB_YESNO / MB_RETRYCANCEL
        - Icon options
            - MB_ICONHAND / MB_ICONQUESTION / MB_ICONEXCLAMATION
              MB_ICONASTERISK
    """
    MsgBox = _user32.MessageBoxW
    MsgBox.argtypes = [c_int, c_wchar_p, c_wchar_p, c_int]
    return MsgBox( parent, message, title, flags )


def show_message(box, message, title, flags):
    """
    Show a message box using the supplied `box` function.
    """

    box(message, title, NULL, flags)


def clear_users():
    """
    Clears the users from the MemoryServes DB.
    MemoryServes must not be running.
    """
    try:
        model.Data.users = {}
        dataloader.do_save()
    except Exception, details:
        logging.exception("Error clearing user accounts.")
        err = unicode(str(details), sys.getfilesystemencoding())
        err_msg = u"Error clearing users:\r%s" % err
        show_message(MessageBox,
                     err_msg,
                     u"Clear Users Error",
                     win32con.MB_OK | win32con.MB_ICONERROR)
    else:
        show_message(MessageBox,
                     u"Successfully cleared users from database",
                     u"Clear Users",
                     win32con.MB_OK | win32con.MB_ICONASTERISK)


def main():
    """
    When called as main.

    Clears user accounts from the db. This will trigger creating a new admin account.

    If Memory Serves is running, displays a dialog instructing the user to quit MS first.
    """

    logging.info("Clearing user accounts")
    settings.get_config()
    url = "http://%s:%s/" % (settings.Settings.HOST, settings.Settings.PORT)
    try:
        urllib2.urlopen(url)
    except:
        # if we failed to load the MS home page, it means MS is not running.
        clear_users()
    else:
        err_msg = u"You must quit Memory Serves before clearing users."
        show_message(MessageBox,
                     err_msg,
                     u"Clear Users Error",
                     win32con.MB_OK | win32con.MB_ICONWARNING)


if __name__ == "__main__":  # pragma no cover
    main()
