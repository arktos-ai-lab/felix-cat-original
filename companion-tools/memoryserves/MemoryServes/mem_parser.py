#coding: UTF8
"""
Parse felix memories

"""
import logging

from lxml import etree
from lxml.html import soupparser


REPLACEMENTS = []
for code in range(1, 9) + range(10, 32):
    char = chr(code)
    replacement = "&#%s;" % code
    REPLACEMENTS.append((char, replacement))


def e2d(element):
    """
    Convert an ElementTree element into a dictionary
    """
    d = {}
    for child in element.getchildren():
        tag = child.tag
        if isinstance(tag, unicode):
            tag = tag.encode("utf-8")
        text = child.text
        if not isinstance(text, unicode):
            if text:
                text = text.decode("utf-8")
            else:
                text = u''
        if tag == "creator":
            tag = "created_by"
        d[tag] = text

    return d


def get_root(xml_fp):
    """
    First tries to parse using the fast lxml parser.
    If lxml chokes on the input, we fall back to
    the slower -- but more forgiving -- ElementSoup
    parser.
    """

    try:
        return etree.parse(xml_fp)
    except etree.XMLSyntaxError, details:
        print "XMLSyntaxError: %s" % repr(details)
        if xml_fp.closed:
            xml_fp = open(xml_fp.name)
        text = xml_fp.read()
        for char, replacement in REPLACEMENTS:
            text = text.replace(char, replacement)

        return soupparser.fromstring(text)


def get_head(root):
    """
    Gets the head element of the XML tree. This has TM metadata.
    """

    return e2d(root.find(".//head"))


def get_records(root):
    """
    Gets the records in the TM, and yields them as dict objects.
    """
    logging.debug("Retrieving records from XML root <record> element")
    for record in root.getiterator(u"record"):
        yield e2d(record)
