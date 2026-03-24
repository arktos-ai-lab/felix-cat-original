"""
Exports records from the specified MemoryServes TM/glossary.
"""

import urllib2
import cPickle
import re
import sys
import datetime
from lxml import etree
from AlignAssist import memory_writer as writer

VERSION = "1.0"

def date2str(date_obj):
    """
    Convert a datetime object into a string for writing to memory.
    """
    if not date_obj:
        return datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    return date_obj.strftime("%Y/%m/%d %H:%M:%S")

def make_head_data(data):
    """
    Make the head data used to write the head XML.
    """
    head = {"creator": data.get("creator", u""),
            "created_on": date2str(data.get("created_on")),
            "creation_tool": "MemoryServesExporter",
            "version": VERSION,
            "count": unicode(data.get("size", 0)),
            "locked": "false"}
    if data.get("memtype") == u"m":
        head["is_memory"] = "true"
    else:
        head["is_memory"] = "false"

    return head

def bool2str(val):
    """
    The true/false values expected by Felix.
    """
    if val:
        return "true"
    return "false"

def massage_rec_data(rec_data):
    """
    Turn it into a format that the XML module can deal with
    """
    data = dict()
    data.update(rec_data)
    data["date_created"] = date2str(data.get("date_created"))
    data["last_modified"] = date2str(data.get("last_modified"))
    if "validated" in data:
        data["validated"] = bool2str(data["validated"])
    if "reliability" in data:
        if data["reliability"]:
            data["reliability"] = unicode(data["reliability"])
        else:
            del data["reliability"]
    if "created_by" in data:
        data["creator"] = data["created_by"]
    if "id" in data:
        data["id"] = unicode(data["id"])
    return data

def get_url_content(url, url_module=urllib2):
    """
    Wraps urllib2.urlopen
    """
    return url_module.urlopen(url).read()

def create_record_xml(data):
    """
    Write the XML for a record.
    """
    lines = [u"  <record>"]
    if "id" in data:
        lines.append(u"    <id>%s</id>" % unicode(data["id"]))
    if "ref_count" in data:
        lines.append(u"    <ref_count>%s</ref_count>" % unicode(data["ref_count"]))


    lines.append(u"    <source><![CDATA[%s]]></source>" % unicode(data["source"]))
    lines.append(u"    <trans><![CDATA[%s]]></trans>" %unicode(data["trans"]))

    if "context" in data and data["context"]:
        lines.append(u"    <context><![CDATA[%s]]></context>" %unicode(data["context"]))
    if "creator" in data:
        lines.append(u"    <creator>%s</creator>" % unicode(data["creator"]))
    if "modified_by" in data:
        lines.append(u"    <modified_by>%s</modified_by>" % unicode(data["modified_by"]))

    lines.append(u"    <date_created>%s</date_created>" % unicode(data["date_created"]))
    lines.append(u"    <last_modified>%s</last_modified>" % unicode(data["last_modified"]))

    if "validated" in data:
        lines.append(u"    <validated>%s</validated>" % unicode(data["validated"]))
    if "reliability" in data and data["reliability"]:
        lines.append(u"    <reliability>%s</reliability>" % unicode(data["reliability"]))

    lines.append(u"  </record>\n")


    text = u"\n".join(lines)
    return text.encode("utf-8")

def export_record(out, raw_data):
    """
    Write a record as XML to output
    """
    rec_data = massage_rec_data(raw_data)
    record_xml = create_record_xml(rec_data)
    out.write(record_xml)

def export_records(record_links, rec_by_id, out, callback):
    """
    Go to the view record page for each of the browse links, and download that record info,
    then write it out as XML.
    """
    for record_link in record_links:
        record_id = re.findall(r'/\d+"', record_link)[0][1:-1]
        rec_url = rec_by_id + record_id
        rec_request = get_url_content(rec_url)
        raw_data = cPickle.loads(rec_request)
        export_record(out, raw_data)
        callback.update()


