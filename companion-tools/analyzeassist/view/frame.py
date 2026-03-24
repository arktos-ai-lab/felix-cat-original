# coding: UTF8
"""
The frame module

The main window of our application
"""
import os
import logging
from datetime import date
import subprocess

import wx
import wx.aui
from wx import py
from wx.lib.inspection import InspectionTool

from AnalyzeAssist.AppUtils import resource_file_name
from AnalyzeAssist.AppUtils import we_are_frozen
from AnalyzeAssist.AppUtils import module_path, get_local_app_data_folder
from AnalyzeAssist import model

from AnalyzeAssist.broadcaster import EventHandlerMethod as EventHandler
from page import StartPage, ReportPage
import update_checker
from AnalyzeAssist.view import wizard
from AnalyzeAssist import broker
from AnalyzeAssist import broadcaster
from AnalyzeAssist.controller import wizard as wizard_controller

__version__ = ""
_ = model._
LOGGER = logging.getLogger(__name__)


class AAToolBar(wx.ToolBar):
    """Wraps wx toolbar with friendlier interface for
    our purposes"""

    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent, -1,
                            wx.DefaultPosition,
                            wx.DefaultSize,
                            wx.TB_FLAT | wx.TB_NODIVIDER)
        self.SetToolBitmapSize((16, 16))

    def add_item(self, icon, name, helptext=u""):
        """Add an icon to the toolbar"""
        return self.AddSimpleTool(wx.NewId(), icon, name, helptext)


