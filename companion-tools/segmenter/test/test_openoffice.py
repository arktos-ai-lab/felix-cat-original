#coding: UTF8
"""
Unit test the rtf segmenter

"""
import zipfile
from cStringIO import StringIO

import mock

from segmenter import openofficeseg
from segmenter.openofficeseg import Segmenter


class TestOpenOfficeSegmenter:
    def setup(self):
        self.segmenter = Segmenter()

        self.DOC_TEXT = r"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rpt="http://openoffice.org/2005/report" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:officeooo="http://openoffice.org/2009/office" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:drawooo="http://openoffice.org/2010/draw" xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0" xmlns:css3t="http://www.w3.org/TR/css3-text/" office:version="1.2"><office:scripts/><office:font-face-decls><style:font-face style:name="Mangal1" svg:font-family="Mangal"/><style:font-face style:name="Times New Roman" svg:font-family="&apos;Times New Roman&apos;" style:font-family-generic="roman" style:font-pitch="variable"/><style:font-face style:name="Arial" svg:font-family="Arial" style:font-family-generic="swiss" style:font-pitch="variable"/><style:font-face style:name="Mangal" svg:font-family="Mangal" style:font-family-generic="system" style:font-pitch="variable"/><style:font-face style:name="ＭＳ Ｐゴシック" svg:font-family="&apos;ＭＳ Ｐゴシック&apos;" style:font-family-generic="system" style:font-pitch="variable"/><style:font-face style:name="ＭＳ Ｐ明朝" svg:font-family="&apos;ＭＳ Ｐ明朝&apos;" style:font-family-generic="system" style:font-pitch="variable"/></office:font-face-decls><office:automatic-styles><style:style style:name="P1" style:family="paragraph" style:parent-style-name="Standard"><style:text-properties officeooo:rsid="001e3f73" officeooo:paragraph-rsid="001e3f73"/></style:style></office:automatic-styles><office:body><office:text><text:sequence-decls><text:sequence-decl text:display-outline-level="0" text:name="Illustration"/><text:sequence-decl text:display-outline-level="0" text:name="Table"/><text:sequence-decl text:display-outline-level="0" text:name="Text"/><text:sequence-decl text:display-outline-level="0" text:name="Drawing"/></text:sequence-decls><text:p text:style-name="P1">Hello, world!</text:p></office:text></office:body></office:document-content>
"""

    def testStr(self):

        assert u"OpenOffice" == str(self.segmenter)

    def test_get_sentences(self):
        doc_file = StringIO()
        zipped = zipfile.ZipFile(doc_file, 'a')
        zipped.writestr('content.xml', self.DOC_TEXT)
        zipped.close()
        open_name = '__builtin__.open'
        with mock.patch(open_name, create=True) as mock_open:
            mock_open.return_value = doc_file

            segs = [x for x in self.segmenter.get_sentences('filename')]

            expected = [u'Hello, world!']

            assert segs == expected, segs


    def test_get_sentences_from_text(self):

        segs = [x for x in self.segmenter.get_sentences_from_text(self.DOC_TEXT)]

        expected = [u'Hello, world!']

        assert segs == expected, segs
