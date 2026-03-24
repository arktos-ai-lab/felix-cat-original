# coding: UTF8
"""
Notebook page classes

"""
import logging

import wx
import wx.html
import cStringIO
from AnalyzeAssist import broadcaster
import os
from AnalyzeAssist.broadcaster import EventHandlerMethod as EventHandler
from AnalyzeAssist.output_format import print_row, format_num
from AnalyzeAssist.AppUtils import resource_file_name
from AnalyzeAssist import model


LOGGER = logging.getLogger(__name__)

_ = model._


def segstat2list(segstat):
    """Convert the SegStat class into a list for printing in
    a table row
    """

    return [segstat.words,
            segstat.characters,
            segstat.chars_no_spaces,
            segstat.asian_chars,
            segstat.non_asian_words]


def range2item(match_range):
    """
    Convert a match range (low,high) into a table row heading.
    
    @param match_range: a pair in the form (low, high), where
        low <= high.
        
    If the low and high values are the same, returns "low%"
    
    If the low value is lower, returns "low&ndash;high%"
    """

    left, right = match_range

    assert left <= right

    if left == right:
        return "%i%%" % left

    return "%i&ndash;%i%%" % match_range


def makeTotalsRow(data):
    """Make the totals row (totals for each category, bolded"""

    totals = ["Totals"]
    for i in range(1, len(data[0])):
        totals.append("<b>%s</b>" % format_num(sum([row[i] for row in data])))
    return totals


def is_url(name):
    return name.startswith("http")


def printHeader(title, outfile):
    """Print the header for each file analyzed"""

    print >> outfile, "<h3>%s</h3>" % title.encode('utf-8')


def print_results_text(results, out):
    """Print the results to file-like object out
    
    @param results: The wordcount results
    @param out: A file-like object
    """

    data, total_seg = results

    top_row, rest = data[0], data[1:]

    print >> out, "\t".join([x.encode("utf-8") for x in top_row])

    for row in rest:
        prow = [row[0].encode("utf-8")] + row[1:]
        print >> out, "\t".join(["%s" % x for x in prow])

    row = [_("Total").encode("utf-8"),
           total_seg.words,
           total_seg.characters,
           total_seg.chars_no_spaces,
           total_seg.asian_chars,
           total_seg.non_asian_words]

    print >> out, "\t".join(["%s" % x for x in row])


def make_title_header(filename):
    if filename.startswith("http"):
        return _("Results for %s") % filename
    elif os.path.isfile(filename):
        return _("Results for %s") % os.path.split(filename)[-1]
    else:
        return filename


def print_results(result, outfile):
    """Prints the results for a file analysis to a table"""

    filename, stats = result
    title = make_title_header(filename)

    columns = [_("Score"),
               _("<b>Words</b>"),
               _("<b>Chars</b>"),
               _("<b>Chars <br />(no spaces)</b>"),
               _("<b>Asian</b>"),
               _("<b>Non-Asian Words</b>")]

    repetitionRow = ["Repetitions"] + segstat2list(stats.repetitions)

    data = []
    for key, segstat in stats.match_ranges.items():
        data.append([key] + segstat2list(segstat))

    data.sort()
    data.reverse()

    data = [repetitionRow] + data
    totals = makeTotalsRow(data)

    assert isinstance(title, unicode)
    printHeader(title, outfile)
    print >> outfile, "<table border=0>"

    print_row(columns, outfile)
    print_row(repetitionRow, outfile)

    printData = [columns] + data
    for row in printData[2:]:
        row[0] = range2item(row[0])
        print_row(row, outfile)

    print_row(totals, outfile)
    print >> outfile, "</table>"


START_ENGLISH = "startE.html"
START_JAPANESE = "startJ.html"


class ListenerPage(wx.html.HtmlWindow):
    def unregisterBroadcastListeners(self):
        broadcaster.unregisterBroadcastListener(self)


# ###########################
# HTML Page                #
############################
class StartPage(ListenerPage):
    def __init__(self, parent, callbacks):
        wx.html.HtmlWindow.__init__(self, parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)

        broadcaster.registerBroadcastListeners(self)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy)

        self.SetPage(self.get_page())
        self.callbacks = callbacks
        self.active = True

    def get_page(self):
        """Get page in correct language"""

        language = model.get_language()

        if language == "Japanese":
            filename = resource_file_name(START_JAPANESE)
        else:
            filename = resource_file_name(START_ENGLISH)

        return unicode(open(filename, "r").read(), "utf8")

    def onDestroy(self, event):
        self.unregisterBroadcastListeners()
        event.Skip()

    def OnLinkClicked(self, linkinfo):
        LOGGER.debug(u'onLinkClicked: %s' % linkinfo.Href)
        lastBit = linkinfo.Href.split('#')[-1]
        if '.htm' not in lastBit:
            assert "#" in linkinfo.Href
            if lastBit == 'on_analyze':
                LOGGER.debug(u'analyze link clicked')
                self.callbacks[lastBit]()

            else:
                broadcaster.Broadcast('event', lastBit, linkinfo)
            linkinfo.Cancel = True

    @EventHandler("event", "on_print")
    def on_print(self):
        if not self.active:
            return

        printer = wx.html.HtmlEasyPrinting()
        printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        printer.PrintText(self.get_page())

    @EventHandler("event", "on_select_all")
    def on_select_all(self):
        if not self.active:
            return
        self.SelectAll()

    @EventHandler("event", "on_copy")
    def on_copy(self):
        if not self.active:
            return
        text_data = wx.TextDataObject(self.SelectionToText())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(text_data)
            wx.TheClipboard.Close()

    @EventHandler("language", "changed")
    def on_language_changed(self):
        """Respond to language changed broadcast by setting page
        to correct language"""

        self.SetPage(self.get_page())

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


