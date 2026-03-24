# coding: UTF8
"""
Document statistics

Match-range text file is a list of ranges, one range to a line.
Here are some examples of good formats:
    "100", "100%", "80-90%", "80% 90%", "80%-90%", "80 90"

When there are two numbers, they must be lower to higher.

Match ranges are a list of tuples, in the form (low, high).
If the range is a single percentage, then low==high

in all cases, val >= 0 and val <= 100 for val in range
"""
import logging
import shutil

from AnalyzeAssist import broker
import os
from AnalyzeAssist.broker import BrokerRequestHandler
from AnalyzeAssist.broadcaster import EventHandlerFunction as EventHandler
from AnalyzeAssist import broadcaster
from segmenter.chunker import is_asian
from AnalyzeAssist.AppUtils import module_path, get_local_app_data_folder

IDEOGRAPHIC_SPACE = unichr(0x3000)
MATCH_RANGE_FILENAME = "match_ranges.txt"
MINSCORE = 1.0
LOGGER = logging.getLogger(__name__)


class BadMatchRangeException(Exception):
    """We raise this when we fail to parse a match range"""
    pass


def parse_match_value(val):
    """Parse the match string into a value, e.g.

    >>> parse_match_value('100')
    100
    >>> parse_match_value(' 50')
    50
    >>> parse_match_value('30%')
    30
    """

    val = val.replace('%', '')
    return int(val)


def split_range_line(line):
    """Here we assume we have a line with one or more numbers, divided by spaces.

    >>> split_range_line('90 100')
    ['90', '100']
    >>> split_range_line('50')
    ['50', '50']
    >>> split_range_line(None)
    Traceback (most recent call last):
        ...
        vals = [ val for val in line.split() if val ]
    AttributeError: 'NoneType' object has no attribute 'split'
    """

    vals = [val for val in line.split() if val]
    if len(vals) == 2:
        return vals
    elif len(vals) == 1:
        return [vals[0], vals[0]]
    else:
        raise BadMatchRangeException("%s: Invalid syntax" % line)


def get_left_and_right(line):
    """parse C{line} into left and right values

    >>> get_left_and_right('10-100')
    ('10', '100')
    >>> get_left_and_right('100')
    ('100', '100')
    >>> get_left_and_right('20 39%')
    ('20', '39%')

    Things that will cause an exception:

    >>> get_left_and_right('100-')
    Traceback (most recent call last):
        ...
        raise BadMatchRangeException, "Syntax error in line [%s]" % line
    BadMatchRangeException: Syntax error in line [100-]
    >>> get_left_and_right(None)
    Traceback (most recent call last):
        ...
        if '-' in line:
    TypeError: argument of type 'NoneType' is not iterable
    """

    if '-' in line:
        try:
            left, right = line.split('-')
            if not (left and right):
                raise BadMatchRangeException
            return left, right
        except Exception:
            raise BadMatchRangeException, "Syntax error in line [%s]" % line

    else:
        # This will do the right thing if line contains only
        # one value
        left, right = split_range_line(line)
        return left, right


def parse_match_range(line):
    """parse <line> into a match range (low,high)

    >>> parse_match_range('20 100')
    (20, 100)
    >>> parse_match_range('30% - 50%')
    (30, 50)
    >>> parse_match_range('30-50%')
    (30, 50)
    >>> parse_match_range('30 50%')
    (30, 50)

    Things that will cause exceptions:

    >>> parse_match_range('100-90')
    Traceback (most recent call last):
        ...
        raise BadMatchRangeException, "Syntax error in line [%s]" % line
    BadMatchRangeException: 100-90: Value on left not lower than value on right

    >>> parse_match_range(None)
    Traceback (most recent call last):
        ...
        raise BadMatchRangeException, message
    BadMatchRangeException: Error parsing line [None] (argument of type 'NoneType' is not iterable)
    """

    try:
        left, right = get_left_and_right(line)
        lowval, highval = (parse_match_value(left), parse_match_value(right))
        if lowval > highval:
            message = "%s: Value on left not lower than value on right" % line
            raise BadMatchRangeException, message
        global MINSCORE
        MINSCORE = min(MINSCORE, highval / 100.0)
        return (lowval, highval)

    # Pass on BadMatchRangeException, cast other exceptions
    # into BadMatchRangeException
    except BadMatchRangeException, details:
        LOGGER.exception("Bad match range exception")
        raise
    except Exception, details:
        message = "Error parsing line [%s] (%s)" % (line, str(details))
        LOGGER.exception(message)
        raise BadMatchRangeException, message


