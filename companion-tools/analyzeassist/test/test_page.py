# coding: UTF8
"""
Unit tests for page module

"""

from nose.tools import raises

from AnalyzeAssist.view import page

import cStringIO
from AnalyzeAssist.output_format import print_row, format_num
from test_utilities import Bunch
from AnalyzeAssist.view.page import _

@raises(AssertionError)
def test_module():
    """Make sure that our module is being picked up in unit tests"""

    assert False


def test_format_num():
    assert "32" == format_num("32")
    assert "32" == format_num(32)
    assert "3,200" == format_num("3200")
    assert "3,200" == format_num(3200)


def test_badformat_num():
    assert "cat" == format_num("cat")


def test_printRow():
    buffer = cStringIO.StringIO()

    row = ["abc", format_num("1234")]

    print_row(row, buffer)

    val = buffer.getvalue()

    assert val == """<tr>
<td><b>abc</b></td>
<td align="right">1,234</td>
</tr>
""", val


def test_segstat2list():
    bunch = Bunch(words=1,
                  characters=2,
                  chars_no_spaces=3,
                  asian_chars=4,
                  non_asian_words=5)

    assert page.segstat2list(bunch) == [1, 2, 3, 4, 5], page.segstat2list(bunch)


def test_makeTotalsRow():
    data = [["abc", 5, 10],
            ["foo", 3, 2]]

    totalsRow = page.makeTotalsRow(data)

    assert totalsRow == [u"Totals", "<b>8</b>", "<b>12</b>"], totalsRow


def test_printHeader():
    buffer = cStringIO.StringIO()
    page.printHeader(u"TOTALS", buffer)
    val = buffer.getvalue()

    assert val == "<h3>TOTALS</h3>\n", val

    buffer = cStringIO.StringIO()
    page.printHeader(u"Results for c:\\test\\foo.txt", buffer)
    val = buffer.getvalue()

    assert val == "<h3>Results for c:\\test\\foo.txt</h3>\n", val


def test_range2item():
    assert page.range2item((0, 0)) == "0%"
    assert page.range2item((10, 20)) == "10&ndash;20%"
    assert page.range2item((100, 100)) == "100%"


@raises(AssertionError)
def testBadRange2Item():
    page.range2item((20, 10))


class FakeReportPage(page.ReportPage):
    def registerBroadcastListeners(self):
        pass


broken_TestReportPage = '''
class TestReportPage:
    def setUp(self):
        matcher = SegMatcher([r"c:\test\a.xml"])
        totalstats = docstats.DocStats()

        result = file_analysis.get_result(None,
                                          textseg.Segmenter(),
                                          r"c:\test\a.txt",
                                          totalstats,
                                          matcher)

        data = ["spam.txt", 10, 10, 10, 10, 10]
        results = [result]
        self.page = FakeReportPage(results, None)

    def testActivate(self):

        assert self.page.active == False
        self.page.activate()
        assert self.page.active == True
        self.page.deactivate()
        assert self.page.active == False

    def testName(self):

        assert self.page.name == _("Report")
        assert not self.page._saveName

    def test_makeName(self):

        assert "foo" == self.page.makeName(r"c:\foo.txt")

    def testFormatResults(self):
        segbunch = Bunch(words=1,
                      characters=2,
                      chars_no_spaces=3,
                      asian_chars=4,
                      non_asian_words=5)
        stats = Bunch(repetitions = segbunch, match_ranges = { (0,50) : segbunch, (51,100) : segbunch })
        results = [(u"TOTALS", stats)]

        AnalyzeAssist.model.language.language = "English"
        formattedResults = self.page.formatResults(results)
        assert formattedResults == """<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
</head>
<body>

<h3>TOTALS</h3>
<table border=0>
<tr>
<td><b>Score</b></td>
<td align="right"><b>Words</b></td>
<td align="right"><b>Chars</b></td>
<td align="right"><b>Chars <br />(no spaces)</b></td>
<td align="right"><b>Asian</b></td>
<td align="right"><b>Non-Asian Words</b></td>
</tr>
<tr>
<td><b>Repetitions</b></td>
<td align="right">1</td>
<td align="right">2</td>
<td align="right">3</td>
<td align="right">4</td>
<td align="right">5</td>
</tr>
<tr>
<td><b>51&ndash;100%</b></td>
<td align="right">1</td>
<td align="right">2</td>
<td align="right">3</td>
<td align="right">4</td>
<td align="right">5</td>
</tr>
<tr>
<td><b>0&ndash;50%</b></td>
<td align="right">1</td>
<td align="right">2</td>
<td align="right">3</td>
<td align="right">4</td>
<td align="right">5</td>
</tr>
<tr>
<td><b>Totals</b></td>
<td align="right"><b>3</b></td>
<td align="right"><b>6</b></td>
<td align="right"><b>9</b></td>
<td align="right"><b>12</b></td>
<td align="right"><b>15</b></td>
</tr>
</table>


</body>
</html>""", formattedResults
'''


class TestMakeHeader:
    def test_url(self):
        title = page.make_title_header("http://ginstrom.com")
        expected = _("Results for http://ginstrom.com")
        assert title == expected, (title, expected)

    def test_filename(self):
        title = page.make_title_header("c:\\keys.txt")
        expected = "c:\\keys.txt"
        assert title == expected, (title, expected)

    def test_total(self):
        title = page.make_title_header("TOTALS")
        expected = _("TOTALS")
        assert title == expected, (title, expected)
