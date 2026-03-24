#coding: UTF8
"""
Unit test the segmenter package

"""

import cStringIO

from nose.tools import raises
import segmenter


@raises(AssertionError)
def test_module():
    assert False

def test_getExtensionsFileName():
    filename = segmenter.getExtensionsFileName()
    assert filename == r"D:\Users\Ryan\AppData\Local\AnalyzeAssist\extensions.txt", filename

def test_writeSegClassLine():
    io = cStringIO.StringIO()

    segmenter.writeSegClassLine(io, "WordFiles", "*.exe")

    val = io.getvalue()
    assert val == "WordFiles = *.exe\n", val

def test_writeSegClassLineHtml():
    io = cStringIO.StringIO()

    segmenter.writeSegClassLine(io, "HTML", "*.htm;*html")

    val = io.getvalue()
    assert val == "HTML = *.htm;*html\n", val

def test_writeSegClassLines():

    vals = { "MS Word" : "*.doc", "Text" : "*.txt", "HTML" : "*.html;*.htm" }
    io = cStringIO.StringIO()

    segmenter.writeSegClassLines(io, vals)

    val = io.getvalue()

    lines = val.splitlines()
    assert "WordFiles = *.doc" in lines, lines
    assert "TextFiles = *.txt" in lines, lines
    assert "HtmlFiles = *.html;*.htm" in lines, lines

def test_parseExtensionDefLine():

    key, vals = segmenter.parseExtensionDefLine("WordFiles = *.exe\n")
    assert (key, vals) == ("WordFiles", "*.exe"), (key, vals)

def test_SegmenterClassNames():
    names = segmenter.getSegClassNames()

    assert str(segmenter.wordseg.Segmenter()) == u"MS Word"
    word = names[u"MS Word"]
    word_segger = segmenter.wordseg.Segmenter
    assert type(word) == type(word_segger), (word, word_segger)
    assert type(names[u"Text"]) == type(segmenter.textseg.Segmenter), names[u"Text"]
    assert type(names[u"MS PowerPoint"]) == type(segmenter.pptseg.Segmenter), names[u"MS PowerPoint"]
    assert type(names[u"HTML"]) == type(segmenter.htmlseg.Segmenter), names[u"HTML"]
    assert type(names[u"RTF"]) == type(segmenter.rtfseg.Segmenter), names[u"RTF"]
    assert type(names[u"MS Excel"]) == type(segmenter.excelseg.Segmenter), names[u"MS Excel"]
    assert type(names[u"XML"]) == type(segmenter.xmlseg.Segmenter), names[u"XML"]

def test_getNamesAndExtensions():
    names = segmenter.getNamesAndExtensions()

    assert names["WordFiles"] == "*.doc;*.rtf;*.docx", names["WordFiles"]
    assert names["TextFiles"] == "*.txt", names["TextFiles"]
    assert names["PptFiles"] == "*.ppt;*.pptx", names["PptFiles"]
    assert names["HtmlFiles"] == "*.html;*.htm;*.shtml;*.mht;*.php", names["HtmlFiles"]
    assert names["ExcelFiles"] == "*.xls;*.csv;*.xlsx"
    assert names["XmlFiles"] == "*.xml;*.ftm;*.fgloss"


def test_getNames():
    names =  segmenter.get_segmenter_class_names()
    assert len(names.keys()) == 8, names.keys()

    print names
    assert str(names["OpenOfficeFiles"]()) == str(segmenter.openofficeseg.Segmenter())
    assert str(names["WordFiles"]()) == str(segmenter.wordseg.Segmenter())
    assert str(names["TextFiles"]()) == str(segmenter.textseg.Segmenter())
    assert str(names["PptFiles"]()) == str(segmenter.pptseg.Segmenter())
    assert str(names["HtmlFiles"]()) == str(segmenter.htmlseg.Segmenter())
    assert str(names["RtfFiles"]()) == str( segmenter.rtfseg.Segmenter())
    assert str(names["ExcelFiles"]()) == str(segmenter.excelseg.Segmenter())
    assert str(names["XmlFiles"]()) == str(segmenter.xmlseg.Segmenter())


