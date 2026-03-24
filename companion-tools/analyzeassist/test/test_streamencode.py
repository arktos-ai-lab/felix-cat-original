# coding: UTF8
"""
Tests the streamencode module

"""

import sys
from AnalyzeAssist.streamencode import OutStreamEncoder
from nose.tools import raises
from cStringIO import StringIO


@raises(AssertionError)
def test_module():
    """Ensure that the unit tests are running on this module..."""
    assert False


def test_OutStreamEncoderCStringIO():
    out = StringIO()
    out = OutStreamEncoder(out, "utf-8")
    print >> out, u"日本語"
    value = out.getvalue()
    assert value == "日本語\n", value
    assert unicode(value, "utf-8") == u"日本語\n", unicode(value, "utf-8")


def test_OutStreamEncoderStdOut():
    old_stdout = sys.stdout
    sys.stdout = OutStreamEncoder(sys.stdout, "utf-8")
    print u"日本語"
    sys.stdout = old_stdout


def test_OutStreamEncoderUtf8():
    out = StringIO()
    out = OutStreamEncoder(out, "utf-8")
    print >> out, "日本語"
    value = out.getvalue()
    assert value == "日本語\n", value
    assert unicode(value, "utf-8") == u"日本語\n", unicode(value, "utf-8")
