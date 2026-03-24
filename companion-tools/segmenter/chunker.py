#coding: UTF8
"""
Chunking strategy module

Takes a glob of text and chunks it into sentences.

Usage:
chunker = Chunker()
text = open("/python25/readme.txt").read()
for chunk in chunker.get_sentences(text):
    print chunk

Known issues:
   * Can't handle abbreviations that don't end a sentence, such as
   [I put catsup, mustard, etc. on my wiener]
   [This sentence won't parse correctly (i.e. it will be split on the 'e period').]

   Possible (partial) solution: check next work for capitalization (but will
   still miss proper nouns (e.g. Henry))

   * Won't properly segment sentences with hard line breaks in them.
   (set seg_control_chars to False to not segment on line breaks and other
   control characters)

"""
import logging
import os
import string
import shutil

import wchartype

from segmenter.AppUtils import module_path, get_local_app_data_folder

NUM_CHARS = set(string.digits + u'.-,')
OK_ENDINGS = tuple("Mr. Ms. Mrs. Dr.".split())
LOGGER = logging.getLogger(__name__)

def has_ok_ending(text):
    """Some period-ended words can't end a sentence

    >>> has_ok_ending("Go see Mrs.")
    True
    >>> has_ok_ending("Eat spam.")
    False
    """

    return text.endswith(OK_ENDINGS)

is_asian = wchartype.is_asian


def is_num(seg):
    """Is seg a number?

    >>> is_num("spam")
    False
    >>> is_num("1 spam")
    False
    >>> is_num("12")
    True
    >>> is_num(u"40.1")
    True
    >>> is_num(u"100,000")
    True
    >>> is_num(u"100%")
    True
    """

    if not isinstance(seg, basestring):
        seg = unicode(seg)

    seg = seg.strip()
    if seg.endswith(u"%"):
        seg = seg[:-1]
    seg = u''.join([x for x in seg if x != ','])
    try:
        float(seg)
        LOGGER.debug(u'%s is a number', seg)
        return True
    except ValueError:
        return False

# the unichr thingies are dot dot dot in single-byte and Unicode versions
DEFAULT_STOPS = u".!?。．！？" + unichr(0x133) + unichr(0x8230)


