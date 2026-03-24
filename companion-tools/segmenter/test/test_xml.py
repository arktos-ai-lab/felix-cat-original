#coding: UTF8
"""
Unit test the xml segmenter

"""
import os

from nose.tools import raises

from segmenter.xmlseg import Segmenter

BASEDIR = os.path.dirname(os.path.abspath(__file__))

@raises(AssertionError)
def test_module():
    assert False

@raises(AttributeError)
def test_WrongClassName():
    """Enshrine this programming error I made"""

    import segmenter.xmlseg
    segmenter.xmlseg.Seg()

class TestXml:
    """Unit test the xmlseg.Segmenter class"""

    def testStr(self):
        assert u"XML" == str(Segmenter())

    def test_japanese(self):
        segmenter = Segmenter()

        filename = os.path.join(BASEDIR, "data", "japanese.xml")
        segs = list(segmenter.get_sentences(filename))

        expected = [u"作為", u"無作為", u"作為"]
        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))

    def test_a_text(self):
        segmenter = Segmenter()
        text = """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE memory >
        <memory>
            <records>
                <record>
                    <source><![CDATA[abc]]></source>
                </record>
                <record>
                    <source><![CDATA[def]]></source>
                </record>
            </record>
        </records></memory>"""

        segs = list(segmenter.get_chunks(text))

        expected = ['\n\nDOCTYPE memory \n', "version='1.0' encoding='%SOUP-ENCODING%'", 'abc', 'def']
        assert segs == expected, "Expected %s but actually %s" % (str(expected), str(segs))


    def test_get_chunks(self):
        segmenter = Segmenter()
        text = """
        <xml>
            <nodes>
                <node>foo</node>
                <node>bar</node>
            </nodes>
        </xml>"""

        chunks = list(segmenter.get_chunks(text))
        assert chunks == "foo bar".split(), chunks

    def test_get_chunks_utf16(self):
        segmenter = Segmenter()
        text = u"""<?xml version="1.0" encoding="UTF-16"?>
        <stuff>
            <nodes>
                <node>日本語</node>
                <node>bar</node>
            </nodes>
        </stuff>""".encode('utf-16')

        chunks = list(segmenter.get_chunks(text))
        assert chunks == u"日本語 bar".split(), chunks
