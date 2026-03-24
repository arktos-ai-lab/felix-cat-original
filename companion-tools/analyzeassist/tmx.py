# coding: UTF8
"""
TMX parsing module

Can't rely on any of the XML parsing libraries, because Trados in
particular makes such of mess of the XML.

I'd love to use pyparsing here instead of regular expressions, but
pyparsing is just *way* too slow -- like orders of magnitude.

TODO: Support different TMX versions
"""
import logging
from segmenter import textseg
import re
from segmenter.htmlseg import strip_tags

LOGGER = logging.getLogger(__name__)

SEG_MATCHER = re.compile(u"<seg.*?>(.*?)</seg", re.DOTALL | re.M)
LANG_MATCHER = re.compile(u"lang=\"(.*?)\"")
DOUBLE_ESCAPE_MATCHER = re.compile(r"\\'[a-f|\d]{2,2}\\'[a-f|\d]{2,2}", re.I)
ESCAPE_MATCHER = re.compile(r"\\'[a-f|\d]{2,2}", re.I)
TUV_MATCHER = re.compile(u"<tuv.*?</tuv>", re.DOTALL | re.M)
TMX_TAG_STRIPPER = re.compile(u"(<ut.*?</ut>)|(<it.*?</it>)|(<bpt.*?</bpt>)|(<ept.*?</ept>)", re.DOTALL | re.M)


def get_utext(filename):
    """Get the TMX memory as unicode text"""

    return textseg.bytes2unicode(open(filename, "rb").read())


def get_tus(text):
    """Get all the tu tag entries"""

    return re.findall(u"<tu[\s>].*?</tu>", text, re.DOTALL | re.M)


def get_srclang(text):
    """Get the source language of the TMX memory"""

    srcmatch = re.search(u'<header.*?srclang="([\\w-]+)"',
                         text,
                         re.DOTALL | re.M)

    return srcmatch.groups()[0]


def get_seg(tuv):
    """Get the segment for the given tuv"""

    return u''.join(SEG_MATCHER.search(tuv).groups())


def get_lang(tuv):
    """Get the language for the given tuv"""

    return LANG_MATCHER.search(tuv).groups()[0]


def get_entry(tu):
    """Parse an entry from the supplied tu tag"""

    return dict([(get_lang(tuv), get_seg(tuv))
                 for tuv in TUV_MATCHER.findall(tu)])


def get_entries(tus):
    """Parse all the entries from the list of tu tags"""

    entries = []
    for tu in tus:
        try:
            entry = get_entry(tu)
        except AttributeError:
            LOGGER.exception("Failed to parse entry")
        else:
            entries.append(entry)

    return entries


def massage_japanese(text):
    """If the language is Japanese, we need to un-escape
    a bunch of the characters, which are representatives of sjis!

    I couldn't make this stuff up!"""

    try:

        # We might fail to encode as sjis below, if there are
        # characters that won't convert, such as the squiggly.
        # So we give it a try here, to salvage what we can.
        try:
            for escaped_char in DOUBLE_ESCAPE_MATCHER.findall(text):
                chars = escaped_char.split("\\")
                chars = [chr(int(e[1:], 16)) for e in chars if e]
                jchar = ''.join(chars)
                text = text.replace(escaped_char, unicode(jchar, "sjis"))
        except:
            pass

        # Now try the same thing, one char at a time as sjis text
        atext = text.encode("sjis")

        for escaped_char in ESCAPE_MATCHER.findall(atext):
            char = chr(int(escaped_char[2:], 16))
            atext = atext.replace(escaped_char, char)
        text = unicode(atext, "sjis")
    finally:
        return text


def unescape_text(text):
    """Replace escaped XML entities in text

    >>> unescape_text(u"&lt;spam&gt;")
    u'<spam>'

    """

    # XML char entities
    charmap = ((u"&apos;", u"'"),
               (u"&quot;", u'"'),
               (u"&lt;", u"<"),
               (u"&gt;", u">"),
               (u"&amp;", "&"))

    for char, replacement in charmap:
        text = text.replace(char, replacement)

    return text


def massage_text(text, lang):
    """Fix up escaped characters and the like"""

    text = TMX_TAG_STRIPPER.sub(u"", text)
    massaged_text = strip_tags(unescape_text(text))

    # Now get escaped chars
    if lang == "JA":
        return massage_japanese(massaged_text)
    else:
        return massaged_text


def get_sources(filename):
    """Get the source segments for all the entries in the memory"""

    text = get_utext(filename)
    tus = get_tus(text)
    entries = get_entries(tus)
    srclang = get_srclang(text)

    sources = []

    for entry in entries:
        for key in entry:
            if key == srclang and entry.get(key):
                sources.append(massage_text(entry[key], key))

    return sources


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
