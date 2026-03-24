#coding: UTF8
"""
Excel segmenter

"""

from win32com.client import DispatchEx
from pywintypes import com_error
import chunker
import office

def getExcel(dispatch=DispatchEx):
    """Retrieve the Excel automation object"""

    return dispatch("Excel.Application")

class Segmenter(object):
    """Excel segmenter"""

    def __init__(self, default_chunker=False):
        """We cache the excel object, so we don't launch a new
        instance for every file"""
        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

        self.excel = None

    def initExcel(self):
        """Launch MS Excel if necessary"""

        if self.excel:
            return

        self.excel = getExcel()
        """The Excel automation object"""

        self.wasVisible = self.excel.Visible
        """If it was not visible, we quit on deletion"""


    def __del__(self):
        """Quit from Excel on delete if it was not visible
        when we started
        """

        if self.excel and not self.wasVisible:
            self.excel.Quit()


    def __str__(self):
        """String representation of our segmenter"""

        return "MS Excel"

    def chunkRange(self, excel_range):
        """Chunkify the specified range

        @param range: The Excel Range object (i.e. UsedRange)
        """

        passes_filter = self.chunking_strategy.passes_filter

        if excel_range and excel_range.Value:
            if isinstance(excel_range.Value, basestring):
                yield excel_range.Value
            else:
                for row in excel_range.Value :
                    for cell in row:
                        if not isinstance(cell, tuple) and passes_filter(cell):
                            yield cell

    def process_shape(self, sheet, shape):

        shapeType = shape.Type

        if shapeType == office.msoOLEControlObject:
            try:
                obj = sheet.OLEObjects(shape.Name)
                text = obj.Object.Caption
                if self.chunking_strategy.passes_filter(text):
                    yield text
            except (AttributeError, com_error), details:
                print "Error getting control text:",
                for detail in details:
                    print detail, ':',
                print
                print "Control:", shape.Name
                print

        elif shapeType == office.msoLine:
            #Assume lines have no text...
            return

        elif shapeType == office.msoPicture:
            try:
                for sub_shape in shape.GroupItems:
                    for chunk in self.process_shape(sub_shape):
                        yield chunk
            except com_error:
                print "Picture has no sub-shapes"

        else:

            try:
                # We need to give a range of characters,              #
                # but we can take advantage of the fact that texboxes #
                # have a maximum length of 255 characters             #
                text = shape.TextFrame.Characters(1, 255).Text
                if self.chunking_strategy.passes_filter(text):
                    yield text
            except (AttributeError, com_error), details:
                print "Error getting shape text:",
                print "Shape:", shape.Name.encode("utf-8")
                print "Shape type:", shape.Type
                print

    def getShapeChunks(self, sheet):
        """Extract text from worksheet shapes

        @param sheet: The Excel worksheet
        """

        for shape in office.ShapeUngrouper(sheet.Shapes).shapes:

            for chunk in self.process_shape(sheet, shape):
                yield chunk

    def get_sentences(self, filename):
        """Retrieve the cell values and shape text for an Excel file

        @param filename: The name of the Excel file
        """

        self.initExcel()
        self.excel.Workbooks.Open(filename)

        for chunk in self.get_sentences_from_excel(self.excel):
            yield chunk

    def get_sentences_from_excel(self, excel):

        for sheet in excel.Sheets:

            # The sheet name
            if sheet.Name:
                yield sheet.Name

            # The cells
            for seg in self.chunkRange(sheet.UsedRange):
                yield unicode(seg)

            # Shapes
            for seg in self.getShapeChunks(sheet):
                yield unicode(seg)

        # Don't save changes when closing
        self.excel.ActiveWorkbook.Close(False)


