__author__ = 'Ryan'

import unittest

import mock
import win32con

from .. import SysTrayIcon

def test_show():
    with mock.patch('MemoryServes.SysTrayIcon.webbrowser') as web:
        SysTrayIcon.show(None)
        web.open.assert_called_once()


class TestShowSysIcon(unittest.TestCase):

    def test_no_sys_icon(self):
        with mock.patch('MemoryServes.SysTrayIcon.webbrowser'):
            with mock.patch('MemoryServes.SysTrayIcon.SysTrayIcon') as mock_sys_tray:
                mock_sys_tray.return_value = None
                cherrybase = mock.Mock()
                SysTrayIcon.show_sys_icon(cherrybase)
                cherrybase.log_error.assert_called_once_with("Failed to load sys tray icon")

    def test_throws(self):
        with mock.patch('MemoryServes.SysTrayIcon.SysTrayIcon') as mock_sys_tray:
            mock_sys_tray.side_effect = Exception("boom")
            cherrybase = mock.Mock()
            SysTrayIcon.show_sys_icon(cherrybase)
            cherrybase.log_error.assert_called_once_with("Failed to load system tray icon: Exception('boom',)")


class TestNonStringIterable(unittest.TestCase):
    def test_int(self):
        assert not SysTrayIcon.non_string_iterable(3)
    def test_str(self):
        assert not SysTrayIcon.non_string_iterable("foo")
    def test_list(self):
        assert SysTrayIcon.non_string_iterable([1, 2, 3])

d = mock.DEFAULT

class TestSysTrayIcon(unittest.TestCase):
    """
    Test the SysTrayIcon class.
    """

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d, win32gui_struct=d)
    def test_destroy(self, **kwargs):
        """
        Ensure that we can destroy the icon.
        """
        with mock.patch("MemoryServes.SysTrayIcon.win32gui") as fake_gui:
            icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=tuple())
            icon.destroy(None, None, None, None)
            fake_gui.Shell_NotifyIcon.assert_called_once()

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d, win32gui_struct=d, win32gui=d)
    def test_notify_left_button_double(self, **kwargs):
        """
        Ensure that we properly handle notifications left-button double clicks
        """
        icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=tuple())
        icon.execute_menu_option = mock.Mock()
        icon.show_menu = mock.Mock()
        icon.notify(None, None, None, win32con.WM_LBUTTONDBLCLK)
        icon.execute_menu_option.assert_called_once()
        assert not icon.show_menu.called

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d, win32gui_struct=d, win32gui=d)
    def test_notify_right_button(self, **kwargs):
        """
        Ensure that we properly handle notifications right-button clicks
        """
        icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=tuple())
        icon.execute_menu_option = mock.Mock()
        icon.show_menu = mock.Mock()
        icon.notify(None, None, None, win32con.WM_RBUTTONUP)
        icon.show_menu.assert_called_once()
        assert not icon.execute_menu_option.called

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d, win32gui_struct=d, win32gui=d)
    def test_notify_left_button(self, **kwargs):
        """
        Ensure that we ignore left-button clicks
        """
        icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=tuple())
        icon.execute_menu_option = mock.Mock()
        icon.show_menu = mock.Mock()
        icon.notify(None, None, None, win32con.WM_LBUTTONUP)
        assert not icon.show_menu.called
        assert not icon.execute_menu_option.called

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d)
    def test_show_menu(self, **kwargs):
        """
        Ensure that we can show the menu.
        """
        with mock.patch("MemoryServes.SysTrayIcon.win32gui") as fake_gui:
            with mock.patch("MemoryServes.SysTrayIcon.win32gui_struct") as fake_struct:
                fake_struct.PackMENUITEMINFO.return_value = (None, None)
                menu_options=(('option', None, lambda : 'foo'),)
                icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=menu_options)
                icon.execute_menu_option = mock.Mock()
                icon.show_menu()
                fake_gui.TrackPopupMenu.assert_called_once()

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d)
    def test_create_menu(self, **kwargs):
        """
        Ensure that we can create the menu, adding menu items in the correct format.
        """
        with mock.patch("MemoryServes.SysTrayIcon.win32gui") as fake_gui:
            with mock.patch("MemoryServes.SysTrayIcon.win32gui_struct") as fake_struct:
                fake_struct.PackMENUITEMINFO.return_value = (None, None)
                menu_options=(('option', None, lambda : 'foo'),)
                icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=menu_options)
                icon.execute_menu_option = mock.Mock()
                menu_options=[('option', None, lambda : 'foo', 1),]
                icon.create_menu(None, menu_options)
                fake_gui.CreatePopupMenu.assert_called_once()

    @mock.patch.multiple("MemoryServes.SysTrayIcon", win32api=d, win32gui_struct=d)
    def test_prep_menu_icon(self, **kwargs):
        """
        Ensure that we do the low-level stuff needed to create a menu icon.
        """
        with mock.patch("MemoryServes.SysTrayIcon.win32gui") as fake_gui:
            menu_options=(('option', None, lambda : 'foo'),)
            icon = SysTrayIcon.SysTrayIcon("icon", "hover_text", menu_options=menu_options)
            icon.execute_menu_option = mock.Mock()
            icon.prep_menu_icon(mock.Mock())
            fake_gui.DrawIconEx.assert_called_once()
            fake_gui.SelectObject.assert_called_once()
            fake_gui.DeleteDC.assert_called_once()
