#coding: UTF8
"""
Unit test the Excel segmenter

"""

from nose.tools import raises
from segmenter import excelseg
from segmenter.excelseg import Segmenter


@raises(AssertionError)
def test_module():
    assert False

class FakeExcel:
    def __init__(self):
        self.Visible = 0
    def Quit(self):
        pass

def getFakeExcel():
    return FakeExcel()

class FakeRange:
    def __init__(self, val):
        self.Value = val

class FakeCharacters:
    def __init__(self,text=""):
        self.Text = text

class FakeTextFrame:
    def __init__(self,text=""):
        self.Text = text
        self.calls = []
    def Characters(self,start,stop):
        self.calls.append("Characters: %i - %i" % (start,stop))
        return FakeCharacters(self.Text)

class FakeShape:
    def __init__(self, type=0, frame=None, name="fake shape"):
        self.Type = type
        self.Name = name
        if frame:
            self.TextFrame = frame

class FakeObject:
    def __init__(self,caption=""):
        self.Caption = caption

class FakeOleObject:
    def __init__(self,caption=""):
        self.Object = FakeObject(caption)

class FakeSheet:

    def __init__(self, ole_objects={}):
        self.ole_objects = ole_objects
    def OLEObjects(self, name):
        return self.ole_objects[name]

class testExcel:
    def setUp(self):
        excelseg.getExcel = getFakeExcel
        self.segmenter = Segmenter()

    def testCreation(self):
        pass

    def testChunkRange(self):
        myvals = ((0,"spam","85"),
                  ("eggs",5,83))

        self.segmenter.chunking_strategy.analyze_numbers = False
        self.segmenter.chunking_strategy.filterNums = True
        vals = [x for x in self.segmenter.chunkRange(FakeRange(myvals))]

        assert vals == ["spam", "eggs"], vals

    def testStr(self):

        assert str(self.segmenter) == u"MS Excel"

    def test_getShapeChunksEmpty(self):
        sheet = FakeSheet
        sheet.Shapes = []
        assert [] == [x for x in self.segmenter.getShapeChunks(sheet)]

    def test_getShapeChunksLines(self):
        sheet = FakeSheet
        shapes = [FakeShape(9), FakeShape(9)]
        sheet.Shapes = shapes
        assert [] == [x for x in self.segmenter.getShapeChunks(sheet)]

    def test_getShapeChunksTextBoxes(self):
        sheet = FakeSheet
        shapes = [FakeShape(0, FakeTextFrame("spam")), FakeShape(0, FakeTextFrame("eggs"))]
        sheet.Shapes = shapes
        assert ["spam", "eggs"] == [x for x in self.segmenter.getShapeChunks(sheet)]
        assert shapes[0].TextFrame.calls == ["Characters: 1 - 255"]
        assert shapes[1].TextFrame.calls == ["Characters: 1 - 255"]

    def test_getShapeChunksOle(self):
        sheet = FakeSheet(ole_objects = {'fake shape' : FakeOleObject("ole spam, batman")})
        sheet.Shapes = [FakeShape(12, FakeTextFrame("spam"))]

        assert ["ole spam, batman"] == [x for x in self.segmenter.getShapeChunks(sheet)]
