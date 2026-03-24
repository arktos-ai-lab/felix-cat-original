from lxml import etree
from lxml import objectify
import tmx
from tmx import XML_LANG
import datetime
import normalizer

def parse_header(header):
    return tmx.TmxHeader(header.get("creationtoolversion"),
                         header.get("datatype"),
                         header.get("segtype"),
                         header.get("adminlang"),
                         header.get("srclang"),
                         header.get("o-tmf"),
                         header.get("creationtool"))

def parse_date(datestr):
    if not datestr:
        return None
    return datetime.datetime.strptime(datestr, "%Y%m%dT%H%M%SZ")

def segtext(seg):
    return normalizer.strip(u"".join(list(seg.itertext())))

def parse_tu(tu):
    segs = dict((tuv.get(XML_LANG), segtext(tuv.seg)) for tuv in tu.tuv)

    return tmx.TmxRecord(segs=segs,
                         tuid=tu.get("tuid"),
                         o_encoding=tu.get("o-encoding"),
                         datatype=tu.get("datatype"),
                         usagecount=tu.get("usagecount"),
                         lastusagedate=parse_date(tu.get("lastusagedate")),
                         creationtool=tu.get("creationtool"),
                         creationtoolversion=tu.get("creationtoolversion"),
                         creationdate=parse_date(tu.get("creationdate")),
                         creationid=tu.get("creationid"),
                         changedate=parse_date(tu.get("changedate")),
                         segtype=tu.get("segtype"),
                         changeid=tu.get("changeid"),
                         o_tmf=tu.get("o-tmf"),
                         srclang=tu.get("srclang"),
                        )

def parse_tmx(fileobj):
    root = objectify.parse(fileobj).getroot()
    return tmx.TmxMemory(parse_header(root.header),
                     [parse_tu(tu) for tu in root.body.tu])
