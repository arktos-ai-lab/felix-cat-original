# coding: UTF8
"""
Unit test extract_segments

"""

from AnalyzeAssist import extract_segments
from nose.tools import raises
import os


def setup():
    print
    print "=" * 30
    print "Running tests on extract_segments"


def teardown():
    print "...tests complete!"
    print "=" * 30
    print


@raises(AssertionError)
def test_module():
    """Make sure that unit tests for this module are being picked up"""

    assert False


def runOnFile(filename, expected):
    print "*" * 10
    print "Testing file", filename

    if os.path.exists(filename + ".segs.txt"):
        os.remove(filename + ".segs.txt")

    extract_segments.main(["-e", ".segs.txt", "-f", filename, ])

    assert os.path.exists(filename + ".segs.txt")
    text = open(filename + ".segs.txt", "r").read()

    assert text == expected, "Expected [%s] but actually [%s]" % \
                             (expected, text)

    print "...tests passed!"
    print "*" * 10
    print


def test_a_main():
    """
    Smoke test the extract_segments utility using file /test/a.txt
    """

    filename = "c:/test/a.txt"

    extract_segments.main(["-e", ".segs.txt", "-f", filename, "-n"])

    assert os.path.exists(filename + ".segs.txt")
    text = open(filename + ".segs.txt", "r").read()

    expected = """abc
def
abcd
abc.
def.
"""
    assert text == expected, "Expected [%s] but actually [%s]" % \
                             (expected, text)


def test_withnums():
    runOnFile("c:/test/withnums.txt", """Here is a table of numbers.
foo
bar
""")


def test_sentences():
    runOnFile("c:/test/sentences.txt", """This is a table.
See Dick run.
Run Dick, run!
Janes sees Dick run.
Dick runs and runs.
""")


def test_japaneseutf8():
    runOnFile("c:/test/japaneseutf8.txt", """日本語
英語
本日晴天なり。
なるほど
""")


def test_japanese():
    runOnFile("c:/test/japanese.txt", """日本語
英語
本日晴天なり。
なるほど
""")