@BrokerRequestHandler("match ranges")
def get_match_ranges():
    """Retrieve the match-range preferences from the textfile
    L{MATCH_RANGE_FILENAME}, and return them parsed as a list of tuples
    """

    text = open(get_match_range_filename(), "r").read()
    return parse_match_ranges(text)


def parse_match_ranges(text):
    """Parse a text string of match ranges (one to a line)
    into a list of range tuples in the form (low,high)

    @param text: the text list of ranges
    """
    try:
        lines = text.splitlines()
        return [parse_match_range(line) for line in lines if line.strip()]
    except Exception, details:
        LOGGER.exception("Invalid match-range syntax")
        import traceback

        message = "Invalid match-range syntax: " + str(details)
        raise BadMatchRangeException, message


def format_match_ranges(ranges=None):
    """Formats the sequence of (low,high) tuples into text
    (for file/textbox output)

    @param ranges: list of (low,high) number tuples
    """
    if not ranges:
        ranges = get_match_ranges()

    lines = []

    for match_range in ranges:
        left, right = match_range
        assert left <= right

        if left == right:  # one value
            lines.append("%i%%" % left)
        else:
            lines.append("%i-%i%%" % (left, right))

    return '\n'.join(lines)


@BrokerRequestHandler("formatted match ranges")
def broker_format_match_ranges():
    """broker provider of formatted text ranges
    """
    ranges = broker.CurrentData()
    return format_match_ranges(ranges)


def get_match_range_filename():
    """Provides the file name of the match-range file (absolute path)
    """
    filename = os.path.join(get_local_app_data_folder(), MATCH_RANGE_FILENAME)
    if not os.path.exists(filename):
        modfile = os.path.join(module_path(), MATCH_RANGE_FILENAME)
        if os.path.exists(modfile):
            shutil.copy(modfile, filename)
    return filename


def set_match_ranges(match_ranges):
    """text is either a string, one range per line,
    or a list of tuples in the form (low,high)

    In the case of tuples, C{low <= high for each row in text}

    @param match_ranges: the match ranges to classify our matches
    @type match_ranges: a string or tuple
    """

    if isinstance(match_ranges, basestring):
        LOGGER.debug("Setting match ranges: %s" % "; ".join(match_ranges.splitlines()))
    else:
        LOGGER.debug("Setting match ranges: %s" % match_ranges)

    try:
        if not match_ranges:
            raise BadMatchRangeException("text must not be empty")
        outtext = ""
        if isinstance(match_ranges, basestring):
            # Ensures that text ranges are valid
            # Relies on semi-magic of throwing an exception if it doesn't
            # parse...
            parse_match_ranges(match_ranges)
            outtext = match_ranges
        else:
            instance_values = [isinstance(match_ranges, typename)
                               for typename in [tuple, list]]
            if not any(instance_values):
                raise BadMatchRangeException("Bad range type")
            # Ensures that the match range tuples are valid
            outtext = format_match_ranges(match_ranges)

        outfile = open(get_match_range_filename(), "w")
        print >> outfile, outtext
    except BadMatchRangeException, details:
        raise details
    except Exception, details:
        LOGGER.exception("Invalid match-range sytax")
        raise


@EventHandler("match ranges", "changed")
def broadcaster_set_match_ranges():
    """Responds to broadcast that match ranges have changed by writing
    new ranges to file
    """

    set_match_ranges(broadcaster.CurrentData())


