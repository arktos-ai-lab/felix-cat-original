# coding: UTF8
"""
Unit test the tmx module
"""

from nose.tools import raises
from AnalyzeAssist import tmx


@raises(AssertionError)
def test_module():
    assert False


class TestGetTus(object):
    def test_empty(self):
        assert not tmx.get_tus(u"")

    def test_one_empty(self):
        tus = tmx.get_tus(u"<tu ></tu>")
        assert [u'<tu ></tu>'] == tus, tus

    def test_one_spam_ml(self):
        tutext = u"""<tu >
        spam
        </tu>"""
        tus = tmx.get_tus(tutext)
        assert [tutext] == tus, tus

    def test_one_padded(self):
        tutext = u"""<tu >
        spam
        </tu>"""
        padded = u"""<header
        srclang="spam"
        >
        """ + tutext + """</body>"""

        tus = tmx.get_tus(padded)
        assert [tutext] == tus, tus

    def test_two(self):
        one = u"""<tu >
        spam
        </tu>"""
        two = u"""<tu >
        eggs
        </tu>"""
        tutext = u"""<header
        srclang="spam"
        >
        """ + one + two + """
        </body>"""

        tus = tmx.get_tus(tutext)
        assert [one, two] == tus, tus

    def test_spam_eggs(self):
        tutext = u"""<tu>spam</tu><tu>eggs</tu>"""

        tus = tmx.get_tus(tutext)

        assert tus == [u"""<tu>spam</tu>""",
                       u"""<tu>eggs</tu>"""], tus


def test_get_srclang():
    text = u"""<?xml version="1.0" ?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
<header
	 creationtool="TRADOS Translator's Workbench for Windows"
	 creationtoolversion="Edition 6 Build 438"
	 segtype="sentence"
	 o-tmf="TW4Win 2.0 Format"
	 adminlang="EN-US"
	 srclang="JA"
	 datatype="rtf"
	 creationdate="20070203T085432Z"
	 creationid="ONO"
>
<prop type="RTFFontTable">
"""

    srclang = tmx.get_srclang(text)

    assert srclang == u"JA", srclang


class TestUnescapeText(object):
    def test_empty(self):
        text = tmx.unescape_text(u"")
        assert text == u"", text

    def test_apos(self):
        text = tmx.unescape_text(u"&apos;Hi&apos;")
        assert text == u"'Hi'", text

    def test_quote(self):
        text = tmx.unescape_text(u"&quot;Hi&quot;")
        assert text == u'"Hi"', text

    def test_lt_gt(self):
        text = tmx.unescape_text(u"&lt;br&gt;")
        assert text == u'<br>', text

    def test_ampersand(self):
        text = tmx.unescape_text(u"AT&amp;T")
        assert text == u'AT&T', text


class TestGetLang(object):
    @raises(AttributeError)
    def test_empty(self):
        tuv = u""""""
        lang = tmx.get_lang(tuv)

    def test_ja(self):
        tuv = u"""<tuv xml:lang="JA">
<seg>プログラム ⇒ ”Teamｃｅｎｔｅｒ Enterpriｓe（OMF）” ⇒ ”Services Startup”</seg>
</tuv>
"""
        lang = tmx.get_lang(tuv)
        assert lang == u"JA", lang

    def test_en(self):
        tuv = u"""<tuv xml:lang="EN-US">
<seg>Programs -&gt; &quot;Teamｃｅｎｔｅｒ Enterpriｓe（OMF）&quot; -&gt; &quot;Services Startup&quot;</seg>
</tuv>"""

        lang = tmx.get_lang(tuv)
        assert lang == u"EN-US", lang


class TestGetSeg(object):
    @raises(AttributeError)
    def test_empty(self):
        tuv = u""""""
        seg = tmx.get_seg(tuv)

    def test_ja(self):
        tuv = u"""<tuv xml:lang="JA">
<seg>プログラム ⇒ ”Teamｃｅｎｔｅｒ Enterpriｓe（OMF）” ⇒ ”Services Startup”</seg>
</tuv>"""

        seg = tmx.get_seg(tuv)
        print seg.encode("utf8")
        assert seg == u'''プログラム ⇒ ”Teamｃｅｎｔｅｒ Enterpriｓe（OMF）” ⇒ ”Services Startup”''', seg.encode("utf8")

    def test_en(self):
        tuv = u"""<tuv xml:lang="EN-US">
<seg>Programs -&gt; &quot;Teamｃｅｎｔｅｒ Enterpriｓe（OMF）&quot; -&gt; &quot;Services Startup&quot;</seg>
</tuv>"""

        seg = tmx.massage_text(tmx.get_seg(tuv), "EN-US")
        print seg.encode("utf8")
        assert seg == u'''Programs -> "Teamｃｅｎｔｅｒ Enterpriｓe（OMF）" -> "Services Startup"''', seg.encode("utf8")


