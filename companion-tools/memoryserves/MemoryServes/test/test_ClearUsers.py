#!/usr/bin/env python

import unittest

import win32con
import mock
from nose import tools

from .. import ClearUsers


def test_message_box():
    """
    Ensure that we can show a native message box.
    """

    with mock.patch("MemoryServes.ClearUsers._user32") as mock_user:
        ClearUsers.MessageBox("message", "title")
        mb = mock_user.MessageBoxW
        mb.assert_called_once_with(ClearUsers.NULL,
                                   "message",
                                   "title",
                                   win32con.MB_OK)


def test_show_message():
    """
    Ensure that the show_message function calls up the message box.
    """

    box = mock.Mock()
    ClearUsers.show_message(box, "message", "title", None)
    box.assert_called_once_with("message", "title", ClearUsers.NULL, None)


class TestClearUsers(unittest.TestCase):
    """
    Tests of the ClearUsers.clear_users function.
    """

    def test_success(self):
        """
        Ensure that successful clearing is handled correctly.
        """

        with mock.patch("MemoryServes.ClearUsers._user32") as mock_user:
            with mock.patch("MemoryServes.ClearUsers.model") as mock_model:
                ClearUsers.clear_users()
                mock_model.load_data.assert_called_once()
                mock_model.set_up_database.assert_called_once()
                mock_model.do_save.assert_called_once()
                mb = mock_user.MessageBoxW
                mb.assert_called_once_with(ClearUsers.NULL,
                                           "Successfully cleared users from database",
                                           "Clear Users",
                                           win32con.MB_OK | win32con.MB_ICONASTERISK)

    def test_error(self):
        """
        Ensure that error while clearing is handled correctly.
        """

        with mock.patch("MemoryServes.ClearUsers._user32") as mock_user:
            with mock.patch("MemoryServes.ClearUsers.dataloader") as mock_loader:
                mock_loader.do_save.side_effect = Exception('boom')
                ClearUsers.clear_users()
                mb = mock_user.MessageBoxW
                mb.assert_called_once_with(ClearUsers.NULL,
                                           "Error clearing users:\rboom",
                                           "Clear Users Error",
                                           win32con.MB_OK | win32con.MB_ICONERROR)


class TestMain(unittest.TestCase):
    """
    Tests of the ClearUsers.main function.
    """

    def test_success(self):
        """
        Ensure that successful clearing is handled correctly.
        """

        with mock.patch("MemoryServes.ClearUsers._user32") as mock_user:
            with mock.patch("MemoryServes.ClearUsers.model") as mock_model:
                with mock.patch("MemoryServes.ClearUsers.urllib2") as mock_url:
                    with mock.patch("MemoryServes.ClearUsers.settings"):
                        mock_url.urlopen.side_effect = Exception('boom')
                        ClearUsers.main()
                        mock_model.load_data.assert_called_once()
                        mock_model.set_up_database.assert_called_once()
                        mock_model.do_save.assert_called_once()
                        mb = mock_user.MessageBoxW
                        mb.assert_called_once_with(ClearUsers.NULL,
                                                   "Successfully cleared users from database",
                                                   "Clear Users",
                                                   win32con.MB_OK | win32con.MB_ICONASTERISK)

    def test_failure(self):
        """
        Ensure that a warning dialog is displayed if the site is running.
        """

        with mock.patch("MemoryServes.ClearUsers._user32") as mock_user:
            with mock.patch("MemoryServes.ClearUsers.model"):
                with mock.patch("MemoryServes.ClearUsers.urllib2"):
                    with mock.patch("MemoryServes.ClearUsers.settings"):
                        ClearUsers.main()
                        mb = mock_user.MessageBoxW
                        msg = "You must quit Memory Serves before clearing users."
                        mb.assert_called_once_with(ClearUsers.NULL,
                                                   msg,
                                                   "Clear Users Error",
                                                   win32con.MB_OK | win32con.MB_ICONWARNING)