def filter_char(c):
    """Filters Asian characters to spaces"""
    if is_asian(c):
        return ' '
    return c


def non_j_len(word):
    u"""Returns number of non-Asian words in C{word}

    >>> non_j_len(u"日本語AアジアンB")
    2
    >>> non_j_len(u"hello")
    1
    >>> non_j_len(u"spam eggs 日本語")
    2
    >>> non_j_len(u"")
    0
    >>> non_j_len(u"日本語")
    0
    """

    # Here are the steps:
    # 本spam本eggs
    # -> [' ', 's', 'p', 'a', 'm', ' ', 'e', 'g', 'g', 's']
    # -> ' spam eggs'
    # -> ['spam', 'eggs']
    # The length of which is 2!
    chars = [filter_char(c) for c in word]
    return len(u''.join(chars).split())


# ###################
# Segment
####################
class Segment(object):
    """Represents a text segment.
    (For bookkeeping)
    """

    def __init__(self, text=""):
        """ text is the segment of text we will calculate.
        Leave it empty if this will be a master count for a document

        @param text: The text of the segment
        """

        self.characters = len(text)

        num_spaces = len([x for x in text if x.isspace()])
        self.chars_no_spaces = self.characters - num_spaces

        self.asian_chars = len([x for x in text if is_asian(x)])

        self.non_asian_words = non_j_len(text)

        self.words = self.non_asian_words + self.asian_chars

    def accumulate(self, seg):
        """Add the stats from <seg> to this one.
        Use this to keep a count for the entire document;
        use another for the whole batch of documents

        @param seg: The segment to accumulate

        >>> seg = Segment(u"")
        >>> seg2 = Segment(u"abc")
        >>> seg.accumulate(seg2)
        >>> seg.words
        1
        >>> seg.characters
        3
        >>> seg = Segment(u"")
        >>> seg.accumulate(u"abc def")
        >>> seg.words
        2
        >>> seg.characters
        7
        """

        if not seg:
            return

        if isinstance(seg, basestring):
            seg = Segment(seg)
        else:
            try:
                seg.words
            except AttributeError:
                seg = Segment(str(seg))

        self.words += seg.words
        self.characters += seg.characters
        self.chars_no_spaces += seg.chars_no_spaces
        self.asian_chars += seg.asian_chars
        self.non_asian_words += seg.non_asian_words


def get_doc_seg(infile, segger):
    """Get a Segment instance with all the segments for <infile> calculated.
    Convenience for getting wordcounts from documents

    @param infile: The input file
    @param segger: The segmenter
    """

    doc_seg = Segment("")

    for seg in segger.get_sentences(infile):
        doc_seg.accumulate(Segment(seg))

    return doc_seg


class DocStats(object):
    """Document statistics"""

    def __init__(self):

        self.match_ranges = {}

        ranges = get_match_ranges()
        for match_range in ranges:
            self.match_ranges[match_range] = Segment("")

        self.repetitions = Segment("")

    def get_range(self, score):
        """Given a score, return the range it comes from
        returns None if it doesn't fall into any of the ranges in
        self.match_ranges.keys()

        @param score: the score for this match
        @return: tuple - dictionary key for this match range,
            or None - if there are no matches
        """

        for match_range in self.match_ranges.keys():
            low, high = match_range
            if low <= score <= high:
                return match_range

        LOGGER.debug(u"docstats [warning] No matching range for score %s" % score)
        return None

    def add_seg(self, seg, match):
        """Add a Segment, with a match score so we know where to file it

        @param seg: the Segment object
        @param match: the match object
        """

        if match == 101:
            self.repetitions.accumulate(seg)
        else:
            match_range = self.get_range(match)
            if match_range:
                self.match_ranges[match_range].accumulate(seg)


@BrokerRequestHandler("DocStats")
def get_doc_stats():
    """broker provider of DocStats instance"""

    return DocStats()


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
