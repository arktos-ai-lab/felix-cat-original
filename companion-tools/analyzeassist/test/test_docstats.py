# coding: UTF8
"""
Unit test the docstats module
"""

from AnalyzeAssist import docstats
from AnalyzeAssist.docstats import Segment
from nose.tools import raises
from AnalyzeAssist import broker

goodMatchRanges = ('100%', '95-99', '85%-94%', '50 - 84', '25 49', '1% 24%', '0')
badMatchRanges = (
['100%-95 ', 'reason: bigger followed by smaller'], ['95-99-88 ', 'reason: more than two numbers on a line'],
['50 to 84 ', 'reason: numbers separated by word "to"'])

canonicalMatchRangesFileContents = """100%
95-99%
85-94%
0-84%
"""


def ensureGood(val):
    docstats.parse_match_range(val)


def test_good():
    for good in goodMatchRanges:
        ensureGood(good)


def test_bad():
    for bad, msg in badMatchRanges:
        try:
            docstats.parse_match_range(bad)
            raise Exception, "%s should cause error (%s)" % (bad, msg)

        except docstats.BadMatchRangeException, e:
            print "%s creates exception as expected:", (bad, str(e))


def test_badCustom():
    for bad, msg in [['100-99', 'Left value not lower than right value'],
                     ['', 'Blank line'],
                     ['1a0', 'Not a number']]:
        try:
            docstats.parse_match_range(bad)
            raise Exception, "%s should cause error (%s)" % (bad, msg)

        except docstats.BadMatchRangeException, e:
            print "%s creates exception as expected:", (bad, str(e))


def test_getMatchRanges():
    ranges = docstats.get_match_ranges()
    for range in ranges:
        low, high = range
        assert low <= high, range

    brokerRanges = broker.Request("match ranges")

    assert ranges == brokerRanges, (ranges, brokerRanges)


class TestParseMatchValue:
    def test_100(self):
        value = docstats.parse_match_value('100')
        assert 100 == value, value

    def test_50_spaces(self):
        value = docstats.parse_match_value(' 50 ')
        assert 50 == value, value

    def test_30_percent(self):
        value = docstats.parse_match_value('30%')
        assert 30 == value, value

    def test_space_30_percent(self):
        value = docstats.parse_match_value(' 30%')
        assert 30 == value, value

    def test_30_percent_space(self):
        value = docstats.parse_match_value('30% ')
        assert 30 == value, value


def test_parseMatchRangeOneVal():
    vals = docstats.parse_match_range('100')
    assert (100, 100) == vals, "Expected (100, 100) but actually %s" % str(vals)

    assert (50, 50) == docstats.parse_match_range(' 50 ')
    assert (30, 30) == docstats.parse_match_range('30%')
    assert (30, 30) == docstats.parse_match_range(' 30%')
    assert (30, 30) == docstats.parse_match_range('30% ')


def test_parseMatchRangeTwoVals():
    vals = docstats.parse_match_range('95-100')
    assert (95, 100) == vals, "Expected (95, 100) but actually %s" % str(vals)

    assert (20, 50) == docstats.parse_match_range(' 20-50 ')
    assert (15, 30) == docstats.parse_match_range('15-30%')
    assert (15, 30) == docstats.parse_match_range(' 15%-30%')

    vals = docstats.parse_match_range('15 30% ')
    assert (15, 30) == vals, "Expected (15, 30) but actually %s" % str(vals)


@raises(AssertionError)
def test_module():
    """Make sure that unit tests for this module are being picked up"""

    assert False


