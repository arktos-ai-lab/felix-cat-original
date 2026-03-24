#coding: UTF8

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class TmxMemory(object):
    def __init__(self, header, records):
        self.header = header
        self.records = records

class TmxRecord(object):
    """
    Translation unit - The <tu> element contains the data for a given translation unit.

    Required attributes:
        None.

    Optional attributes:
        tuid, o-encoding, datatype, usagecount, lastusagedate, creationtool,
        creationtoolversion, creationdate, creationid, changedate, segtype,
        changeid, o-tmf, srclang.

    Contents:
        Zero, one or more <note>, or <prop> elements in any order, followed by
        One or more <tuv> elements.
        Logically, a complete translation-memory database will contain at least
        two <tuv> elements in each translation unit.
    """
    def __init__(self,
                 segs,
                 tuid=None,
                 o_encoding=None,
                 datatype=None,
                 usagecount=None,
                 lastusagedate=None,
                 creationtool=None,
                 creationtoolversion=None,
                 creationdate=None,
                 creationid=None,
                 changedate=None,
                 segtype=None,
                 changeid=None,
                 o_tmf=None,
                 srclang=None,
                 ):
        self.segs = segs
        self.tuid = tuid
        self.o_encoding = o_encoding
        self.datatype = datatype
        self.usagecount = usagecount
        self.lastusagedate = lastusagedate
        self.creationtool = creationtool
        self.creationtoolversion = creationtoolversion
        self.creationdate = creationdate
        self.creationid = creationid
        self.changedate = changedate
        self.segtype = segtype
        self.changeid = changeid
        self.o_tmf = o_tmf
        self.srclang = srclang

    @property
    def Source(self):
        return self.get_segment(self.srclang)

    def get_segment(self, lang):
        return self.segs[lang]

class TmxHeader(object):
    def __init__(self,
                 creationtoolversion,
                 datatype,
                 segtype,
                 adminlang,
                 srclang,
                 o_tmf,
                 creationtool):
        self.creationtoolversion = creationtoolversion
        self.datatype = datatype
        self.segtype = segtype
        self.adminlang = adminlang
        self.srclang = srclang
        self.o_tmf = o_tmf
        self.creationtool = creationtool
