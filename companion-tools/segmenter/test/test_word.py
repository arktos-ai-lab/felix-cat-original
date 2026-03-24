#coding: UTF8
"""
Unit test the word segmenter

"""

from nose.tools import raises
from segmenter import wordseg
from segmenter.wordseg import Segmenter

@raises(AssertionError)
def test_module():
    """Make sure this module's tests are getting picked up"""

    assert False

def test_get_word():
    x = wordseg.getWord(lambda x : x)
    assert x == "Word.Application", x

class FakeWord:
    def __init__(self):
        self.Visible = 0
        self.calls = []

    def Quit(self, value=None):
        self.calls.append("Quit")

def getFakeWord(dispatch_func=lambda x : x):
    return FakeWord()

class FakeTextRange:
    def __init__(self, text=""):
        self.Text = text

class FakeTextFrame:
    def __init__(self, textrange=None):
        self.TextRange = textrange
        if self.TextRange:
            self.HasText = True
        else:
            self.HasText = False

class FakeShape:
    pass

class TestWord:
    def setUp(self):
        self.old_get_word = wordseg.getWord
        wordseg.getWord = getFakeWord
        self.segmenter = Segmenter()

    def teardown(self):
        wordseg.getWord = self.old_get_word

    def testCreation(self):
        pass

    def testStr(self):
        assert "MS Word" == str(self.segmenter)

    def testInitWord(self):
        assert not self.segmenter.word

        self.segmenter.initWord()

        assert self.segmenter.word

        assert not self.segmenter.was_visible

    def testGetFrameTextNoFrame(self):
        assert "" == self.segmenter.getFrameText(FakeShape())

    def testGetFrameTextNoText(self):
        frame = FakeTextFrame()
        assert not frame.HasText
        shape = FakeShape()
        shape.TextFrame = frame
        assert "" == self.segmenter.getFrameText(shape)

    def testGetFrameTextEmptyText(self):
        frame = FakeTextFrame(FakeTextRange(""))
        assert frame.HasText
        shape = FakeShape()
        shape.TextFrame = frame
        assert "" == self.segmenter.getFrameText(shape)

    def testGetFrameTextHasText(self):
        frame = FakeTextFrame(FakeTextRange("foo"))
        assert frame.HasText
        shape = FakeShape()
        shape.TextFrame = frame
        assert "foo" == self.segmenter.getFrameText(shape)

    def testDeletionNoWord(self):
        assert not self.segmenter.word
        del self.segmenter

    def testDeletion(self):
        """Make sure that deleting segmenter causes Quit to
        be called on Word interface"""

        calls = []
        self.segmenter.initWord()
        self.segmenter.word.calls = calls
        del self.segmenter
        assert "Quit" in calls, calls
