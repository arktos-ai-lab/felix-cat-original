#coding: UTF8
"""
CharSegment class
"""

import string
import wchartype


class CharSegment(object):
    """Accumulates character statistics"""

    def __init__(self, text=None):
        self.asian = 0
        self.alpha = 0
        self.digits = 0
        self.punct = 0
        self.spaces = 0
        self.others = 0

        if text:
            self.accumulate(text)

    def accumulate(self, chunk):
        """Add the stats from <seg> to this one.
        Use this to keep a count for the entire document;
        use another for the whole batch of documents

        @param seg: The segment to accumulate

        >>> seg = CharSegment()
        >>> seg.accumulate(u"abc 123")
        >>> seg.asian
        0
        >>> seg.alpha
        3
        >>> seg.digits
        3
        >>> seg.spaces
        1
        >>> seg = CharSegment(u'\u65e5\u672c\u8a9e')
        >>> seg.asian
        3
        >>> seg.alpha
        0
        >>> seg.digits
        0
        >>> seg.punct
        0

        # final symbol is Omega
        >>> seg = CharSegment(u"!.?\u03a9")
        >>> seg.asian
        0
        >>> seg.alpha
        1
        >>> seg.digits
        0
        >>> seg.punct
        3
        >>> seg.spaces
        0
        >>> seg.others
        0

        # square geometric character
        >>> seg = CharSegment(u"\u25A0")
        >>> seg.others
        1

        # accumulate other segments, too
        >>> seg = CharSegment()
        >>> seg.accumulate(CharSegment(u"abc 123"))
        >>> seg.asian
        0
        >>> seg.alpha
        3
        >>> seg.digits
        3
        >>> seg.spaces
        1

        """

        if isinstance(chunk, basestring):
            for char in chunk:
                if wchartype.is_asian(char):
                    self.asian += 1
                elif char.isalpha():
                    self.alpha += 1
                elif char.isdigit():
                    self.digits += 1
                elif char in string.punctuation:
                    self.punct += 1
                elif char.isspace():
                    self.spaces += 1
                else:
                    self.others += 1
        elif chunk:
            self.asian += chunk.asian
            self.alpha += chunk.alpha
            self.digits += chunk.digits
            self.punct += chunk.punct
            self.spaces += chunk.spaces
            self.others += chunk.others