class TestGetEntry(object):
    def test_numbers(self):
        tu_text = u"""    <tu tuid="1" srclang="JA">
      <tuv xml:lang="JA">
        <seg>"①/②/③/④ ⑥/⑦ ⑧ ⑨"</seg>
      </tuv>
      <tuv xml:lang="EN" creationdate="20070131T075121Z" creationid="Ryan Ginstrom" lastusagedate="20070131T075121Z" changedate="20070131T100058Z" changeid="Ryan Ginstrom" usagecount="0">
        <seg><bpt i="1" x="1">&lt;FONT FACE="Arial"&gt;</bpt>"A/B/C/D F/G H I"<ept i="1">&lt;/FONT&gt;</ept></seg>
      </tuv>
    </tu>"""

        entry = tmx.get_entry(tu_text)

        english = tmx.massage_text(entry["EN"], "EN")
        assert english == u'"A/B/C/D F/G H I"', english
        assert entry["JA"] == u'"①/②/③/④ ⑥/⑦ ⑧ ⑨"', entry

    def test_jfont(self):
        tu_text = u"""    <tu tuid="5" srclang="JA">
      <tuv xml:lang="JA">
        <seg>(*)<bpt i="1" x="1">&lt;font face="ＭＳ ゴシック"&gt;</bpt>：ビデオが<ept i="1">&lt;/font&gt;</ept> MPEG4 <bpt i="1" x="1">&lt;font face="ＭＳ ゴシック"&gt;</bpt>の場合のみ有効。<ept i="1">&lt;/font&gt;</ept></seg>
      </tuv>
      <tuv xml:lang="EN" creationdate="20060831T155455Z" creationid="Ryan Ginstrom" lastusagedate="20070131T100045Z" changedate="20070131T100058Z" changeid="Ryan Ginstrom" usagecount="0">
        <seg>(*) : Only available when video is MPEG4.</seg>
      </tuv>
    </tu>"""

        entry = tmx.get_entry(tu_text)

        japanese = tmx.massage_text(entry["JA"], "JA")
        english = entry["EN"]
        assert english == u'(*) : Only available when video is MPEG4.', english
        assert japanese == u'(*)：ビデオが MPEG4 の場合のみ有効。', japanese.encode("utf8")


    def test_old_style(self):
        tu_text = u"""<tu creationdate="20061003T090957Z" creationid="ACCESS">
<prop type="Att::Status">Approved</prop>
<prop type="Att::File Name">nmcs34_drm_agent_api_spec_1_0_0</prop>
<tuv lang="JA">
<seg>1<ut>{\f3 </ut>回の処理で読み込むサイズは、バッファサイズを上限として、入力データ内に改行コードが含まれる場合は、入力データ内の最後の改行まで読み込まれる（最後の改行以降の未取得データがバウンダリを意味する可能性があるため）。<ut>}</ut></seg>
</tuv>
<tuv lang="EN-US">
<seg>As for the size of data that can be loaded for processing at one time, if linefeed code is included in input data, until the last linefeed in the input data, up to buffer size, can be loaded (since the data that is not obtained following the last linefeed may mean it is a boundary).</seg>
</tuv>
</tu>"""

        entry = tmx.get_entry(tu_text)

        japanese = tmx.massage_text(entry["JA"], "JA")
        english = entry["EN-US"]
        assert english == u'As for the size of data that can be loaded for processing at one time, if linefeed code is included in input data, until the last linefeed in the input data, up to buffer size, can be loaded (since the data that is not obtained following the last linefeed may mean it is a boundary).', english
        assert japanese == u'1回の処理で読み込むサイズは、バッファサイズを上限として、入力データ内に改行コードが含まれる場合は、入力データ内の最後の改行まで読み込まれる（最後の改行以降の未取得データがバウンダリを意味する可能性があるため）。', japanese.encode(
            "utf8")
        
        