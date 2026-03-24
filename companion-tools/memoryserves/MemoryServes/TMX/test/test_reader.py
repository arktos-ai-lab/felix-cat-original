#coding: UTF8

from MemoryServes.TMX import reader
from MemoryServes.TMX import tmx
from cStringIO import StringIO
import datetime
from lxml import objectify


class TestParseTmxHeader:
    def setup(self):
        text = """﻿<?xml version="1.0" ?>
    <tmx version="1.4">
      <header creationtoolversion="1.0.0" datatype="html" segtype="sentence" adminlang="EN-US" srclang="JP" o-tmf="Felix" creationtool="Felix"/>
      <body>
        <tu tuid="1" creationid="Ryan" srclang="JP" usagecount="5" changedate="20091226T173430Z" changeid="鈴木">
          <tuv xml:lang="JP">
            <seg>aa&lt;&gt;aa</seg>
          </tuv>
          <tuv xml:lang="EN-US">
            <seg>bbb</seg>
          </tuv>
        </tu>
        <tu tuid="2" creationid="Ryan" srclang="JP" creationdate="20091226T173430Z">
          <tuv xml:lang="JP">
            <seg>ccc	&amp;#10;</seg>
          </tuv>
          <tuv xml:lang="EN-US">
            <seg>ddd</seg>
          </tuv>
        </tu>
        <tu tuid="3" creationid="Ryan" srclang="JP" changedate="20091226T173430Z" changeid="George">
          <tuv xml:lang="JP">
            <seg>日本語</seg>
          </tuv>
          <tuv xml:lang="EN-US">
            <seg>英語</seg>
          </tuv>
        </tu>
      </body>
    </tmx>"""

        data = StringIO(text)

        self.header = reader.parse_tmx(data).header
    def test_creationtoolversion(self):
        assert self.header.creationtoolversion == "1.0.0", self.header.creationtoolversion
    def test_datatype(self):
        assert self.header.datatype == "html", self.header.datatype
    def test_segtype(self):
        assert self.header.segtype == "sentence", self.header.segtype
    def test_adminlang(self):
        assert self.header.adminlang == "EN-US", self.header.adminlang
    def test_srclang(self):
        assert self.header.srclang == "JP", self.header.srclang
    def test_o_tmf(self):
        assert self.header.o_tmf == "Felix", self.header.o_tmf
    def test_creationtool(self):
        assert self.header.creationtool == "Felix", self.header.creationtool