assert issubclass(StartPage, wx.html.HtmlWindow)

REPORT_TEMPLATE = """<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
</head>
<body>

%s

</body>
</html>"""


class ReportPage(ListenerPage):
    """
    Displays analysis results
    """

    def __init__(self, results, parent):
        self.initSuper(parent)
        self.init_base()

        self.active = False

        self.results = results
        self.showResults(results)

        self.name = _("Report")
        self._saveName = None

        self.file_type = "html"

    def init_base(self):
        """
        We override this in the fake class for unit testing
        """

        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy)

        broadcaster.registerBroadcastListeners(self)

    def onDestroy(self, event):
        self.unregisterBroadcastListeners()
        event.Skip()

    @EventHandler("event", "on_print")
    def on_print(self):
        """Prints results if active"""

        if not self.active:
            return

        printer = wx.html.HtmlEasyPrinting()
        printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        printer.PrintText(self.page)

    @EventHandler("event", "on_save")
    def on_save(self):
        """Saves report to HTML file if active"""

        self.on_save_as()

    def get_save_text(self, results):
        """Saves report to HTML file if active"""

        outfile = cStringIO.StringIO()

        for result in results:
            print_results_text(result, outfile)

        return outfile.getvalue()


    def makeName(self, name):
        """Creates a tab name from the file name"""

        base = os.path.basename(name)
        return base.split('.')[0]

    def do_save(self):
        fp = open(self._saveName, "w")
        if self.file_type == "text":
            print >> fp, self.get_save_text(self.results)
        else:
            print >> fp, self.formatResults(self.results)
        fp.close()

        self.name = self.makeName(self._saveName)
        broadcaster.Broadcast("page", "saved", self.name)

    @EventHandler("event", "on_save_as")
    def on_save_as(self):
        """Shows save file dialog, then saves file"""

        if not self.active:
            return False

        wildcard = u"|".join([u"HTML File",
                              u"*.html;*.htm",
                              u"Text File (tab-delimited)",
                              u"*.txt",
                              u"All Files (*.*)",
                              u"*.*"])

        dlg = wx.FileDialog(
            self, message=_("Save Report"), defaultFile=self.name,
            wildcard=wildcard, style=wx.SAVE | wx.CHANGE_DIR
        )
        try:
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                filename = dlg.GetPath()
                self._saveName = filename
                LOGGER.debug(u"Save name is %s" % filename)
                LOGGER.debug(u"Filter index is %s" % dlg.FilterIndex)
                if dlg.FilterIndex == 1:
                    LOGGER.debug("Saving as text")
                    self.file_type = "text"
                    if not u"." in self._saveName:
                        self._saveName = self._saveName + u".txt"
                else:
                    if not u"." in self._saveName:
                        self._saveName = self._saveName + u".html"
                self.do_save()
                return True
        finally:
            dlg.Destroy()
            return False


    # Edit menu
    @EventHandler("event", "on_undo")
    def on_undo(self):
        """
        Not implemented!
        """

        if not self.active:
            return
        LOGGER.warn("undo not implemented in report page!")

    @EventHandler("event", "on_redo")
    def on_redo(self):
        """Not implemented!"""

        if not self.active:
            return
        LOGGER.warn("redo not implemented in report page!")

    @EventHandler("event", "on_copy")
    def on_copy(self):
        """Copies current selection to the clipboard"""

        if not self.active:
            return
        text_data = wx.TextDataObject(self.SelectionToText())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(text_data)
            wx.TheClipboard.Close()

    @EventHandler("event", "on_cut")
    def on_cut(self):
        """Cuts current selection into the clipboard"""

        if not self.active:
            return
        LOGGER.debug("%s: on_cut" % self)

    @EventHandler("event", "on_paste")
    def on_paste(self):
        """Clipboard past action"""

        if not self.active:
            return

        LOGGER.warn("paste not implemented in report page!")

    @EventHandler("event", "on_delete")
    def on_delete(self):
        """Reponds to delete key"""

        if not self.active:
            return

        LOGGER.warn("delete not implemented in report page!")

    @EventHandler("event", "on_select_all")
    def on_select_all(self):
        """Responds to select all command if active"""

        if not self.active:
            return
        self.SelectAll()

    def initSuper(self, parent):
        """Overridden in unit testing class"""

        wx.html.HtmlWindow.__init__(self, parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)

    @EventHandler("language", "changed")
    def on_language_changed(self):
        """Respond to language changed broadcast by showing
        report in the correct language"""

        self.showResults(self.results)

    def showResults(self, results):
        """Format and display the results"""

        self.results = results

        self.page = unicode(self.formatResults(self.results), "utf-8")
        self.SetPage(self.page)

    def activate(self):
        """The page has been activated"""

        self.active = True

    def deactivate(self):
        """The page has been deactivated"""

        self.active = False

    def formatResults(self, results):
        """Format the results into HTML tables"""

        outfile = cStringIO.StringIO()

        for result in results:
            print_results(result, outfile)

        val = outfile.getvalue()
        return REPORT_TEMPLATE % val


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()