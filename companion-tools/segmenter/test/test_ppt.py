#coding: UTF8
"""
Unit test the ppt segmenter

"""

import mock
from nose.tools import raises

from segmenter import pptseg
from segmenter.pptseg import Segmenter
from test_excel import FakeShape, FakeTextFrame

@raises(AssertionError)
def test_module():
    """
    Ensure that this module's unit tests are
    getting picked up
    """
    assert False


class FakeRange:

    def __init__(self, value=[]):
        self.Value = value

class FakeExcelSheet:

    def __init__(self, value=[], shapes=[]):
        self.UsedRange = FakeRange(value)
        self.Shapes = shapes

class FakeObject:

    def __init__(self, sheet=None):
        if sheet:
            self.ActiveSheet = sheet
        else:
            self.ActiveSheet = FakeExcelSheet()

class FakeOleFormat:

    def __init__(self, obj=None):
        if obj:
            self.Object = obj
        else:
            self.Object = FakeObject()

    def Activate(self):
        pass

class FakeEmbeddedShape:

    def __init__(self, ole_format=None):
        if ole_format:
            self.OLEFormat = ole_format
        else:
            self.OLEFormat = FakeOleFormat()

class TestExtractExcelText:

    def test_empty(self):

        shape = FakeEmbeddedShape()

        text = [x for x in pptseg.extract_excel_text(shape)]

        assert text == [], text

    def test_range(self):

        sheet = FakeExcelSheet([["spam", "eggs"], ["beans", "bacon"]])
        obj = FakeObject(sheet)
        format = FakeOleFormat(obj)
        shape = FakeEmbeddedShape(format)

        text = [x for x in pptseg.extract_excel_text(shape)]

        assert text == ["spam", "eggs", "beans", "bacon"], text

    def test_text_with_empties(self):

        sheet = FakeExcelSheet([["spam", "eggs", ""], ["beans", "", "bacon"]])
        obj = FakeObject(sheet)
        format = FakeOleFormat(obj)
        shape = FakeEmbeddedShape(format)

        text = [x for x in pptseg.extract_excel_text(shape)]

        assert text == ["spam", "eggs", "beans", "bacon"], text

    def test_shapes(self):
        shapes = [FakeShape(0, FakeTextFrame("spam")), FakeShape(0, FakeTextFrame("eggs"))]

        sheet = FakeExcelSheet(shapes=shapes)
        obj = FakeObject(sheet)
        format = FakeOleFormat(obj)
        shape = FakeEmbeddedShape(format)

        text = [x for x in pptseg.extract_excel_text(shape)]

        assert text == ["spam", "eggs"], text

    def test_text_and_shapes(self):
        used_range = [["spam", "eggs"]]
        shapes = [FakeShape(0, FakeTextFrame("beans")), FakeShape(0, FakeTextFrame("bacon"))]

        sheet = FakeExcelSheet(used_range, shapes=shapes)
        obj = FakeObject(sheet)
        format = FakeOleFormat(obj)
        shape = FakeEmbeddedShape(format)

        text = [x for x in pptseg.extract_excel_text(shape)]

        assert text == ["spam", "eggs", "beans", "bacon"], text

class FakeTextRange:

    def __init__(self, text=""):
        self.Text = text

class FakePptTextFrame:

    def __init__(self, text=""):
        self.TextRange = FakeTextRange(text)

class FakePptShape:

    def __init__(self, text=""):
        self.TextFrame = FakePptTextFrame(text)

class TestGetOrdinaryShapeText:

    def test_empty(self):
        shape = FakePptShape("")

        text = pptseg.get_ordinary_shape_text(shape)

        assert text == "", text

    def test_simple(self):
        shape = FakePptShape("spam")

        text = pptseg.get_ordinary_shape_text(shape)

        assert text == "spam", text

class FakePresentation:
    def __init__(self, slides=[]):
        self.Slides = slides

    def Close(self):
        pass

class FakePresentations:
    def __init__(self, pres=None):
        self.filename = ""
        self.bool1 = False
        self.bool2 = False
        self.bool3 = False

        if pres:
            self.Presentation = pres
        else:
            self.Presentation = FakePresentation()

    def Open(self, filename, bool1, bool2, bool3):
        self.filename = filename
        self.bool1 = bool1
        self.bool2 = bool2
        self.bool3 = bool3

        return self.Presentation

class FakePowerPoint:
    """So we can run our PowerPoint unit tests without waiting
    for PowerPoint to load each time..."""
    def __init__(self, presentations=None):
        self.Visible = 0
        self.Height = 0
        self.Width = 0
        if presentations:
            self.Presentations = presentations
        else:
            self.Presentations = FakePresentations()

    def Quit(self):
        pass

"""Unit tests for pptseg.Segmenter class"""
class TestPowerPointSegmenter:

    def setup(self):
        self.fake_ppt = FakePowerPoint()
        pptseg.get_ppt = self.get_fake_powerpoint
        self.segmenter = Segmenter()

    def get_fake_powerpoint(self):
        return self.fake_ppt

    def teardown(self):
        del self.segmenter

    def testCreation(self):
        pass

    def testStr(self):
        assert u"MS PowerPoint" == str(self.segmenter)

    def test_empty_ppt(self):
        filename = r"c:\foo.ppt"

        chunks = [x for x in self.segmenter.get_sentences(filename)]

        assert chunks == [], chunks