class test_parseMatchRanges:
    # Non-strings

    @raises(docstats.BadMatchRangeException)
    def test_List(self):
        docstats.parse_match_ranges([])

    @raises(docstats.BadMatchRangeException)
    def test_None(self):
        docstats.parse_match_ranges(None)

    @raises(docstats.BadMatchRangeException)
    def test_Int(self):
        docstats.parse_match_ranges(42)


    # Invalid strings
    @raises(docstats.BadMatchRangeException)
    def test_InvalidRange(self):
        ranges = docstats.parse_match_ranges("""100
            90-80
            0-79""")


    # Valid strings

    def test_1(self):
        ranges = docstats.parse_match_ranges("""100
            80-90
            0-79""")

        assert ranges == [(100, 100), (80, 90), (0, 79)], ranges


    def test_2(self):
        ranges = docstats.parse_match_ranges("""100
            
            """)

        assert ranges == [(100, 100)], ranges


    def test_2(self):
        ranges = docstats.parse_match_ranges("""100
            
            40-50
            """)

        assert ranges == [(100, 100), (40, 50)], ranges


def test_formatMatchRanges():
    actual = docstats.format_match_ranges([(100, 100)])
    assert "100%" == actual, actual

    actual = docstats.format_match_ranges([(100, 100), (40, 50)])
    assert """100%
40-50%""" == actual, actual

    actual = docstats.format_match_ranges([(100, 100), (80, 99), (0, 79)])
    assert """100%
80-99%
0-79%""" == actual, actual

    actual = broker.Request("formatted match ranges", [(100, 100), (80, 99), (0, 79)])
    assert """100%
80-99%
0-79%""" == actual, actual

    actual = broker.Request("formatted match ranges")
    assert actual


def test_getLeftAndRight():
    assert ("100", "100") == docstats.get_left_and_right("100"), docstats.get_left_and_right("100")
    assert ("0", "49") == docstats.get_left_and_right("0-49"), docstats.get_left_and_right("0-49")
    assert ("0%", "0%") == docstats.get_left_and_right("0%"), docstats.get_left_and_right("0%")
    assert ("90", "100") == docstats.get_left_and_right("90-100"), docstats.get_left_and_right("90-100")
    assert ("50%", "65%") == docstats.get_left_and_right("50% 65%"), docstats.get_left_and_right("50% 65%")


class test_setMatchRanges:
    def setup(self):
        self.oldMatchRanges = docstats.get_match_ranges()

    def teardown(self):
        docstats.set_match_ranges(self.oldMatchRanges)


    # Non-strings

    @raises(docstats.BadMatchRangeException)
    def test_List(self):
        docstats.set_match_ranges([])

    @raises(docstats.BadMatchRangeException)
    def test_None(self):
        docstats.set_match_ranges(None)

    @raises(docstats.BadMatchRangeException)
    def test_Int(self):
        docstats.set_match_ranges(42)


def test_nonJLen():
    assert docstats.non_j_len(u"日本語AアジアンB") == 2
    assert docstats.non_j_len("hello") == 1
    assert docstats.non_j_len(u"日本") == 0


def test_filter_char():
    assert docstats.filter_char(u"日") == ' '
    assert docstats.filter_char(u"a") == 'a'
    assert docstats.filter_char(u".") == '.'
    assert docstats.filter_char(u"1") == '1'