class Frame(wx.Frame):
    """
    The main window of the application
    """

    def __init__(self, parent=None, id=-1, title="AnalyzeAssist", pos=(10, 10),
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
                                            wx.SUNKEN_BORDER |
                                            wx.CLIP_CHILDREN):

        self.init_base(parent, id, title, pos, size, style)

        self._do_layout()

        broker.Register('frame', lambda: self)

        wx.CallAfter(self.check_for_updates)

    def check_for_updates(self):

        prefs = model.get_preferences()

        LOGGER.debug("Doing automatic update check")
        self.check_permission(prefs, date.today())
        if "parent" in prefs:
            del prefs["parent"]
        model.save_preferences(prefs)

    def check_permission(self, prefs, today):
        if not prefs["ask_about_updates"] and not prefs["check_updates"]:
            return
        last_check = prefs["last_update_check"]
        if not last_check:
            LOGGER.debug(u"No previous checks")
            prefs["last_update_check"] = today
            return
        else:
            diff = today - last_check
            LOGGER.debug(u"It has been %s days since the last check" % diff.days)
            check_interval = prefs["check_interval"]
            if diff.days >= check_interval:
                if prefs["ask_about_updates"]:
                    update_checker.ask_permission(self, prefs)
                else:
                    LOGGER.debug("User doesn't want us to ask about updates")
                    update_checker.check_updates()
                prefs["last_update_check"] = today

    def init_base(self, parent, id, title, pos, size, style):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

    def onPaneChanged(self, event):
        """Handle pane changes"""

        oldSelection = event.GetOldSelection()
        LOGGER.debug("Pane changed from %s to %s" % (oldSelection, event.GetSelection()))

        if oldSelection != -1:
            self.notebook.GetPage(event.GetOldSelection()).deactivate()
        self.notebook.GetPage(event.GetSelection()).activate()

    @EventHandler("progress", "start")
    def handleProgressStatusBarStart(self):
        """Respond to progress messages by putting the message text in
        the status bar
        """

        data = broadcaster.CurrentData()

        self.progress_dlg = wx.ProgressDialog(data.title,
                                              data.message,
                                              maximum=data.total,
                                              parent=self,
                                              style=wx.PD_CAN_ABORT
                                                    | wx.PD_APP_MODAL
                                                    | wx.PD_ELAPSED_TIME
                                                    #| wx.PD_ESTIMATED_TIME
                                                    | wx.PD_REMAINING_TIME
        )

        self.statusbar.SetStatusText(data.message, 0)

        self.progress_dlg.Update(data.current)

    @EventHandler("progress", "end")
    def handleProgressStatusBarEnd(self):
        """Respond to progress messages by putting the message text in
        the status bar
        """

        data = broadcaster.CurrentData()
        self.statusbar.SetStatusText(data.message, 0)
        LOGGER.debug("Destroying progress dialog")
        self.progress_dlg.Destroy()

    @EventHandler("progress", "progress")
    def handleProgressStatusBarProgress(self):
        """Respond to progress messages by putting the message text in
        the status bar
        """

        data = broadcaster.CurrentData()
        self.statusbar.SetStatusText(data.message, 0)
        self.progress_dlg.Update(data.current, data.message)

    def addReport(self, results):
        """Add a report page with the specified C{results}.

        @param results: a list of results in the form (title, docstats)
        """

        page = ReportPage(results, parent=self.notebook)
        self.notebook.AddPage(page, _("Report"), select=True)


    @EventHandler("language", "changed")
    def OnLanguageChange(self):
        """
        Respond to changed GUI language by re-creating the menu
        """

        self.initMenu()

        self.ToolBar.ClearTools()
        self.add_tools()

        if model.get_language() == "Japanese":
            self.statusbar.SetStatusText(_("UI language changed to Japanese"),
                                         0)
        else:
            self.statusbar.SetStatusText(_("UI language changed to English"),
                                         0)

    @EventHandler("page", "saved")
    def onPageSaved(self):
        """
        Respond to page save by changing notebook title
        """

        name = broadcaster.CurrentData()

        self.SetStatusText(_("Saved page"), 0)
        current = self.notebook.GetSelection()
        self.notebook.SetPageText(current, name)

    def initStatusBar(self):
        """
        Initialize the status bar upon creation
        """

        statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)

        statusbar.SetStatusWidths([-2, -3])
        statusbar.SetStatusText(_("Ready"), 0)
        statusbar.SetStatusText(_("AnalyzeAssist version %s") % __version__, 1)

        self.statusbar = statusbar

    def pngicon(self, iconname):
        """
        Load a .png format image as an icon

        @param iconname: the name of the png image file
        """

        p = resource_file_name(iconname + ".png")
        return wx.Bitmap(p, wx.BITMAP_TYPE_PNG)

    def makeImage(self, fileName):
        """
        Create and set up a bitmap for the toolbar or menu

        @param fileName: the name of the image file
        """

        bitmap = wx.Bitmap(resource_file_name(fileName), wx.BITMAP_TYPE_ANY)
        mask = wx.Mask(bitmap, (255, 0, 255))
        bitmap.SetMask(mask)
        bitmap.SetSize((16, 16))
        return bitmap

    def initIcon(self):
        """
        Set the program icon
        """

        # set icon
        icon = wx.EmptyIcon()
        p = resource_file_name("AnalyzeAssist.ICO")
        icon.LoadFile(p, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def addMenuItemBmp(self, menu, img, name, tooltip):
        """
        Add a menu item with a Bitmap icon

        Candidate for refactoring for DRY with L{addMenuItemPng}

        @param menu: the menu we are adding this item to
        @param img: the name of the image file (without path)
        @param name: the name of the menu item (label)
        @param tooltip: the menu item tooltip
        """

        item = wx.MenuItem(menu,
                           wx.NewId(),
                           name,
                           tooltip)  #, kind=wx.ITEM_CHECK)

        bmp = wx.Bitmap(resource_file_name(img))
        bmp.SetMaskColour((255, 0, 255))
        item.SetBitmap(bmp)
        return menu.AppendItem(item)

    def addMenuItemPng(self, menu, img, name, tooltip):
        """
        Add a menu item with PNG icon

        @param menu: the menu we are adding this item to
        @param img: the name of the image file (without path)
        @param name: the name of the menu item (label)
        @param tooltip: the menu item tooltip
        """

        item = wx.MenuItem(menu,
                           wx.NewId(),
                           name,
                           tooltip)

        png = self.pngicon(img)
        item.SetBitmap(png)
        menu.AppendItem(item)
        return item

    def initMenu(self):
        """Initializes the menu upon creation
        """

        # Menu Bar

        self.menu_items = {}

        ###########
        # Help
        ###########
        help_menu_items = (('on_about',
                            _('&About...'),
                            _("View version and copyright information")),
                           ('on_license',
                            _('&License'),
                            _("View the license agreement for this program")),
                           [],
                           ('on_check_updates',
                            _('Check &Updates'),
                            _("Check online for updates")),
                           [],
                           ('on_help',
                            "help16.bmp",
                            _("&Help...\tF1"),
                            _("View help for using this program"))
        )

        HelpMenu = wx.Menu()
        for item in help_menu_items:
            if len(item) == 3:
                key_text, menu_text, help_text = item

                key = self.EventKey(key_text)
                self.menu_items[key] = HelpMenu.Append(wx.NewId(),
                                                       _(menu_text),
                                                       _(help_text))
            elif len(item) == 4:
                key_text, img_name, menu_text, help_text = item
                key = self.EventKey(key_text)
                self.menu_items[key] = self.addMenuItemBmp(HelpMenu,
                                                           img_name,
                                                           _(menu_text),
                                                           _(help_text))
            else:
                HelpMenu.AppendSeparator()


        ###########
        # Tools
        ###########
        ToolsMenu = wx.Menu()
        key = self.EventKey('on_options')
        self.menu_items[key] = ToolsMenu.Append(wx.NewId(), _("&Options"))

        ###########
        # Language
        ###########
        LanguageMenu = wx.Menu()

        key = model.on_english
        self.menu_items[key] = self.addMenuItemBmp(LanguageMenu,
                                                   "us.bmp",
                                                   _("&English"),
                                                   _("Switch the GUI language to English"))

        key = model.on_japanese
        self.menu_items[key] = self.addMenuItemBmp(LanguageMenu,
                                                   "jp.bmp",
                                                   _("&Japanese"),
                                                   _("Switch the GUI language to Japanese"))

        ToolsMenu.AppendSeparator()
        ToolsMenu.AppendSubMenu(LanguageMenu, _("&Language"))

        ###########
        # File
        ###########
        FileMenu = wx.Menu()

        self.menu_items[self.OnAnalyze] = self.addMenuItemBmp(FileMenu,
                                                   "statistics16.bmp",
                                                   _("&Analyze\tF5"),
                                                   _("Analyze files against translation memories"))

        key = self.EventKey('on_save')
        self.menu_items[key] = self.addMenuItemPng(FileMenu,
                                                   "saveHS",
                                                   _("&Save\tCtrl+S"),
                                                   _("Save the current page"))

        key = self.EventKey('on_save_as')
        self.menu_items[key] = FileMenu.Append(wx.NewId(),
                                               _("Sa&ve As..."),
                                               _("Save the page with a new name"))

        FileMenu.AppendSeparator()

        key = self.EventKey('on_print')
        self.menu_items[key] = self.addMenuItemBmp(FileMenu,
                                                   "Print.bmp",
                                                   _("&Print\tCtrl+P"),
                                                   _("Prints the current document"))

        FileMenu.AppendSeparator()

        self.menu_items[self.onExitApp] = FileMenu.Append(wx.NewId(),
                                                          _("E&xit"),
                                                          _("Exit the program"))

        ###########
        # Edit
        ###########
        EditMenu = wx.Menu()

        key = self.EventKey('on_undo')
        self.menu_items[key] = self.addMenuItemPng(EditMenu,
                                                   "Edit_UndoHS",
                                                   _("&Undo\tCtrl+Z"),
                                                   _("Undo the action"))

        key = self.EventKey('on_redo')
        self.menu_items[key] = self.addMenuItemPng(EditMenu,
                                                   "Edit_RedoHS",
                                                   _("&Redo\tCtrl+Y"),
                                                   _("Redo the action"))

        EditMenu.AppendSeparator()

        key = self.EventKey('on_copy')
        self.menu_items[key] = self.addMenuItemPng(EditMenu,
                                                   "CopyHS",
                                                   _("&Copy\tCtrl+C"),
                                                   _("Copy the selection to the clipboard"))

        key = self.EventKey('on_cut')
        self.menu_items[key] = self.addMenuItemPng(EditMenu,
                                                   "CutHS",
                                                   _("Cu&t\tCtrl+X"),
                                                   _("Cut the selection into the clipboard"))

        key = self.EventKey('on_paste')
        self.menu_items[key] = self.addMenuItemPng(EditMenu,
                                                   "PasteHS",
                                                   _("&Paste\tCtrl+V"),
                                                   _("Paste the clipboard contents"))

        key = self.EventKey('on_delete')
        self.menu_items[key] = self.addMenuItemPng(EditMenu,
                                                   "DeleteHS",
                                                   _("&Delete\tDel"),
                                                   _("Delete the selection"))
        EditMenu.AppendSeparator()
        key = self.EventKey('on_select_all')
        self.menu_items[key] = EditMenu.Append(wx.NewId(),
                                               _("Select &All\tCtrl+A"),
                                               _("Select the entire page"))

        ###########
        # Debug
        ###########
        DebugMenu = wx.Menu()
        self.menu_items[self.OnWrap] = DebugMenu.Append(wx.NewId(), "&Wrap")
        self.menu_items[self.OnInspect] = DebugMenu.Append(wx.NewId(), "&Inspect")
        DebugMenu.AppendSeparator()
        self.menu_items[self.on_show_log] = DebugMenu.Append(wx.NewId(), _("View Log"))

        menuBar = wx.MenuBar()
        menuBar.Append(FileMenu, _("&File"))
        menuBar.Append(EditMenu, _("&Edit"))
        menuBar.Append(DebugMenu, _("&Debug"))
        menuBar.Append(ToolsMenu, _("&Tools"))
        menuBar.Append(HelpMenu, _("&Help"))
        self.SetMenuBar(menuBar)

        for key, item in self.menu_items.items():
            self.Bind(wx.EVT_MENU, key, item)

    def on_show_log(self, event):

        def get_format(modpath):
            if " " in modpath:
                return '"%s"'
            else:
                return '%s'

        if we_are_frozen():
            modpath = module_path()
            filename = os.path.join(modpath, "ShowLogs.exe")
            LOGGER.debug("Showing log files")
            cmd = get_format(modpath) % filename
        else:
            modpath = get_local_app_data_folder()
            filename = os.path.join(modpath, "ShowLogs.py")
            cmd = "pythonw.exe %s" % (get_format(modpath) % filename)
        assert os.path.exists(filename), filename

        LOGGER.debug(u"Calling Show Logs with command: %s" % cmd)
        subprocess.Popen(cmd, shell=False)

    def initToolbar(self):
        """Initialize the toolbar, loading the images and
        binding the events"""

        self.toolbar = AAToolBar(self)
        self.SetToolBar(self.toolbar)

        self.add_tools()

    def add_tools(self):
        ToolBarItems = {}

        analyze_image = self.makeImage("statistics16.bmp")
        analyze_help = _("Analyze files against translation memories")
        ToolBarItems[self.OnAnalyze] = self.toolbar.add_item(analyze_image,
                                                  _("Analyze"),
                                                  analyze_help)

        key = self.EventKey('on_save')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("saveHS"),
                                                  _("Save"),
                                                  _("Save the document"))

        self.toolbar.AddSeparator()

        key = self.EventKey('on_copy')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("CopyHS"),
                                                  _("Copy"),
                                                  _("Copy selection to the clipboard"))

        key = self.EventKey('on_cut')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("CutHS"),
                                                  _("Cut"),
                                                  _("Cut selection into the clipboard"))

        key = self.EventKey('on_paste')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("PasteHS"),
                                                  _("Paste"),
                                                  _("Paste the clipboard contents"))

        key = self.EventKey('on_delete')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("DeleteHS"),
                                                  _("Delete"),
                                                  _("Delete the selection"))

        self.toolbar.AddSeparator()

        key = self.EventKey('on_undo')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("Edit_UndoHS"),
                                                  _("Undo"),
                                                  _("Undo the action"))

        key = self.EventKey('on_redo')
        ToolBarItems[key] = self.toolbar.add_item(self.pngicon("Edit_RedoHS"),
                                                  _("Redo"),
                                                  _("Redo the action"))

        self.toolbar.AddSeparator()

        bm1 = self.makeImage("Print.bmp")

        ToolBarItems[self.EventKey('on_print')] = \
            self.toolbar.add_item(bm1,
                                  _("Print"),
                                  _("Prints the current document"))

        bm1 = self.makeImage("help16.bmp")

        ToolBarItems[self.EventKey('on_help')] = \
            self.toolbar.add_item(bm1,
                                  _("Help"),
                                  _("Show help for this program"))

        self.toolbar.Realize()

        for key, item in ToolBarItems.items():
            self.Bind(wx.EVT_MENU, key, item)

    def OnAnalyze(self, event):
        """
        File -> Analysis action
        Performs analysis using wizard data
        """
        self.perform_analysis()

    def perform_analysis(self):
        """
        performs analysis using wizard data
        """

        LOGGER.debug(u'performing analysis')

        def callback(data):
            LOGGER.debug(u'wizard callback returned data: %s', data)
            wizard_controller.on_wizard_completed(data, self)

        wizard.create_and_show_analysis_wizard(self, callback)

    def OnWrap(self, event):
        frame = py.crust.CrustFrame(parent=self)
        frame.SetSize((750, 525))
        frame.Show(True)
        frame.shell.interp.locals['frame'] = self

    def OnInspect(self, evt):
        if not InspectionTool().initialized:
            InspectionTool().Init()

        InspectionTool().Show(self, True)

    def EventKey(self, name):
        """
        Creates a lambda'd function that calls broadcaster.Broadcast,
        to pass to the bind function
        """

        eb = lambda *args: broadcaster.Broadcast('event', *args)

        return lambda *args: eb(name, *args)

    def _do_layout(self):
        """wxGlade-generated layout code"""

        broadcaster.registerBroadcastListeners(self)

        self.initIcon()

        callbacks = dict(on_analyze=self.perform_analysis)

        self.notebook = wx.aui.AuiNotebook(self,
                                           style=wx.aui.AUI_NB_WINDOWLIST_BUTTON |
                                                 wx.aui.AUI_NB_DEFAULT_STYLE)
        self.notebook.AddPage(StartPage(self.notebook, callbacks), _("Start"))
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.onPaneChanged)

        self.initMenu()
        self.initStatusBar()
        self.initToolbar()

        sizer = wx.BoxSizer()
        sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        self.SetMinSize((600, 450))

        # Begin layout
        self.SetAutoLayout(True)
        sizer.Fit(self)
        sizer.SetSizeHints(self)
        self.Layout()
        self.Centre()
        # End layout

        self.Bind(wx.EVT_CLOSE, self.onClose)

    def unregister(self):
        """Is this really necessary?"""
        broadcaster.unregisterBroadcastListener(self)

    def onClose(self, event):
        """Handle a close event. Calls event.Skip() to allow wxPython to
        perform normal window destruction.
        """

        LOGGER.debug("Closing frame window")
        broadcaster.Broadcast(source='app', title='shutting down')
        self.Destroy()

        event.Skip()

    def onExitApp(self, event):
        """Recieve a shutdown notification from the user"""

        LOGGER.debug("Exit app command received from user")

        self.Close()


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
