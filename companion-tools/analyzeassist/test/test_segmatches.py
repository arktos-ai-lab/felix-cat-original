# coding: UTF8
"""
Test the segmatches module

"""

import unittest
import os

from nose.tools import raises

from AnalyzeAssist import debugging
from AnalyzeAssist import segmatches


@raises(AssertionError)
def test_module():
    """Make sure that unit tests for this module are being picked up"""

    assert False


class TestLoadMemories(object):
    def setup(self):
        self.base_path = r"D:\dev\python\Test Files\MemoryFiles"

    def make_path(self, filename):
        return os.path.join(self.base_path, filename)

    def test_empty_file(self):
        filename = "EmptyFile.xml"
        records = segmatches.load_memory(self.make_path(filename))

        assert records == [], records

    def test_empty_memory(self):
        filename = "EmptyMemory.xml"
        records = segmatches.load_memory(self.make_path(filename))

        assert records == [], records

    def test_foo(self):
        filename = "foo.xml"
        records = sorted(segmatches.load_memory(self.make_path(filename)))

        assert records == sorted([u"Hello", u"GoodBye"]), records

    def test_music(self):
        expected = sorted([u"「天使」",
                           u"東京藝術大学",
                           u"東京音楽大学"])

        filename = "Music gloss.xml"
        actual = sorted(segmatches.load_memory(self.make_path(filename)))

        for seg in actual:
            print seg.encode("utf-8")

        assert actual == expected, actual


class TestSegMatcher(object):
    """Test the SegMatcher class, with no memories loaded
    """

    def setup(self):
        self.matcher = segmatches.SegMatcher([])

    def test_simpleCreate(self):
        assert not self.matcher.memories

    def test_getScore(self):
        assert int(segmatches.get_score(u"abc", u"abc") * 100) == 100
        assert int(segmatches.get_score(u"abc", u"123") * 100) == 0
        assert int(segmatches.get_score(u"abcd", u"ab12") * 100) == 50
        assert int(segmatches.get_score(u"abcd", u"abc") * 100) == 75

    def test_repetitions(self):
        match = self.matcher.best_match(u"abc")
        assert match == 0, match

        match = self.matcher.best_match(u"abc")
        assert match == 101, match

        match = self.matcher.best_match(u"abc")
        assert match == 101, match

        match = self.matcher.best_match(u"foo")
        assert match == 0, match


class test_Segmatcher_boxes:
    """Test the SegMatcher class

    Our test memory is:
    /test/boxes.xml
    """

    def setup(self):
        segmatches.MINSCORE = 0.1
        self.matcher = segmatches.SegMatcher(["/dev/python/Test Files/test/boxes.xml"])

    def test_simple(self):
        assert len(self.matcher.memories) == 3, self.matcher.memories

    def test_best(self):
        best_match = self.matcher.best_match(u"And a second, unrelated one.")
        print "Best score is:", best_match
        assert 100 == best_match

        best_match = self.matcher.best_match(u"abc")
        print "Best score is:", best_match
        assert 10 == best_match, best_match

    def test_repetitions(self):
        print self.matcher.memories

        match = self.matcher.best_match(u"And a second, unrelated one.")
        assert match == 100, match

        match = self.matcher.best_match(u"And a second, unrelated one.")
        assert match == 100, match

        match = self.matcher.best_match(u"abc")
        assert match == 10, match

        match = self.matcher.best_match(u"abc")
        assert match == 101, match


@raises(IOError)
def test_load_nonexistent_tmx():
    records = segmatches.load_memory(r"C:\dev\does_not_exist.tmx")


class TestLoadTmxMemoriesEtoJ(object):
    def setup(self):
        segmatches.MINSCORE = 0.1
        self.sources = segmatches.load_memory(r"D:\dev\python\Test Files\TMX\TMX\EtoJap.tmx")

    def test_etoj_load(self):
        pass

    def test_etoj_len(self):
        assert len(self.sources) == 12, len(self.sources)

    def test_etoj_content(self):
        segs = [u"Digitally Sign a Macro Project in Microsoft Word 2000",
                u"Recording a new Macro",
                u"Choose the Security Level you need: High / Medium / Low.",
                u"Click on Tools > Macro > Security to open the Security dialog."]

        print self.sources
        for seg in segs:
            assert seg in self.sources, "%s\n\n%s" % (seg, "\n\t".join(self.sources))


class test_Segmatcher_a:
    """Test the SegMatcher class

    Our test memory is:
    /test/a.xml
    """

    def setup(self):
        segmatches.MINSCORE = 0.1
        self.matcher = segmatches.SegMatcher(["/dev/python/Test Files/test/a.xml"])

    def test_simple(self):
        assert len(self.matcher.memories) == 3

    def test_best(self):
        best_match = self.matcher.best_match(u"abc")
        print "Best score is:", best_match
        assert 100 == best_match

        best_match = self.matcher.best_match(u"And a second, unrelated one.")
        print "Best score is:", best_match
        assert 7 == best_match, best_match

    def test_repetitions(self):
        match = self.matcher.best_match(u"And a second, unrelated one.")
        assert match == 7, match

        match = self.matcher.best_match(u"And a second, unrelated one.")
        assert match == 101

        match = self.matcher.best_match(u"abc")
        assert match == 100

        # If it is a 100% match, we don't track repetitions
        match = self.matcher.best_match(u"abc")
        assert match == 100


class test_Segmatcher_a_boxes:
    """Test the SegMatcher class

    Our test memories are:
    /test/a.xml
    /test/boxes.xml
    """

    def setup(self):
        segmatches.MINSCORE = 0.1
        self.matcher = segmatches.SegMatcher(["/dev/python/Test Files/test/boxes.xml", "/dev/python/Test Files/test/a.xml"])

    def test_simple(self):
        assert len(self.matcher.memories) == 6, len(self.matcher.memories)
        assert "abc" in self.matcher.memories
        assert "And a second, unrelated one." in self.matcher.memories

    def test_best(self):
        best_match = self.matcher.best_match(u"abc")
        print "Best score is:", best_match
        assert 100 == best_match

        best_match = self.matcher.best_match(u"And a second, unrelated one.")
        print "Best score is:", best_match
        assert 100 == best_match

    def test_repetitions(self):
        match = self.matcher.best_match(u"And a second, unrelated one.")
        assert match == 100

        match = self.matcher.best_match(u"And a second, unrelated one.")
        assert match == 100

        match = self.matcher.best_match(u"abc")
        assert match == 100

        match = self.matcher.best_match(u"abc")
        assert match == 100

    @raises(AttributeError)
    def test_badGetScore(self):
        self.matcher.getScore("foo", u"bar")


def test_get_seg_matcher():
    matcher = segmatches.get_seg_matcher([])
    assert "best_match" in dir(matcher)


if __name__ == "__main__":
    unittest.main()