class TestSegment:
    def failUnless(self, expr):
        assert expr

    def failUnlessEqual(self, lhs, rhs):
        assert lhs == rhs, (lhs, rhs)

    def testSimple(self):
        segment = Segment("foo")
        self.failUnlessEqual(1, segment.words)
        self.failUnlessEqual(3, segment.characters)
        self.failUnlessEqual(3, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)

    def testSentence(self):
        segment = Segment("foo is a bar")
        self.failUnlessEqual(4, segment.words)
        self.failUnlessEqual(12, segment.characters)
        self.failUnlessEqual(9, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)

    def testIdeographicSpace(self):
        segment = Segment(u"　spam")
        self.failUnlessEqual(1, segment.words)
        self.failUnlessEqual(5, segment.characters)
        self.failUnlessEqual(4, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)

    def testJSentence(self):
        segment = Segment(u"本日晴天なり。")
        self.failUnlessEqual(7, segment.words)
        self.failUnlessEqual(7, segment.characters)
        self.failUnlessEqual(7, segment.chars_no_spaces)
        self.failUnlessEqual(7, segment.asian_chars)

    def testconstructor(self):
        segment = Segment("")
        self.failUnlessEqual(0, segment.words)
        self.failUnlessEqual(0, segment.characters)
        self.failUnlessEqual(0, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)
        self.failUnlessEqual(0, segment.non_asian_words)

    def testOneWord(self):
        segment = Segment("foo")
        self.failUnlessEqual(1, segment.words)
        self.failUnlessEqual(3, segment.characters)
        self.failUnlessEqual(3, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)
        self.failUnlessEqual(1, segment.non_asian_words)

    def testSimpleSentence(self):
        segment = Segment("This is a simple sentence.")
        self.failUnlessEqual(5, segment.words)
        self.failUnlessEqual(26, segment.characters)
        self.failUnlessEqual(22, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)
        self.failUnlessEqual(5, segment.non_asian_words)

    def testSimpleSentenceWithJ(self):
        segment = Segment(u"This is a simple sentence. 日本語もある。")
        self.failUnlessEqual(12, segment.words)
        self.failUnlessEqual(34, segment.characters)
        self.failUnlessEqual(29, segment.chars_no_spaces)
        self.failUnlessEqual(7, segment.asian_chars)
        self.failUnlessEqual(5, segment.non_asian_words)

    def test_AccumulateSimple_SimpleWithJ(self):
        segment = Segment("")
        segment1 = Segment("This is a simple sentence.")
        segment.accumulate(segment1)

        self.failUnlessEqual(5, segment.words)
        self.failUnlessEqual(26, segment.characters)
        self.failUnlessEqual(22, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)
        self.failUnlessEqual(5, segment.non_asian_words)

        segment2 = Segment(u"This is a simple sentence. 日本語もある。")
        segment.accumulate(segment2)

        self.failUnlessEqual(12 + 5, segment.words)
        self.failUnlessEqual(34 + 26, segment.characters)
        self.failUnlessEqual(29 + 22, segment.chars_no_spaces)
        self.failUnlessEqual(7 + 0, segment.asian_chars)
        self.failUnlessEqual(5 + 5, segment.non_asian_words)


    def testPunctLine(self):
        segment = Segment(u"{|}C:\\dev\\c++\\WTL80_6137\\Samples\\WTLExplorer\\res\\WTLExplorer.ico{|}t{|}")
        self.failUnlessEqual(1, segment.words)
        self.failUnlessEqual(71, segment.characters)
        self.failUnlessEqual(71, segment.chars_no_spaces)
        self.failUnlessEqual(0, segment.asian_chars)
        self.failUnlessEqual(1, segment.non_asian_words)

    def testWordliness(self):
        """The characters (no spaces) count won't match, because we are not counting
        spaces between segments"""

        text = u"""There was no time to waste (was there any?). The haste-making were-rats were upon the peaceful Ur*hamsters; and the destruction ? nay, the devoration ? was upon them, to the 2^4 and the 2-5th generations! (日本語も挿入しておく)"""
        segment = Segment(text)
        self.failUnlessEqual(47, segment.words)
        self.failUnlessEqual(217, segment.characters)
        self.failUnlessEqual(182, segment.chars_no_spaces)
        self.failUnlessEqual(10, segment.asian_chars)  # 10 jibes with Word, but we are fudging Unicode
        # ndashes into single byte...
        self.failUnlessEqual(37, segment.non_asian_words)


class mockMatch:
    def __init__(self, score=100):
        self.score = score


