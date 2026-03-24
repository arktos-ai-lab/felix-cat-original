#coding: UTF8
"""
Unit test the rtf segmenter

"""

from nose.tools import raises
from segmenter import rtfseg
from segmenter.rtfseg import Segmenter

@raises(AssertionError)
def test_module():
    assert False

def test_isEscape():
    assert rtfseg.isEscapedChar("'01")
    assert rtfseg.isEscapedChar("'1a")
    assert rtfseg.isEscapedChar("'a1")
    assert rtfseg.isEscapedChar("'a1 ")
    assert rtfseg.isEscapedChar("'a1\\")
    assert rtfseg.isEscapedChar("'A1")

    assert not rtfseg.isEscapedChar("01")
    assert not rtfseg.isEscapedChar("'1 ")
    assert not rtfseg.isEscapedChar("'a13")


class testRtf:
    def setup(self):
        self.segmenter = Segmenter()

    def testCreation(self):
        pass

    def testStr(self):

        assert u"RTF" == str(self.segmenter)

    def test_b(self):

        filename = "/test/b.rtf"

        segs = [x for x in self.segmenter.get_sentences(filename)]

        for seg in [u'abc', u'def', u'foo', u'foo']:
            assert seg in segs, segs

    def test_get_sentences_from_text(self):
        text = r""" {\rtf1\ansi\deff0

  {\fonttbl
  {\f0 Times New Roman;}
  }

  \deflang1033\widowctrl

  \page\lang1033\fs32
  {\pard
  abc. def.
  \par}
  }"""
        segs = [x for x in self.segmenter.get_sentences_from_text(text)]

        for seg in [u'abc.', u'def.']:
            assert seg in segs, segs