class Chunker(object):
    """Chunks lines into segments"""

    def __init__(self,
                 stop_chars=DEFAULT_STOPS,
                 seg_control_chars=True,
                 analyze_numbers=True):
        """
        @param stop_chars: Stop characters (periods, question marks, etc.)
        @param seg_control_chars: Should control characters be end-of-segment markers?
        @param analyze_numbers: Whether numbers should be emitted as text chunks
        """

        # Character codes for the various ways to end a sentence...
        self.sentence_end_markers = set(stop_chars)
        """e.g. periods, exclamation marks, ..."""

        self.analyze_numbers = analyze_numbers
        """Filter out nums?"""

        self.seg_on_control_chars = seg_control_chars
        """Segment on control characters?"""

        self.rightquotes = {'"', "'", unichr(0x2019), unichr(0x201D)}
        """Both dumb and plain single and double quotes"""

        self.low_control_chars = set([unichr(x) for x in range(0x01, 0x09)])
        """Control characters below tab"""

        self.control_chars = self.low_control_chars
        """All control characters"""

        self.control_chars.update([unichr(x) for x in range(0x09, 0x20)])
        """Tabs, Bell (table cell sep in Word), etc. Things that denote
        a segment boundary"""

        self.stop_chars = set(self.sentence_end_markers)

        if self.seg_on_control_chars:
            self.stop_chars.update(self.control_chars)

    def passes_filter(self, seg):
        """Does the seg pass the filter?

        @param seg: a segment of text

        >>> chunker = Chunker()
        >>> chunker.passes_filter("")
        False
        >>> chunker.passes_filter("spam")
        True
        >>> chunker.analyze_numbers = False
        >>> chunker.passes_filter("45")
        False
        >>> chunker.analyze_numbers = True
        >>> chunker.passes_filter("45")
        True
        """

        if not seg:
            return False

        if self.analyze_numbers:
            LOGGER.debug(u'passes filter because analyze_numbers is True')
            return True

        return not is_num(seg)

    def get_sentences(self, text):
        """'chunkify' C{text} into segments

        >>> chunker = Chunker()
        >>> list(chunker.get_sentences("I luv spam. I hates hobbitses"))
        ['I luv spam.', 'I hates hobbitses']
        >>> # text = u'書く。晴天なり'
        >>> text = u'\u66f8\u304f\u3002\u6674\u5929\u306a\u308a'
        >>> list(chunker.get_sentences(text))
        [u'\u66f8\u304f\u3002', u'\u6674\u5929\u306a\u308a']
        """

        LOGGER.debug(u'get_sentences; analyze_numbers: %r', self.analyze_numbers)

        sentence = []

        control_chars = self.seg_on_control_chars
        low_control_chars = self.low_control_chars
        sentence_end_markers = self.sentence_end_markers
        stop_chars = self.stop_chars

        pos = 0
        while pos < len(text):

            char = text[pos]
            # We need to add the character here, because we check
            # the sentence ending "Mr...." down below
            if not (control_chars and char in low_control_chars):
                sentence.append(char)

            should_yield = False

            # ('.', '!', '?', '。', ...)
            if char in sentence_end_markers:
                pos, should_yield = self.check_end_marker(pos, sentence, text)

            # tabs, control characters, etc.
            # We assume our input is already split into lines,
            # or that multiline segments are OK (like in HTML).
            elif char in stop_chars:
                should_yield = True

            # Yield the segment if necessary
            if should_yield:
                ys = ''.join(sentence).strip()
                sentence = []
                if self.passes_filter(ys):
                    LOGGER.debug(u'%s passes the filter', ys)
                    yield ys

            pos += 1

        # Final accumulated sentence. Yield if necessary
        ys = ''.join(sentence).strip()
        if self.passes_filter(ys):
            LOGGER.debug(u'%s passes the filter', ys)
            yield ys

    def check_end_marker(self, pos, sentence, text):
        """
        We have found an end marker. Should we yield a sentence?

        @param pos: The current position in the text
        @param sentence: The current sentence we are building
        @param text: The text we are segmenting

        @returns: pos, should_yield
        """

        char = text[pos]
        # ('。', '！', ...)
        if is_asian(char):
            return pos, True # And don't set last_was_period (no space to eat)

        try:

            next_char = text[pos+1]
            #Special case for right quotes: "I heart spam."
            if next_char in self.rightquotes:
                sentence.append(next_char)
                return pos+1, True

            # Special case for periods
            if u'.' in self.sentence_end_markers and char == u'.':

                # Number
                if next_char in string.digits:
                    return pos, False

                # ('Mr.', 'Mrs.', ...)
                if has_ok_ending(u''.join(sentence)):
                    return pos, False

                if next_char.isspace():
                    return pos, True

                # in abbreviation!
                pos += 1
                while not text[pos].isspace():
                    sentence.append(text[pos])
                    pos += 1

                if text[pos-1] == u'.':
                    while text[pos].isspace():
                        sentence.append(text[pos])
                        pos += 1
                    if text[pos].isupper():
                        should_yield = True
                    else:
                        should_yield = False
                    # Un-eat the letter now
                    pos -= 1
                    return pos, should_yield

            elif next_char.isspace():
                return pos, True

        except IndexError: # End of string
            pass

        return pos, True


def seg_lines2rules(lines):
    """Convert lines from segrules file into rules

    >>> lines = "spam=eggs", "alive=false", "parrot=true"
    >>> seg_lines2rules(lines)
    {'parrot': True, 'alive': False, 'spam': u'eggs'}

    """

    rules = {}

    for line in lines:
        key, val = [x.strip() for x in line.split("=")]
        if val.lower() == 'true':
            val = True
        elif val.lower() == 'false':
            val = False
        else:
            val = unicode(val,'utf8')
        rules[key] = val

    return rules


def get_segmentation_rules():
    """Get the segmentation rules from the configuration file
    segrules.txt

    >>> rules = get_segmentation_rules()
    >>> '.' in rules['StopChars']
    True
    >>> 'a' in rules['StopChars']
    False
    """

    try:
        filename = os.path.join(get_local_app_data_folder(), "segrules.txt")
        if not os.path.exists(filename):
            modfile = os.path.join(module_path(), "segrules.txt")
            if os.path.exists(modfile):
                shutil.copy(modfile, filename)

        lines = open(filename,"r")

        return seg_lines2rules(lines)
    except IOError:
        chunk = Chunker()
        return dict(StopChars=chunk.stop_chars,
                    SegControlChars=chunk.seg_on_control_chars,
                    AnalyzeNumbers=chunk.analyze_numbers)


def get_chunker(analyze_numbers=True):
    """Retrieve the chunking strategy, configured for our needs

    >>> rules = get_segmentation_rules()
    >>> chunker = get_chunker()
    >>> chunker.sentence_end_markers == set(rules['StopChars'])
    True
    >>> chunker.analyze_numbers
    True
    >>> chunker.seg_on_control_chars == rules['SegControlChars']
    True
    """

    try:
        rules = get_segmentation_rules()

        stop_chars = rules["StopChars"]
        seg_control_chars = rules["SegControlChars"]

        return Chunker(stop_chars=stop_chars,
                       analyze_numbers=analyze_numbers,
                       seg_control_chars=seg_control_chars)
    except IOError:
        return Chunker()


