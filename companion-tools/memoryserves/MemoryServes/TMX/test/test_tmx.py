#coding: UTF8
from MemoryServes.TMX import tmx

class TestTmxRecord:
    def test_source(self):
        segs = dict(EN="English", JP=u"日本語")
        record = tmx.TmxRecord(segs, srclang="EN")
        assert record.Source == "English", (record.Source, record.segs)
    def test_get_segment_jp(self):
        segs = dict(EN="English", JP=u"日本語")
        record = tmx.TmxRecord(segs, srclang="EN")
        assert record.get_segment("JP") == u"日本語", (record.get_segment("JP"), record.segs)