class TestParseTmxRecords:
    def setup(self):
        text = """﻿<?xml version="1.0" ?>
    <tmx version="1.4">
      <header creationtoolversion="1.0.0" datatype="html" segtype="sentence" adminlang="EN-US" srclang="JP" o-tmf="Felix" creationtool="Felix"/>
      <body>
        <tu tuid="1" creationid="Ryan" srclang="JP" usagecount="5" changedate="20091226T173430Z" changeid="鈴木">
          <tuv xml:lang="JP">
            <seg>aa&lt;&gt;aa</seg>
          </tuv>
          <tuv xml:lang="EN-US">
            <seg>bbb</seg>
          </tuv>
        </tu>
        <tu tuid="2" creationid="Ryan" srclang="JP" creationdate="20091226T173430Z">
          <tuv xml:lang="JP">
            <seg>ccc	&amp;#10;</seg>
          </tuv>
          <tuv xml:lang="EN-US">
            <seg>ddd</seg>
          </tuv>
        </tu>
        <tu tuid="3"
            creationid="Ryan"
            srclang="JP"
            changedate="20091226T173430Z"
            changeid="George"
            lastusagedate="20001122T112233Z">
          <tuv xml:lang="JP">
            <seg>日本語</seg>
          </tuv>
          <tuv xml:lang="EN-US">
            <seg>英語</seg>
          </tuv>
        </tu>
      </body>
    </tmx>"""

        data = StringIO(text)

        self.records = reader.parse_tmx(data).records
    def test_num_tus(self):
        assert len(self.records) == 3, self.records
    def test_num_segs(self):
        for record in self.records:
            assert len(record.segs) == 2, (record.segs, len(record.segs))

    # attributes
    def test_attr_0(self):
        """
        <tu tuid="1" creationid="Ryan" srclang="JP" usagecount="5" changedate="20091226T173430Z" changeid="鈴木">
        """
        rec = self.records[0]
        assert rec.tuid == "1", rec.tuid
        assert rec.creationid == "Ryan", rec.creationid
        assert rec.srclang == "JP", rec.srclang
        assert rec.usagecount == "5", rec.usagecount
        assert rec.changedate == datetime.datetime(2009, 12, 26, 17, 34, 30), rec.changedate
        assert rec.changeid == u"鈴木", rec.changeid

    def test_attr_1_non_dates(self):
        """
        <tu tuid="3"
            creationid="Ryan"
            srclang="JP"
            changedate="20091226T173430Z"
            changeid="George"
            lastusagedate="20001122T112233Z">
        """
        rec = self.records[1]
        assert rec.tuid == "2", rec.tuid
        assert rec.creationid == "Ryan", rec.creationid
        assert rec.srclang == "JP", rec.srclang
        assert rec.changeid is None, rec.changeid
        assert rec.usagecount is None, rec.usagecount

    def test_attr_1(self):
        """
        <tu tuid="3"
            creationid="Ryan"
            srclang="JP"
            changedate="20091226T173430Z"
            changeid="George"
            lastusagedate="20001122T112233Z">
        """
        rec = self.records[1]
        assert rec.creationdate == datetime.datetime(2009, 12, 26, 17, 34, 30), rec.creationdate
        assert rec.changedate is None, rec.changedate
        assert rec.lastusagedate is None, rec.lastusagedate

    def test_attr_2_non_dates(self):
        """
        <tu tuid="3" creationid="Ryan" srclang="JP" changedate="20091226T173430Z" changeid="George">
        """
        rec = self.records[2]
        assert rec.tuid == "3", rec.tuid
        assert rec.creationid == "Ryan", rec.creationid
        assert rec.srclang == "JP", rec.srclang
        assert rec.changeid == "George", rec.changeid
        assert rec.usagecount is None, rec.usagecount

    def test_attr_2_dates(self):
        """
        <tu tuid="3" creationid="Ryan" srclang="JP" changedate="20091226T173430Z" changeid="George">
        """
        rec = self.records[2]
        assert rec.changedate == datetime.datetime(2009, 12, 26, 17, 34, 30), rec.changedate
        assert rec.lastusagedate == datetime.datetime(2000, 11, 22, 11, 22, 33), rec.changedate
        assert rec.creationdate is None, rec.creationdate

    # segs
    def test_segs_0(self):
        rec = self.records[0]
        assert rec.segs["JP"] == u"aa<>aa", rec.segs
        assert rec.segs["EN-US"] == u"bbb", rec.segs
    def test_segs_1(self):
        rec = self.records[1]
        assert rec.segs["JP"] == u"ccc\t\n", rec.segs
        assert rec.segs["EN-US"] == u"ddd", rec.segs
    def test_segs_2(self):
        rec = self.records[2]
        assert rec.segs["JP"] == u"日本語", rec.segs
        assert rec.segs["EN-US"] == u"英語", rec.segs

def test_parse_tu_empty_attrs():
    """
    No attributes are required for tu tag
    """

    tu = objectify.fromstring("<tu><tuv><seg /></tuv></tu>")
    rec = reader.parse_tu(tu)

    assert len(rec.segs) == 1, (rec.segs, len(rec.segs))
    assert rec.tuid is None, rec.tuid
    assert rec.creationid is None, rec.creationid
    assert rec.srclang is None, rec.srclang
    assert rec.changeid is None, rec.changeid
    assert rec.usagecount is None, rec.usagecount
    assert rec.creationdate is None, rec.creationdate
    assert rec.changedate is None, rec.changedate
    assert rec.lastusagedate is None, rec.lastusagedate

def test_segtext_plain():
    seg = objectify.fromstring("""<seg>Digitally Sign a Macro Project in Microsoft Word 2000</seg>""")
    text = reader.segtext(seg)
    assert text == "Digitally Sign a Macro Project in Microsoft Word 2000", text

def test_segtext_tags():
    seg = objectify.fromstring("""<seg><it pos="begin" x="1">&lt;1&gt;</it>Digitally Sign a Macro Project in Microsoft Word 2000</seg>""")
    text = reader.segtext(seg)
    assert text == "Digitally Sign a Macro Project in Microsoft Word 2000", text
