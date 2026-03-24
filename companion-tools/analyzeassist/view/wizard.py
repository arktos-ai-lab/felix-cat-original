# coding: UTF8
"""
View code for Analysis Wizard

"""

from __future__ import nested_scopes
import logging
import wx.wizard
from AnalyzeAssist import broadcaster, broker
import wx
from AnalyzeAssist import model  # _
from AnalyzeAssist import docstats
import filelist
import os
import dirdlg

DirDialog = wx.DirDialog
FileDialog = wx.FileDialog
LOGGER = logging.getLogger(__name__)
_ = model._


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


#####################
# makePageTitle
#####################

def makePageTitle(wizPg, title):
    """Create a basic wizard page with title"""

    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND | wx.ALL, 5)
    return sizer


class WizPageFileListBase(wx.wizard.WizardPageSimple):
    """
    Base class for wizard page with file file_list control and browse button
    """

    def __init__(self, parent, title, subtitle):

        wx.wizard.WizardPageSimple.__init__(self, parent)
        self.layout(title, subtitle)

    def make_remove_button(self):
        self.remove_button = wx.Button(self, label=_("&Remove"))
        self.remove_button.SetToolTipString(_("Remove the selected item(s)"))
        self.remove_button.Disable()

    def make_file_list(self):
        self.file_list = filelist.FileList(self)

    def layout(self, title, subtitle):
        self.sizer = makePageTitle(self, title)

        self.sizer.Add(wx.StaticText(self, label=subtitle), 0, wx.EXPAND | wx.ALL, 5)

        self.make_file_list()
        STRETCH_VERTICALLY = 1
        self.sizer.Add(self.file_list, STRETCH_VERTICALLY, wx.EXPAND | wx.ALL, 5)

        drop_target = MyFileDropTarget(self)
        self.file_list.SetDropTarget(drop_target)

        self.statusArea = wx.StaticText(self, label=_(""))
        self.make_remove_button()
        self.make_button_row()

        flexgrid = wx.FlexGridSizer(1, 6, 5, 5)
        flexgrid.AddGrowableCol(2)
        flexgrid.SetFlexibleDirection(wx.HORIZONTAL)

        flexgrid.Add(self.remove_button, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        flexgrid.Add(self.statusArea, 3, flag=wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        flexgrid.Add(wx.StaticText(self), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        self.layout_button_row(flexgrid)

        self.sizer.Add(flexgrid, 0, wx.EXPAND | wx.ALL, 5)

        self.bindEvents()

        self.files = set()

        self.Fit()

    def bindEvents(self):
        self.Bind(wx.EVT_BUTTON,
                  self.OnRemove,
                  self.remove_button)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,
                  self.OnItemSelected,
                  self.file_list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,
                  self.OnItemDeSelected,
                  self.file_list)

    def get_filename_at(self, index):
        pos = self.file_list.GetItemData(index)
        return self.file_list._filenames[pos]

    def OnRemove(self, event):
        """Remove the selected item from the file_list"""

        LOGGER.debug("WizPageMemories -- OnRemove")
        self.remove_button.Disable()

        select_index = -1

        while self.file_list.GetFirstSelected() <> -1:
            # get the indexes
            select_index = self.file_list.GetFirstSelected()
            key = self.get_filename_at(select_index)

            # delete them
            self.files.remove(key)
            self.file_list.DeleteItem(select_index)

        if select_index <> -1:
            if select_index >= self.file_list.GetItemCount():
                self.file_list.Select(select_index - 1)
            else:
                self.file_list.Select(select_index)

        event.Skip()

    def OnItemDeSelected(self, event):
        """Give information about the selected item, and
        activate/deactivate the remove button"""

        LOGGER.debug("WizPageMemories -- OnItemSelected")
        if self.file_list.GetSelectedItemCount() == 0:
            self.remove_button.Disable()
        else:
            self.remove_button.Enable()
        event.Skip()

    def OnItemSelected(self, event):
        """Give information about the selected item, and
        activate/deactivate the remove button"""

        LOGGER.debug("WizPageMemories -- OnItemSelected")
        self.remove_button.Enable()
        event.Skip()

    def OnBrowse(self, event):
        """Select memories"""

        dlg = FileDialog(
            self,
            message=_("Select Files"),
            defaultFile="",
            wildcard=self.get_wildcard(),
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)

        # Show the dialog and retrieve the user response. If it is the OK response,
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python file_list of files that were selected.
            paths = dlg.GetPaths()

            for path in paths:
                self.files.add(path)

            self.file_list.DeleteAllItems()
            for index, path in enumerate(self.files):
                item = self.file_list.add_file(path)
                self.file_list.SetItemData(item, index)

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()

        self.file_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def add_file(self, path):
        self.files.add(path)

        self.file_list.DeleteAllItems()
        for index, path in enumerate(self.files):
            item = self.file_list.add_file(path)
            self.file_list.SetItemData(item, index)
        wx.Yield()


#####################
# WizPageFiles
#####################

class WizPageFiles(WizPageFileListBase):
    """The first wizard page.
    It prompts the user to select files to analyze"""

    def __init__(self, parent):

        WizPageFileListBase.__init__(self, parent,
                                     _("Select Files (step 1 of 3)"),
                                     _("Select one or more files to analyze.")
        )

        self.SetMinSize((600, 500))

    def OnUrl(self, event):
        LOGGER.debug("Adding URL to files page")
        dlg = wx.TextEntryDialog(
            self,
            _("Enter a URL"),
            _("Enter URL"))

        if dlg.ShowModal() == wx.ID_OK:
            self.files.add(dlg.Value)

            self.file_list.DeleteAllItems()
            for index, path in enumerate(self.files):
                item = self.file_list.add_file(path)
                self.file_list.SetItemData(item, index)

        dlg.Destroy()

    def OnFolder(self, event):
        LOGGER.debug("Adding folder to files page")
        dlg = dirdlg.AddDirDialog(self)

        if dlg.ShowModal() == wx.ID_OK:
            self.files.update(set(dlg.get_files()))

            self.file_list.DeleteAllItems()
            for index, path in enumerate(self.files):
                item = self.file_list.add_file(path)
                self.file_list.SetItemData(item, index)

        dlg.Destroy()
        self.file_list.color_items()

    def layout_button_row(self, flexgrid):
        # next row
        flexgrid.Add(self.browse_button, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        flexgrid.Add(self.folder_button, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        flexgrid.Add(self.url_button, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)


    def make_button_row(self):
        self.url_button = wx.Button(self, label=_("&URL..."))
        self.url_button.SetToolTipString(_("Enter the URL of a web page"))

        self.browse_button = wx.Button(self, label=_("&Browse..."))
        self.browse_button.SetToolTipString(_("Select a file to add"))

        self.folder_button = wx.Button(self, label=_("Add &Folder..."))
        self.folder_button.SetToolTipString(_("Add a folder to be analyzed"))

        self.Bind(wx.EVT_BUTTON,
                  self.OnBrowse,
                  self.browse_button)
        self.Bind(wx.EVT_BUTTON,
                  self.OnUrl,
                  self.url_button)
        self.Bind(wx.EVT_BUTTON,
                  self.OnFolder,
                  self.folder_button)

    def get_wildcard(self):
        return '|'.join([_("All Files (*.*)|*.*"),
                         _("MS Word (*.doc)|*.doc"),
                         _("MS Excel (*.xls;*.csv)|*.xls;*.csv"),
                         _("MS PowerPoint (*.ppt)|*.ppt"),
                         _("Text Files (*.txt)|*.txt"),
                         _("XML Files (*.xml)|*.xml"),
                         _("HTML Files (*.html;*.htm)|*.html;*.htm"),
                         _("PDF Files (*.pdf)|*.pdf"),
        ])


#####################
# WizPageMemories
#####################

class WizPageMemories(WizPageFileListBase):
    """The second wizard page
    Prompts the user to select memory files to use in the analysis"""

    def __init__(self, parent):

        WizPageFileListBase.__init__(self, parent,
                                     _("Select Memories (step 2 of 3)"),
                                     _("Select one or more memory files.")
        )


    def OnUrl(self, event):
        LOGGER.debug("OnRemote")
        dlg = wx.TextEntryDialog(
            self,
            _("Enter a Connection URL"),
            _("Enter URL"))

        if dlg.ShowModal() == wx.ID_OK:
            self.files.add(dlg.Value)

            self.file_list.DeleteAllItems()
            for index, path in enumerate(self.files):
                item = self.file_list.add_file(path)
                self.file_list.SetItemData(item, index)

        dlg.Destroy()


    def layout_button_row(self, flexgrid):
        # next row
        flexgrid.Add(self.browse_button, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        flexgrid.Add(self.url_button, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)


    def make_button_row(self):
        self.url_button = wx.Button(self, label=_("Re&mote..."))
        self.browse_button = wx.Button(self, label=_("&Browse..."))

        self.url_button.SetToolTipString(_("Enter the URL of a \nMemory Serves memory"))
        self.browse_button.SetToolTipString(_("Select a memory to analyze files"))

        self.Bind(wx.EVT_BUTTON,
                  self.OnBrowse,
                  self.browse_button)
        self.Bind(wx.EVT_BUTTON,
                  self.OnUrl,
                  self.url_button)

    def get_wildcard(self):
        return '|'.join([_("Memory Files (*.ftm, *.xml, *.tmx)|*.ftm;*.xml;*.tmx"),
                         _("Felix Files (*.ftm, *.xml)|*.ftm;*.xml"),
                         _("TMX Files (*.tmx)|*.tmx"),
                         _("All Files (*.*)|*.*")])


broker.Register('extensions', lambda: None)


def makeMatchRangelabel(parent):
    """Adds the match range label to the parent"""

    parent.match_rangeLabel = wx.StaticText(parent,
                                            -1,
                                            _("Match ranges"))
    parent.match_rangeLabel.SetToolTipString(_("Enter the match ranges here,\none range to a line"))


def makeMatchRangeTxtCtrl(parent):
    """Adds the match range text control to the parent"""

    parent.match_rangesTextCtrl = wx.TextCtrl(parent, -1, "", style=wx.TE_MULTILINE)
    parent.match_rangesTextCtrl.SetValue(parent.match_ranges)


def makeExtractSegsCheck(parent):
    """Adds an extract segments checkbox to the parent"""

    parent.extractSegsCheck = wx.CheckBox(parent,
                                          -1,
                                          _("Extract non-matching segments"))
    parent.extractSegsCheck.SetToolTipString(_("Select this to extract non-perfect matches\nto a separate text file"))
    if parent.fuzzy_options:
        parent.extractSegsCheck.SetValue(wx.CHK_CHECKED)
    else:
        parent.extractSegsCheck.SetValue(wx.CHK_UNCHECKED)


def addMatchRange(parent):
    """Adds a match range widget to the parent
    """

    makeMatchRangelabel(parent)
    makeMatchRangeTxtCtrl(parent)
    rangeSizer = wx.FlexGridSizer(rows=1,
                                  cols=2,
                                  vgap=10,
                                  hgap=10)
    rangeSizer.Add(parent.match_rangeLabel)
    rangeSizer.Add(parent.match_rangesTextCtrl,
                   flag=wx.EXPAND | wx.ALL)
    rangeSizer.AddGrowableCol(1)
    rangeSizer.AddGrowableRow(0)
    parent.sizer.Add(rangeSizer,
                     proportion=1,
                     flag=wx.EXPAND | wx.ALL)


#####################
# WizPagePreferences
#####################
def makeAnalysisPrefsPage(parent):
    """ Get the preferences
    """

    LOGGER.debug("Creating analysis preferences page")

    prefs = model.get_preferences()
    parent.match_ranges = docstats.format_match_ranges()
    parent.fuzzy_options = prefs["fuzzy options"] or {}

    LOGGER.debug("Fuzzy options: %s" % parent.fuzzy_options)

    parent.sizer.Add(wx.StaticText(parent,
                                   -1,
                                   u" "))

    addMatchRange(parent)

    makeExtractSegsCheck(parent)
    parent.Bind(wx.EVT_CHECKBOX, parent.onExtractSegs, parent.extractSegsCheck)
    parent.sizer.Add(parent.extractSegsCheck)

    parent.segExtensionLabel = wx.StaticText(parent,
                                             -1,
                                             _("File extension"))
    parent.segExtensionLabel.SetToolTipString(_("This file extension will be added to the\nextracted file."))
    parent.segExtensionTextCtrl = wx.TextCtrl(parent,
                                              -1,
                                              "")
    parent.saveDirTextCtrl = wx.TextCtrl(parent,
                                         -1,
                                         "")

    parent.saveDirLabel = wx.StaticText(parent,
                                        -1,
                                        _("Save directory"))
    parent.saveDirLabel.SetToolTipString(_("Extracted files will be saved to this directory."))

    rangeSizer2 = wx.FlexGridSizer(rows=2,
                                   cols=4,
                                   vgap=10,
                                   hgap=10)
    rangeSizer2.Add((10, 10))
    rangeSizer2.Add(parent.segExtensionLabel)
    rangeSizer2.Add(parent.segExtensionTextCtrl)
    rangeSizer2.Add(wx.StaticText(parent, -1, u"  "))

    rangeSizer2.Add((10, 10))
    rangeSizer2.Add(parent.saveDirLabel)
    rangeSizer2.Add(parent.saveDirTextCtrl,
                    proportion=1,
                    flag=wx.EXPAND | wx.ALL)

    parent.browse_button = wx.Button(parent, -1, _("&Browse..."))
    parent.Bind(wx.EVT_BUTTON,
                parent.OnBrowse,
                parent.browse_button)

    rangeSizer2.Add(parent.browse_button)

    rangeSizer2.AddGrowableCol(2)

    if parent.fuzzy_options.get("extract"):
        parent.segExtensionTextCtrl.Value = parent.fuzzy_options["extension"] or ""
        parent.saveDirTextCtrl.Value = parent.fuzzy_options["directory"] or ""
        parent.extractSegsCheck.Value = True
    else:
        parent.extractSegsCheck.Value = False
        parent.segExtensionTextCtrl.Value = "fuzzy"
        parent.segExtensionTextCtrl.Disable()
        parent.saveDirTextCtrl.Value = ""
        parent.saveDirTextCtrl.Disable()
        parent.browse_button.Disable()

    parent.sizer.Add(wx.StaticText(parent,
                                   -1,
                                   u" "))
    parent.sizer.Add(rangeSizer2, flag=wx.EXPAND | wx.ALL)
    parent.sizer.Add(wx.StaticText(parent,
                                   -1,
                                   u" "))

    parent.Fit()


@broker.BrokerRequestHandler("make analysis options page")
def getAnalysisOptionsPage():
    """Creates and retrieves the analysis options page"""

    return makeAnalysisPrefsPage(broker.CurrentData())


class PreferencesBase(object):
    """Common code for options page and wizard page"""

    def getAnalysisPreferences(self):
        """Get the user preferences for analysis"""

        fuzzy_options = dict(extension=self.segExtensionTextCtrl.Value,
                             directory=self.saveDirTextCtrl.Value,
                             extract=self.extractSegsCheck.Value)

        return (self.match_rangesTextCtrl.Value, fuzzy_options)

    def OnBrowse(self, event):
        """Select memories"""

        dlg = DirDialog(self, _("Select directory for fuzzy match files:"),
                        style=wx.DD_DEFAULT_STYLE
                              #| wx.DD_DIR_MUST_EXIST
                              | wx.DD_CHANGE_DIR
        )

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it.
        if dlg.ShowModal() == wx.ID_OK:
            LOGGER.debug(u'Selected directory: %s' % dlg.GetPath())
            self.saveDirTextCtrl.Value = dlg.GetPath()

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()

    def onExtractSegs(self, event):
        """Whether the extensions text control is enabled depends
        on the checkbox value"""

        if self.extractSegsCheck.Value:
            self.segExtensionTextCtrl.Enable()
            self.saveDirTextCtrl.Enable()
            self.browse_button.Enable()
        else:
            self.segExtensionTextCtrl.Disable()
            self.saveDirTextCtrl.Disable()
            self.browse_button.Disable()


class WizPagePreferences(wx.wizard.WizardPageSimple, PreferencesBase):
    """Preferences page on the Analysis wizard

    TODO: Consider replacing multiple inheritance with encapsulation."""

    def __init__(self, parent):
        self.init_base(parent)
        self.layout()

    def layout(self):
        """Lays out the widgets on the wizard page.
        We define this as a separate method so we can override it in the
        fake wizard"""

        self.sizer = makePageTitle(self, _("Set Preferences (step 3 of 3)"))

        broker.Request("make analysis options page", self)

        self.checkbox = wx.CheckBox(self,
                                    -1,
                                    _("Count number-only segments"))

        self.checkbox.SetToolTipString(_("Select to include number-only segments in analysis"))
        self.sizer.Add(self.checkbox)
        self.Fit()

    def init_base(self, parent):
        """We override this in the fake wizard"""

        wx.wizard.WizardPageSimple.__init__(self, parent)

    def analyze_numbers(self):
        """Whether we should analyze numbers"""

        return self.checkbox.Value


def get_wizard(parent=None):
    """Creates and returns the analysis wizard"""

    return wx.wizard.Wizard(parent,
                            -1,
                            _("Analyze Files"),
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)


#####################
# AnalyzerWiz
#####################

def create_and_show(wizard, callback):
    page1 = WizPageFiles(wizard)
    page2 = WizPageMemories(wizard)
    page3 = WizPagePreferences(wizard)

    wizard.FitToPage(page1)
    wizard.SetMinSize((600, 800))

    # Use the convenience Chain function to connect the pages
    wx.wizard.WizardPageSimple_Chain(page1, page2)
    wx.wizard.WizardPageSimple_Chain(page2, page3)

    wizard.GetPageAreaSizer().Add(page1)
    wizard.GetPageAreaSizer().Add(page2)
    wizard.GetPageAreaSizer().Add(page3)
    if wizard.RunWizard(page1):
        LOGGER.debug(" ... The wizard was completed")
        prefs = list(page3.getAnalysisPreferences()) + [page3.analyze_numbers()]
        data = dict(files=list(page1.files),
                    memories=list(page2.files),
                    prefs=prefs)
        callback(data)
    else:
        LOGGER.debug(" ... Wizard canceled.")


def create_and_show_analysis_wizard(parent, callback):
    """
    Creates and shows the Analysis wizard
    """

    LOGGER.debug("Running AnalyzerWiz")

    wizard = get_wizard(parent)
    create_and_show(wizard, callback)


INITIAL_IMPORT = True

if INITIAL_IMPORT:
    broadcaster.Register(create_and_show_analysis_wizard, "event", "on_analyze")

INITIAL_IMPORT = False


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