class testDocStats:
    def setup(self):
        self.ds = docstats.DocStats()
        self.ds.match_ranges = {(100, 100): Segment(""),
                                (95, 99): Segment(""),
                                (80, 94): Segment(""),
                                (0, 79): Segment("")}


    def testCreate(self):
        assert len(self.ds.match_ranges) > 0

        for left, right in self.ds.match_ranges:
            assert left <= right

    def testGetRange(self):
        assert self.ds.get_range(100) == (100, 100)

        assert self.ds.get_range(95) == (95, 99)
        assert self.ds.get_range(99) == (95, 99)
        assert self.ds.get_range(97) == (95, 99)

        assert self.ds.get_range(80) == (80, 94)
        assert self.ds.get_range(92) == (80, 94)
        assert self.ds.get_range(94) == (80, 94)

        assert self.ds.get_range(0) == (0, 79)
        assert self.ds.get_range(25) == (0, 79)
        assert self.ds.get_range(50) == (0, 79)
        assert self.ds.get_range(79) == (0, 79)

        assert self.ds.get_range(-10) is None
        self.ds.match_ranges = {(100, 100): Segment(""),
                                (95, 99): Segment(""),
                                (80, 94): Segment("")}
        assert self.ds.get_range(50) is None

    def testAddSeg(self):
        seg1 = Segment("foo")
        seg2 = Segment("bar")

        self.ds.add_seg(seg1, 100)
        self.ds.add_seg(seg2, 100)

        numwords = self.ds.match_ranges[(100, 100)].words
        assert numwords == 2, numwords
        assert self.ds.match_ranges[(100, 100)].characters == 6
        assert self.ds.match_ranges[(100, 100)].chars_no_spaces == 6
        assert self.ds.match_ranges[(100, 100)].asian_chars == 0
        assert self.ds.match_ranges[(100, 100)].non_asian_words == 2

    def testAddSeg90Japanese(self):
        self.ds.add_seg(Segment(u"日本語"), 90)
        self.ds.add_seg(Segment(u"foo bar"), 90)

        assert self.ds.match_ranges[(100, 100)].words == 0
        assert self.ds.match_ranges[(100, 100)].characters == 0
        assert self.ds.match_ranges[(100, 100)].chars_no_spaces == 0
        assert self.ds.match_ranges[(100, 100)].asian_chars == 0
        assert self.ds.match_ranges[(100, 100)].non_asian_words == 0

        numwords = self.ds.match_ranges[(80, 94)].words
        assert numwords == 5, numwords
        assert self.ds.match_ranges[(80, 94)].characters == 10
        assert self.ds.match_ranges[(80, 94)].chars_no_spaces == 9
        assert self.ds.match_ranges[(80, 94)].asian_chars == 3
        assert self.ds.match_ranges[(80, 94)].non_asian_words == 2

    def testAddSegRepetitionJapanese(self):
        self.ds.add_seg(Segment(u"日本語"), 101)
        self.ds.add_seg(Segment(u"foo bar"), 101)

        assert self.ds.match_ranges[(100, 100)].words == 0
        assert self.ds.match_ranges[(100, 100)].characters == 0
        assert self.ds.match_ranges[(100, 100)].chars_no_spaces == 0
        assert self.ds.match_ranges[(100, 100)].asian_chars == 0
        assert self.ds.match_ranges[(100, 100)].non_asian_words == 0

        assert self.ds.match_ranges[(80, 94)].words == 0
        assert self.ds.match_ranges[(80, 94)].characters == 0
        assert self.ds.match_ranges[(80, 94)].chars_no_spaces == 0
        assert self.ds.match_ranges[(80, 94)].asian_chars == 0
        assert self.ds.match_ranges[(80, 94)].non_asian_words == 0

        assert self.ds.repetitions.words == 5, self.ds.repetitions.words
        assert self.ds.repetitions.characters == 10
        assert self.ds.repetitions.chars_no_spaces == 9
        assert self.ds.repetitions.asian_chars == 3
        assert self.ds.repetitions.non_asian_words == 2


def test_getDocStats():
    docStats = docstats.get_doc_stats()
    assert "add_seg" in dir(docStats)
    assert "get_range" in dir(docStats)

    docStats = broker.Request("DocStats")
    assert "add_seg" in dir(docStats)
    assert "get_range" in dir(docStats)