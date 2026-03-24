#coding: UTF8
"""PPT segmenter
"""

from win32com.client import DispatchEx
import chunker
import office
from pythoncom import com_error

def get_ppt(dispatch=DispatchEx):
    """Get the PowerPoint automation object"""
    return dispatch("PowerPoint.Application")


def get_ordinary_shape_text(shape):
    """
    Plain vanilla textbox
    """

    try:
        return shape.TextFrame.TextRange.Text
    except Exception:
        # Failed to get text from text range.
        return ""


def process_table(table):
    """
    Process a table in a PowerPoint slide
    """

    for row in table.Rows:
        for cell in row.Cells:
            try:
                cell_textrange = cell.Shape.TextFrame.TextRange
                if cell_textrange:
                    yield cell_textrange.Text
            except Exception:
                # print "Failed to get TextRange from PowerPoint cell:", e
                pass

def print_error(msg, details):
    """
    Print an error for the benefit of the log
    """
    print msg
    import traceback
    print traceback.format_exc()
    for detail in details:
        print detail


def extract_excel_text(shape):
    """
    Process embedded excel worksheets in the powerpoint slide
    """

    try:
        format = shape.OLEFormat
        format.Activate()
        excel = format.Object
        sheet = excel.ActiveSheet
    except AttributeError, details:
        print "Failed to extract text from excel sheet:", str(details)
        return
    import excelseg

    excel_segmenter = excelseg.Segmenter()

    for cell in excel_segmenter.chunkRange(sheet.UsedRange):
        yield cell

    for chunk in excel_segmenter.getShapeChunks(sheet):
        yield chunk

class Segmenter(object):
    """
    PowerPoint segmenter
    """

    def __init__(self, default_chunker=False):
        """
        In order to extract the embedded Excel worksheets,
        we've got to make the sheet visible.
        """

        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

        self.ppt = None

    def init_ppt(self):
        if self.ppt:
            return

        self.ppt = get_ppt()
        self.wasVisible = self.ppt.Visible
        """If it was not visible, we quit on deletion"""
        self.ppt.WindowState = office.ppWindowMinimized
        self.ppt.Visible = 1


    def __del__(self):
        """
        Quit from PowerPoint on delete if it was not visible
        when we started
        """

        if self.ppt and not self.wasVisible:
            self.ppt.Quit()

    def __str__(self):
        return "MS PowerPoint"

    def processNotes(self, slide):
        """
        Go through the shapes on the NotesPage, and try
        to get the text from each
        """

        # The notes page
        for shape in slide.NotesPage.Shapes:
            text = self.get_notes_text(shape)
            if text:
                yield text


    def get_notes_text(self, shape):
        """
        Get the text from the notes portion of the slide

        The NotesPage object has two shapes, one of which has
        the textframe we are after. We try to get the text
        from this shape; if we fail, it must be the other one :-)

        @param shape: the shape, possibly having a TextFrame
        """

        try:
            return shape.TextFrame.TextRange.Text
        except Exception:
            # Failed to get PowerPoint Notes TextFrame
            return ""

    def get_sentences(self, filename):
        """
        Get the segments from <filename>

        @param filename: the name of the PowerPoint file to parse

        """

        self.init_ppt()

        # We have got to set the fourth argument to False, in order
        # to script PowerPoint with the window invisible
        pres = self.ppt.Presentations.Open(filename, True, False, True)

        get_sentences = self.chunking_strategy.get_sentences
        try:
            for slide in pres.Slides:

                for shape in office.ShapeUngrouper(slide.Shapes).shapes:
                    self.preprocess_shape(shape)

                #==========================================================#
                # In this second pass, we ought to have embedded objects   #
                # "ungrouped" into PowerPoint shapes, so we are ready      #
                # to rock and roll                                         #
                #==========================================================#
                # A problem with this approach is that it won't catch      #
                # foreign objects embedded within foreign objects          #
                # (such as the dreaded "Excel sheet embedded in Word doc   #
                # embedded in PPT sheet..."), but I don't think we should  #
                # even condone such horrid abuses!                         #
                #==========================================================#
                for shape in office.ShapeUngrouper(slide.Shapes).shapes:

                    for chunked_seg in self.chunk_shape(shape):
                        yield chunked_seg

                for seg in self.processNotes(slide):
                    for chunked_seg in get_sentences(seg):
                        yield chunked_seg
        finally:
            pres.Close()

    def preprocess_shape(self, shape):
        """
        Run the shape through an initial preprocessing step.

        In the first pass, we look for embedded objects
        other than MS Excel. If our Excel processing fails,
        then we try ungrouping them, to get at the
        shap-ey goodness inside...

        Note that doing this step in ShapeUngrouper itself doesn't
        work, because PowerPoint starts complaining at us
        """
        if shape.Type != office.msoEmbeddedOLEObject:
            return

        try:
            for x in extract_excel_text(shape):
                pass
        except (com_error, AttributeError), details:
            print "Error activating OLE object"
            try:
                shape.Ungroup()
            except Exception, details:
                print_error("Failed to ungroup OLE object", details)

    def chunk_shape(self, shape):
        """
        Get the text segments from a PowerPoint shape
        """

        get_chunks = self.chunking_strategy.get_sentences

        # Table
        if shape.Type == office.msoTable:
            for seg in [ x for x in process_table(shape.Table) ]:
                for chunked_seg in get_chunks(seg):
                    yield chunked_seg

        # MsExcel
        elif shape.Type == office.msoEmbeddedOLEObject:
            try:
                passes_filter = self.chunking_strategy.passes_filter
                for seg in [ x for x in extract_excel_text(shape) if passes_filter(x)]:
                    yield seg
            except com_error, details:
                print_error("Failed to exract text from embedded object",
                            details)

        # Ordinary textbox
        else:
            for chunked_seg in get_chunks(get_ordinary_shape_text(shape)):
                yield chunked_seg

