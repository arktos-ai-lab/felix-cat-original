#coding: UTF8
"""
Unit test the text segmenter
"""

from segmenter import textseg
from segmenter.textseg import Segmenter

class TestBytes2Unicode:
    """Unit tests for bytes2unicode function"""

    def test_ascii(self):
        bytes = "spam"
        text = textseg.bytes2unicode(bytes)
        assert text == u"spam", text

    def test_utf8_bom(self):
        bytes = chr(0xEF) + chr(0xBB) + chr(0xBF) + "spam"
        text = textseg.bytes2unicode(bytes)
        assert text == u"spam", text

    def test_utf8_japanese_bom(self):
        bytes = chr(0xEF) + chr(0xBB) + chr(0xBF) + "日本語"
        text = textseg.bytes2unicode(bytes)
        assert text == u"日本語", text

    def test_sjis_japanese(self):
        bytes = u"日本語".encode("sjis")
        text = textseg.bytes2unicode(bytes)
        assert text == u"日本語", text

    def test_spam_utf16(self):
        bytes = open("/test/spam_utf16.txt").read()
        assert bytes.startswith(chr(0xFF)), bytes
        text = textseg.bytes2unicode(bytes)
        assert text == u"spam", text

    def test_spam_utf16be(self):
        bytes = open("/test/spam_utf16be.txt").read()
        assert bytes.startswith(chr(0xFE)), bytes
        text = textseg.bytes2unicode(bytes)
        assert text == u"spam", text


class TestTextSegmenter:
    """Test the text segmenter"""

    def setup(self):
        self.segmenter = Segmenter()

    def test_creation(self):
        pass

    def testStr(self):

        assert u"Text" == str(self.segmenter)

    def test_a(self):

        filename = r"c:/test/a.txt"

        segs = list(self.segmenter.get_sentences(filename))

        assert segs == ["abc", "def", "abcd", "abc.", "def."]

    def test_a_get_all_text(self):

        filename = r"c:/test/a.txt"

        segs = list(self.segmenter.get_all_text(filename))

        assert segs == [u"abc", u"def", u"abcd", u"abc. def."], segs

    def test_sentences(self):

        filename = r"c:/test/sentences.txt"

        segs = list(self.segmenter.get_sentences(filename))

        assert segs == ["This is a table.",
                "See Dick run.",
                "Run Dick, run!",
                "Janes sees Dick run.",
                "Dick runs and runs."]


    def test_withnums_no_nums(self):

        filename = r"c:/test/withnums.txt"

        self.segmenter.chunking_strategy.analyze_numbers = False
        segs = list(self.segmenter.get_sentences(filename))

        expected = ["Here is a table of numbers.",
                "foo",
                "bar",
                ]
        assert segs == expected, segs

    def test_withnums_yes_nums(self):
        filename = r"c:/test/withnums.txt"

        self.segmenter.chunking_strategy.analyze_numbers = True
        filename = r"c:/test/withnums.txt"

        segs = list(self.segmenter.get_sentences(filename))

        expected = ["Here is a table of numbers.",
                "foo",
                "34",
                "54",
                "16",
                "bar",
                "34",
                "54",
                "16",
                ]
        assert segs == expected, (segs, expected)

    def test_japanese(self):

        filename = r"c:/test/japanese.txt"

        segs = list(self.segmenter.get_sentences(filename))

        assert segs == [u"日本語",
                u"英語",
                u"本日晴天なり。",
                u"なるほど",
                ]

    def test_japaneseutf8(self):

        filename = r"c:/test/japaneseutf8.txt"

        segs = [x for x in self.segmenter.get_sentences(filename)]

        expected = [u"日本語",
                u"英語",
                u"本日晴天なり。",
                u"なるほど",
                ]

        for expected, actual in zip(expected,segs):
            assert expected == actual, "Expected %s but actual %s" % \
                             (expected.encode('utf8'),actual.encode('utf8'))

    def test_japaneseutf16(self):

        filename = r"c:\test\japaneseutf16.txt"

        segs = [x for x in self.segmenter.get_sentences(filename)]

        expected = [u"日本語",
                u"英語",
                u"本日晴天なり。",
                u"なるほど",
                ]

        for expected, actual in zip(expected,segs):
            assert expected == actual, "Expected %s but actual %s" % \
                             (expected.encode('utf8'),actual.encode('utf8'))

    def test_japaneseutf16be(self):

        filename = r"c:\test\japaneseutf16be.txt"

        segs = [x for x in self.segmenter.get_sentences(filename)]

        expected = [u"日本語",
                u"英語",
                u"本日晴天なり。",
                u"なるほど",
                ]

        for expected, actual in zip(expected,segs):
            assert expected == actual, "Expected [%s] but actual [%s]" % \
                             (expected.encode('utf8'),actual.encode('utf-8'))

    def test_washing(self):

        filename = "/test/washing.txt"

        actualSegs = list(self.segmenter.get_sentences(filename))

        expectedSegs = """こちらは株式会社ナミコスです。
トップページへはこちらから <../index.html>
英語ページへはこちらから <#>
------------------------------------------------------------------------
メニュー
* 商品案内 <../ampoule/index.html>
* 工場の案内 <../factory/index.html>
* 会社案内 <../corporate/index.html>
* お問い合わせ <mailto:メールアドレス>
------------------------------------------------------------------------
サブメニュー
* アンプル <../ampoule/index.html>
* シリコーン加工 <../silicone/index.html>
* 洗浄加工 <../washing/index.html>
* 品質保証体制 <../quality/index.html>
* 樹脂容器 <../countainer/index.html>
------------------------------------------------------------------------
洗浄加工
洗浄加工について
従来経口剤用の硝子瓶は、製薬会社にてエアー洗浄を行い使用されるケースが多
かったのですが、市場での要求品質が高まるにつれ、水洗の需要が多くなりました。
これを受け弊社では、お客様の前工程として瓶の洗浄を事業化致しました。
お客
様では、錠剤・カプセル・液剤・粉剤などの薬や健康食品を直接充填され省力化
につながるとご好評を頂いております。
洗浄加工室
洗浄外観検査室
（全数について外観検査を実施）
------------------------------------------------------------------------
製造環境
従来経口剤用の硝子瓶は、製薬会社にてエアー洗浄を行い使用されるケースが多
かったのですが、市場での要求品質が高まるにつれ、水洗の需要が多くなりました。
これを受け弊社では、お客様の前工程として瓶の洗浄を事業化致しました。
お客
様では、錠剤・カプセル・液剤・粉剤などの薬や健康食品を直接充填され省力化
につながるとご好評を頂いております。
------------------------------------------------------------------------
包装形態
シュリンク包装を行い輸送時の紙粉等の異物付着を防止し、洗浄時のクリーン度
を保ったまま納入致します。
エアーシャワー室
シュリンク包装による
クリーンパッケージング
""".splitlines()

        for expected, actual in zip(expectedSegs,actualSegs):
            assert unicode(expected, 'utf8') == actual, "Expected %s but actual %s" % \
                             (expected,actual.encode('utf8'))
