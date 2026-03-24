#!/usr/bin/env python
from __future__ import with_statement

from lxml import etree
import codecs
import datetime
import time
from tmx import XML_LANG
from normalizer import strip

def get_now():
    """
    Get the current datetime
    """

    return datetime.datetime(*time.localtime()[:6])

def parse_time(expr):
    """
    Parse the time into a time object if it's a string.
    If it's already a date, return that.
    Otherwise, return the current datetime.
    """

    if isinstance(expr, basestring):
        try:
            return datetime.datetime(*time.strptime(expr, "%Y/%m/%d %H:%M:%S")[:6]).strftime("%Y%m%dT%H%M%SZ")
        except ValueError:
            return get_now().strftime("%Y%m%dT%H%M%SZ")
    if expr:
        try:
            return expr.strftime("%Y%m%dT%H%M%SZ")
        except AttributeError:
            return datetime.datetime(*expr[:6]).strftime("%Y%m%dT%H%M%SZ")
    return get_now().strftime("%Y%m%dT%H%M%SZ")

def replace(text):
    """
    Replace the forbidden character codes
    """
    if not isinstance(text, unicode):
        text = unicode(text, "utf-8")
    text = strip(text)
    for code in range(1, 9) + range(10, 32):
        char = unichr(code)
        replacement = u"&#%s;" % code
        text = text.replace(char, replacement)
    return text

def write_head(root, info):
    head = etree.SubElement(root, "header")

    attrib = head.attrib
    attrib["creationtoolversion"] = "1.0.0"
    attrib["datatype"] = "html"
    attrib["segtype"] = "sentence"
    attrib["adminlang"] = "EN-US"
    attrib["srclang"] = info["source_language"]
    attrib["o-tmf"] = "Felix"
    attrib["creationtool"] = "Felix"

def set_tu_info(tu, record, info):
    attrib = tu.attrib
    if "id" in record:
        attrib["tuid"] = str(record["id"])
    if "created_by" in record:
        attrib["creationid"] = record["created_by"]
    attrib["srclang"] = info["source_language"]
    if "ref_count" in record:
        attrib["usagecount"] = str(record["ref_count"])
    if "date_created" in record:
        attrib["creationdate"] = parse_time(record["date_created"])
    if "last_modified" in record:
        attrib["changedate"] = parse_time(record["last_modified"])
    if "modified_by" in record:
        attrib["changeid"] = record["modified_by"]

def write_body(root, info, records):
    body = etree.SubElement(root, "body")

    for record in records:
        tu = etree.SubElement(body, "tu")
        set_tu_info(tu, record, info)

        # source
        tuv_source = etree.SubElement(tu, "tuv")
        tuv_source.attrib[XML_LANG] = info["source_language"]
        seg_source = etree.SubElement(tuv_source, "seg")
        seg_source.text = replace(record["source"])

        # trans
        tuv_trans = etree.SubElement(tu, "tuv")
        tuv_trans.attrib[XML_LANG] = info["target_language"]
        seg_trans = etree.SubElement(tuv_trans, "seg")
        seg_trans.text = replace(record["trans"])

def create_tmx(info, records, encoding="utf-8"):
    root = etree.Element("tmx")
    root.attrib["version"] = "1.4"

    # head
    write_head(root, info)

    # body
    write_body(root, info, records)

    return etree.tostring(root,
                          xml_declaration=True,
                          pretty_print=True,
                          encoding=encoding)

def write_tmx(info, records, filename):

    doc = create_tmx(info, records)

    with open(filename, "w") as out:
        out.write(doc)


if __name__ == "__main__":
    run_test()
