#!/usr/bin/env python
# Module     : SysTrayIcon.py
# Synopsis   : Windows System tray icon.
# Programmer : Simon Brunning - simon@brunningonline.net
# Date       : 11 April 2005
# Notes      : Based on (i.e. ripped off from) Mark Hammond's
#              win32gui_taskbar.py and win32gui_menu.py demos from PyWin32
'''
System Tray Icon class.

For now, the demo at the bottom shows how to use it...
'''

import os
import win32api
import win32con
import win32gui_struct
import win32gui
import webbrowser
import logging

import pywintypes

import dataloader
import model
import settings
import loc


logger = logging.getLogger(__name__)


class SysTrayIcon(object):
    '''
    Represents the system tray icon.
    '''
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]

    FIRST_ID = 1023

    def __init__(self,
                 icon,
                 hover_text,
                 menu_options,
                 on_quit=None,
                 default_menu_index=None,
                 window_class_name=None,):

        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit

        menu_options = menu_options + (('Quit', None, self.QUIT),)
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id


        self.default_menu_index = (default_menu_index or 0)
        self.window_class_name = window_class_name or "SysTrayIconPy"

        message_map = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
                       win32con.WM_DESTROY: self.destroy,
                       win32con.WM_COMMAND: self.command,
                       win32con.WM_USER+20 : self.notify,}
        # Register the Window class.
        window_class = win32gui.WNDCLASS()
        hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(window_class)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom,
                                          self.window_class_name,
                                          style,
                                          0,
                                          0,
                                          win32con.CW_USEDEFAULT,
                                          win32con.CW_USEDEFAULT,
                                          0,
                                          0,
                                          hinst,
                                          None)
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = self.get_notify_id(None)
        self.refresh_icon(win32gui.NIM_ADD)

        win32gui.PumpMessages()

    def __del__(self):
        """
        On deletion, make sure we've destroyed the HWND.
        """
        self._destroy_window()

    def _destroy_window(self):
        """
        Destroy the HWND
        """
        self._remove_icon()
        if self.hwnd:
            logger.debug("Destroying the window")
            win32gui.DestroyWindow(self.hwnd)
            self.hwnd = None

    def _notify_icon(self, message, tries=0):
        if tries > 3:
            logging.warn("Retry limit exceeded")
            return
        try:
            win32gui.Shell_NotifyIcon(message, self.notify_id)
        except pywintypes.error:
            logger.warn("Call to Shell_NotifyIcon(%s) failed; retrying" % message)
            self._notify_icon(message, tries+1)

    def _remove_icon(self):
        logger.debug("Destroying the icon")
        self._notify_icon(win32gui.NIM_DELETE)

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                result.append(menu_option + (self._next_action_id,))
            elif non_string_iterable(option_action):
                result.append((option_text,
                               option_icon,
                               self._add_ids_to_menu_options(option_action),
                               self._next_action_id))
            else:
                print 'Unknown item', option_text, option_icon, option_action
            self._next_action_id += 1
        return result

    def get_notify_id(self, hicon):
        return (self.hwnd,
                win32con.WM_USER + 20,
                win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                win32con.WM_USER + 20,
                hicon,
                self.hover_text)

    def refresh_icon(self, message):
        # Try and find a custom icon
        self._remove_icon()
        hinst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self.icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                       self.icon,
                                       win32con.IMAGE_ICON,
                                       0,
                                       0,
                                       icon_flags)
        else:
            print "Can't find icon file - using default."
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        self.notify_id = self.get_notify_id(hicon)

        self._notify_icon(message)

    def restart(self, hwnd, msg, wparam, lparam):
        self.refresh_icon(win32gui.NIM_MODIFY)

    def destroy(self, hwnd, msg, wparam, lparam):
        """
        Got a destroy message.
        """
        logger.debug("Got a destroy message")
        self._remove_icon()
        model.SHOULD_QUIT = True
        dataloader.SHOULD_QUIT = True
        self._destroy_window()
        if self.on_quit: self.on_quit(self)

    def notify(self, hwnd, msg, wparam, lparam):
        """
        Reacting to a notification message
        """
        if lparam==win32con.WM_LBUTTONDBLCLK:
            self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam==win32con.WM_RBUTTONUP:
            self.show_menu()
        return True

    def show_menu(self):
        """
        Display the pop-up menu
        """
        logger.debug("Showing the popup menu")
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)

        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hwnd,
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def create_menu(self, menu, menu_options):
        """
        Create the menu.
        """
        logger.debug("Creating the menu")
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)

            item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text,
                                                            hbmpItem=option_icon,
                                                            wID=option_id)
            win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(self, icon):
        """
        Perform the low-level actions needed to turn an icon file into a menu icon.
        """
        logger.debug("Prepping the menu icon")
        # First load the icon.
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # Fill the background.
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        # unclear if brush needs to be feed.  Best clue I can find is:
        # "GetSysColorBrush returns a cached brush instead of allocating a new
        # one." - implies no DeleteObject
        # draw the icon
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)

        return hbm

    def command(self, hwnd, msg, wparam, lparam):
        """
        A windows command messsage.
        """
        logger.debug("Windows command %s" % wparam)
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)

    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
        else:
            menu_action(self)

def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, basestring)


def show(_):
    """
    This is a menu option to show the website in the browser
    """
    address = "http://%s:%s/" % (settings.get_host(), settings.get_port())
    logger.debug("Showing app in web browser at %s" % address)
    webbrowser.open(address)

def show_sys_icon(cherrybase):
    """
    Show a system tray icon to let users know we're running,
    and give them quick access to quitting, etc.
    """
    try:
        logger.debug("Showing system icon")
        hover_text = "Memory Serves"

        menu_options = (('Show in Browser', None, show),)

        tray_icon = SysTrayIcon(os.path.join(loc.get_media_dir(),
                                             "MemoryServes.ico"),
                                hover_text,
                                menu_options,
                                on_quit=None,
                                default_menu_index=1)
        if not tray_icon:
            cherrybase.log_error("Failed to load sys tray icon")
    except Exception, details:
        cherrybase.log_error("Failed to load system tray icon: %s" % repr(details))


def main():  # pragma no test
    """
    Run when called as main. Demo for testing.
    """
    import itertools, glob, os

    logging.basicConfig(level=logging.DEBUG)
    logger.debug("Launching sys icon as main")

    icons = itertools.cycle(glob.glob('L:\\dev\\icons\\Icons\\Cartoon\\*.ico'))
    hover_text = "SysTrayIcon.py Demo"
    def hello(sysTrayIcon): print "Hello World."
    def simon(sysTrayIcon): print "Hello Simon."
    def switch_icon(sysTrayIcon):
        sysTrayIcon.icon = icons.next()
        sysTrayIcon.refresh_icon()

    menu_options = (('Say Hello', icons.next(), hello),
                    ('Switch Icon', None, switch_icon),
                    ('A sub-menu', icons.next(), (('Say Hello to Simon', icons.next(), simon),
                                                  ('Switch Icon', icons.next(), switch_icon),
                    ))
    )
    def bye(sysTrayIcon):
        print 'Bye, then.'
        os._exit(0)

    SysTrayIcon(icons.next(), hover_text, menu_options, on_quit=bye, default_menu_index=1)

# Minimal self test. You'll need a bunch of ICO files in the current working
# directory in order for this to work...
if __name__ == '__main__':  # pragma no test
    main()
