# coding: UTF8
"""
Unit tests for the file_analysis module

"""

from nose.tools import raises
from AnalyzeAssist import file_analysis
from AnalyzeAssist import model

from cStringIO import StringIO
from AnalyzeAssist import broker
from AnalyzeAssist import broadcaster
import inspect


@raises(AssertionError)
def test_module():
    """Ensure that the unit tests are running on this module..."""
    assert False


def test_is_url_http():
    assert file_analysis.is_url("http://ginstrom.com/")


def test_is_url_https():
    assert file_analysis.is_url("https://ginstrom.com/")


def test_is_url_no():
    assert not file_analysis.is_url("c:\\foo.txt")


class TestMakeFullPath:
    def test_url(self):
        options = dict(directory="c:\\",
                       extension="txt")

        path = file_analysis.make_full_path("http://ginstrom.com/", options)
        assert path == "c:\\ginstrom.com_.txt.txt", path


class FakeNomatchWriter(file_analysis.NomatchWriter):
    def __init__(self, filename, fuzzy_options):
        file_analysis.NomatchWriter.__init__(self, filename, fuzzy_options)

    def init_fp(self, filename):
        self.fp = StringIO()

    def close_fp(self):
        self.val = self.fp.getvalue()


class TestGetNomatchWriter:
    def test_devnull(self):
        writer = file_analysis.get_nomatch_writer("spam", {})
        assert writer == file_analysis.devnull_nomatch, writer
        assert not inspect.ismethod(writer), writer


class TestGetResults:
    def setup(self):
        self.oldextension = model.get_fuzzy_options()
        model.set_fuzzy_options({})
        self.devNullSegs = []
        file_analysis.devnull_nomatch = self.fakeDevNull

    def teardown(self):
        model.set_fuzzy_options(self.oldextension)

    def fakeDevNull(self, seg):
        self.devNullSegs.append(seg)

    def testAllMatch(self):
        results = file_analysis.get_results(["/dev/python/Test Files/test/a_text.xml"],
                                            ["/dev/python/Test Files/test/a.xml"],
                                            FakeNomatchWriter)

        print results
        ranges = results[0][1].match_ranges

        key = (100, 100)
        assert ranges[key].characters == 9, ranges[key].characters
        key = (85, 94)
        assert ranges[key].characters == 0, ranges[key].characters
        key = (95, 99)
        assert ranges[key].characters == 0, ranges[key].characters
        key = (0, 84)
        assert ranges[key].characters == 0, ranges[key].characters

        assert self.devNullSegs == [], self.devNullSegs

    def testNoMemories(self):
        results = file_analysis.get_results(["/dev/python/Test Files/test/a_text.xml"], [], {})
        print results
        ranges = results[0][1].match_ranges

        print ranges.items()

        key = (100, 100)
        assert ranges[key].characters == 0, ranges[key].characters
        key = (85, 94)
        assert ranges[key].characters == 0, ranges[key].characters
        key = (95, 99)
        assert ranges[key].characters == 0, ranges[key].characters
        key = (0, 84)
        assert ranges[key].characters == 9, ranges[key].characters

        assert self.devNullSegs == [u'abc', u'def', u'ghi'], self.devNullSegs


class TestNomatchWriter:
    def setup(self):
        self.writer = FakeNomatchWriter("c:\\foo.txt", dict(extension="fuzzy", directory=None))

    def testCreate(self):
        pass

    def testWriteOneLine(self):
        self.writer("foo")

        value = self.writer.fp.getvalue()
        assert value == "foo\n", value

    def testWriteTwoLines(self):
        self.writer("foo")
        self.writer("bar")

        value = self.writer.fp.getvalue()
        assert value == "foo\nbar\n", value


def test_make_full_path():
    path_to_analysis_file = r"c:\foo.doc"
    dir = r"d:\spam"
    ext = "fuzz"

    full_path = file_analysis.make_full_path(path_to_analysis_file,
                                             dict(extension=ext,
                                                  directory=dir))

    assert full_path == r"d:\spam\foo.doc.fuzz.txt", full_path