def build_download_url(page_num, parsed_url):
    """
    Build the URL for the browse TM page that we will scrape.
    """
    url = "/".join([parsed_url.scheme + "/", parsed_url.netloc, "memories", "browse", parsed_url.mem_num, page_num])
    return url


def find_record_links(browse_page):
    """
    Find all record links on the page.
    """
    record_links = re.findall(r'href="/records/edit/\d+/\d+"', browse_page, re.M)
    return record_links


def find_page_links(browse_page):
    """
    Find all page links on the page.
    """
    page_links = re.findall(r'<a href="\d+" title="Go to page \d+">\d+</a>', browse_page, re.M)
    return page_links


def download_pages(parsed_url, page_num, get_record_url, out, callback):
    """
    Download and parse browse page `page_num`.
    Download all other pages linked from this page.
    Keep track of the pages we have already downloaded, so that we don't download a page twice.
    """

    seen_pages = set()
    pages_to_consume = [page_num]

    while pages_to_consume:
        page_num = pages_to_consume.pop(0)
        if page_num not in seen_pages:
            seen_pages.add(page_num)
            url = build_download_url(page_num, parsed_url)
            browse_page = get_url_content(url)
            for page_link in find_page_links(browse_page):
                page_num = re.findall(r'"\d+"', page_link)[0][1:-1]
                pages_to_consume.append(page_num)

            record_links = find_record_links(browse_page)
            export_records(record_links, get_record_url, out, callback)


def write_records(data_source, data, out, callback):
    """
    Writes all the records from the memory.
    Kicks off the download at page 1.
    """
    url = data_source.parse_url()
    download_pages(url, "1", data["rec_by_id"], out, callback)

def write_head_node(info, out):
    """
    Writes the head-node XML.
    """
    head_data = make_head_data(info)
    head = etree.Element("head")
    out.write(etree.tostring(writer.write_head_nodes(head_data, head), pretty_print=True, encoding="utf-8"))

def write_head(data, out):
    """
    Writes the memory head to file-like object `out`
    """
    info = cPickle.loads(get_url_content(data["info"]))
    write_head_node(info, out)
    return info

class ParsedUrl(object):
    """
    Represents a parsed URL, so we don't have to pass around all the bits.
    """
    def __init__(self, scheme, netloc, mem_num):
        self.scheme = scheme
        self.netloc = netloc
        self.mem_num = mem_num

class DataSource(object):
    """
    Wraps a data source. Used to parse the connection URL and get the data from it.
    """
    def __init__(self, connection_url):
        self.connection_url = connection_url
    
    def get_data(self):
        conn_request = get_url_content(self.connection_url)
        return cPickle.loads(conn_request)
    
    def parse_url(self):
        pieces = [x for x in self.connection_url.split('/') if x]
        scheme = pieces[0]
        netloc = pieces[1]
        mem_num = pieces[-1]
        return ParsedUrl(scheme, netloc, mem_num)


def write_memory(data_source, out, callback):
    """
    Writes the memory from `data_source` to file-like object `out'.
    """
    
    data = data_source.get_data()
    out.write("""<?xml version="1.0" encoding="UTF-8"?>
<!-- Created by MemoryServesExporter v %s -->
<memory>\n""" % VERSION)
    info = write_head(data, out)
    callback.initialize(info["size"])
    print >> out, "<records>"
    write_records(data_source, data, out, callback)
    print >> out, """</records>
</memory>"""

def export(connection_url, out, callback):
    """
    Exports the TM from `connection_url` to file-like object `out`.
    """
    data_source = DataSource(connection_url)
    write_memory(data_source, out, callback)

if __name__ == "__main__": # pragma no cover
    class FakeProgress(object):
        def initialize(self, val):
            print >> sys.stderr, "initialize callback", val
        def update(self):
            print >> sys.stderr, "update callback"
    export(sys.argv[-1], sys.stdout, FakeProgress())