def test_getFileExtension():
    """Make sure we get the right file extensions"""

    assert "*.txt" == segmenter.getFileExtension("foo.txt")
    assert "*.txt" == segmenter.getFileExtension("FOO.TXT")

    assert "*.txt" == segmenter.getFileExtension("c:\\foo.txt")
    assert "*.txt" == segmenter.getFileExtension("c:\\FOO.TXT")

    assert "*.html" == segmenter.getFileExtension("foo.html")
    assert "*.html" == segmenter.getFileExtension("foo.bar.html")

    assert "*.html" == segmenter.getFileExtension("c:\\foo.html")
    assert "*.html" == segmenter.getFileExtension("c:\\foo.bar.html")

    assert "" == segmenter.getFileExtension("foo")
    assert "" == segmenter.getFileExtension("c:\\foo")
    assert "" == segmenter.getFileExtension("c:\\foo\\foo")
    assert "" == segmenter.getFileExtension("c:\\foo.bar\\foo")


@raises(KeyError)
def test_getExtensionsBogus():
    extensions = segmenter.getMapping()

    # Excel
    assert extensions["*.excel"] == segmenter.excelseg.Segmenter


def test_getExtensions():

    extensions = segmenter.getMapping()

    assert "foo" not in extensions.keys()

    # Word
    assert str(extensions["*.doc"]()) == str(segmenter.wordseg.Segmenter())
    assert str(extensions["*.txt"]()) != str(segmenter.wordseg.Segmenter())

    # Text
    assert str(extensions["*.txt"]()) == str(segmenter.textseg.Segmenter())
    assert str(extensions["*.doc"]()) != str(segmenter.textseg.Segmenter())

    # PowerPoint
    assert str(extensions["*.ppt"]()) == str(segmenter.pptseg.Segmenter())

    # Html
    assert str(extensions["*.html"]()) == str(segmenter.htmlseg.Segmenter())
    assert str(extensions["*.htm"]()) == str(segmenter.htmlseg.Segmenter())
    assert str(extensions["*.shtml"]()) == str(segmenter.htmlseg.Segmenter())

    # Rtf
    sws = segmenter.wordseg.Segmenter
    assert str(extensions["*.rtf"]()) == str(sws()), extensions["*.rtf"]

    # Excel
    assert str(extensions["*.xls"]()) == str( segmenter.excelseg.Segmenter())

    # Xml
    assert str(extensions["*.xml"]()) == str(segmenter.xmlseg.Segmenter())

class TestGetSegmenterClass:
    def test_txt(self):
        klass = segmenter.getSegmenterClass("/test/a.txt")
        assert klass == segmenter.textseg.Segmenter, klass
    def test_none(self):
        klass = segmenter.getSegmenterClass("/test/a")
        assert klass == segmenter.textseg.Segmenter, klass
    def test_nonexistent(self):
        klass = segmenter.getSegmenterClass("/test/a.snarfle")
        assert klass == segmenter.textseg.Segmenter, klass

    def test_doc(self):
        klass = segmenter.getSegmenterClass("/test/a.doc")
        assert klass == segmenter.wordseg.Segmenter, klass
    def test_docx(self):
        klass = segmenter.getSegmenterClass("/test/a.docx")
        assert klass == segmenter.wordseg.Segmenter, klass
    def test_rtf(self):
        klass = segmenter.getSegmenterClass("/test/a.rtf")
        assert klass == segmenter.wordseg.Segmenter, klass

    def test_xls(self):
        klass = segmenter.getSegmenterClass("/test/a.xls")
        assert klass == segmenter.excelseg.Segmenter, klass
    def test_xlsx(self):
        klass = segmenter.getSegmenterClass("/test/a.xlsx")
        assert klass == segmenter.excelseg.Segmenter, klass

    def test_ppt(self):
        klass = segmenter.getSegmenterClass("/test/a.ppt")
        assert klass == segmenter.pptseg.Segmenter, klass
    def test_pptx(self):
        klass = segmenter.getSegmenterClass("/test/a.pptx")
        assert klass == segmenter.pptseg.Segmenter, klass


def test_getSegmenterClassesTextOnly():
    """Test getSegmenterClasses, using only text files"""

    files = ["foo.txt", "bar.txt"]

    classes = segmenter.getSegmenterClasses(files)

    assert [str(k()) for k in classes] == [str(segmenter.textseg.Segmenter())], ([str(k()) for k in classes],
        [str(segmenter.textseg.Segmenter())])

    key = classes.keys()[0]
    assert len(classes[key]) == 2

    assert "foo.txt" in classes[key]
    assert "bar.txt" in classes[key]
