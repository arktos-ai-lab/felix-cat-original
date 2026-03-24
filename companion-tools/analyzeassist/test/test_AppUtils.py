# coding: UTF8
"""
Test app utils
"""

from AnalyzeAssist import broker

broker.checkProv = lambda x: x
from AnalyzeAssist import AppUtils
from nose.tools import raises
from cStringIO import StringIO
import cPickle
import os


@raises(AssertionError)
def test_module():
    assert False


def testFrozen():
    assert AppUtils.we_are_frozen() == False


def test_module_path_SetFrozen():
    import sys

    if not hasattr(sys, "frozen"):
        sys.frozen = "windows_exe"
        sys.executable = "d:\\spam.exe"
        assert AppUtils.module_path() == 'd:\\'
        del sys.frozen


def test_module_path():
    expected = r'd:\dev\python\analyzeassist'.lower()
    actual = AppUtils.module_path().lower()
    assert actual == expected, (actual, expected)


class TestLoad:
    @raises(IOError)
    def test_fake_file(self):
        assert not AppUtils.load('someFileThatDoesNotExist.foo')

    def test_empty_file(self):
        os.chdir(os.path.dirname(__file__))
        assert AppUtils.load('empty.txt') is None

    def test_load_and_serialize(self):
        fname = AppUtils.file_name("test_data.txt")

        data = [3, 4.5, "spam", {'spam': 'eggs'}]

        AppUtils.serialize(data, fname)
        loadedData = AppUtils.load(fname)

        for old, new in zip(data, loadedData):
            assert old == new


class TestLoadFromStream:
    def test_empty(self):
        out = StringIO()
        cPickle.dump(None, out)
        out.seek(0)
        assert AppUtils.load_from_stream(out) is None

    def test_dict(self):
        out = StringIO()
        data = dict(spam="eggs", integer=3, floatingpoint=4.5)
        cPickle.dump(data, out)
        out.seek(0)
        loaded_data = AppUtils.load_from_stream(out)
        assert data == loaded_data, (data, loaded_data)


def test_get_resource_filename():
    res_filename = AppUtils.resource_file_name("aboutE.html")

    expected = r"D:\dev\python\AnalyzeAssist\res\aboutE.html"
    assert res_filename == expected, res_filename
