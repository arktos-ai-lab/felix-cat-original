#coding: UTF8
from MemoryServes.TMX import writer
from lxml import objectify

class TestCreateTmx:
    def setup(self):

        info = dict(source_language="JP",
                    target_language="EN-US")
        records = [dict(source=u"aa<>aa",
                        trans=u"<b>bbb</b>",
                        created_by="Ryan",
                        ref_count=5,
                        modified_by=u"鈴木",
                        last_modified=writer.get_now(),
                        id=1),
                   dict(source=u"ccc\t\n",
                        trans=u"ddd",
                        created_by="Ryan",
                        date_created=writer.get_now(),
                        id=2),
                   dict(source=u"日本語",
                        trans=u"英語",
                        created_by="Ryan",
                        last_modified=writer.get_now(),
                        modified_by="George",
                        id=3)]
        self.doc = writer.create_tmx(info, records)
        self.mem = objectify.fromstring(self.doc)

    def test_xml_declaration(self):
        assert "<?xml version='1.0' encoding='utf-8'?>" in self.doc, self.doc
    def test_nihongo_doc(self):
        assert "<seg>日本語</seg>" in self.doc, self.doc
    def test_eigo_doc(self):
        assert "<seg>英語</seg>" in self.doc, self.doc
    def test_tu_doc(self):
        assert '<tu tuid="1" creationid="Ryan" srclang="JP" usagecount="5" ' in self.doc, self.doc
    def test_entities_doc(self):
        assert '&amp;#10;</seg>' in self.doc, self.doc

    def test_num_tus(self):
        assert len(self.mem.body.tu) == 3, self.mem.body.tu

    def test_tu_0_creationid(self):
        tu = self.mem.body.tu[0]
        assert tu.attrib["creationid"] == u"Ryan", tu
    def test_tu_0_changeid(self):
        tu = self.mem.body.tu[0]
        assert tu.attrib["changeid"] == u"鈴木", tu
    def test_tu_0_tuvs(self):
        tu = self.mem.body.tu[0]
        assert len(tu.tuv) == 2, tu.tuv
    def test_tu_0_tuv_source(self):
        tuv = self.mem.body.tu[0].tuv[0]
        assert tuv.seg.text == u"aa<>aa", tuv.seg.text
    def test_tu_0_tuv_source_escaped(self):
        tuv = self.mem.body.tu[0].tuv[0]
        assert "aa&lt;&gt;aa" in self.doc, self.doc
    def test_tu_0_tuv_trans(self):
        tuv = self.mem.body.tu[0].tuv[1]
        assert tuv.seg.text == u"bbb", tuv.seg.text
