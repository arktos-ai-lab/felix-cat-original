#coding: UTF8
"""
Word file segmenter module

To get all the segments from a Word document:

segger = wordseg.Segmenter()

for seg in segger.get_sentences("/test/file.doc"):
    print seg
"""

from win32com.client import DispatchEx
import chunker
import office
from office import msoAutoShape, msoTextBox, wdTextFrameStory


def getWord(dispatch_function=DispatchEx):
    """Retrieve the Word automation object"""

    return dispatch_function("Word.Application")


class Segmenter(object):
    """Word file segmenter"""

    def __init__(self, default_chunker=False):
        """Cache the Word object.
        """
        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

        self.word = None
        self.was_visible = False

    def initWord(self):
        
        if self.word:
            return
        
        # The Word automation object
        self.word = getWord()

        # If it was not visible, we quit on deletion
        self.was_visible = self.word.Visible

    def __del__(self):
        """Quit from Word on delete if it was not visible
        when we started
        """

        if self.word and not self.was_visible:
            self.word.Quit(False)

    def __str__(self):
        return "MS Word"

    def getFrameText(self, shape):
        try:
            if shape.TextFrame.HasText:
                return shape.TextFrame.TextRange.Text
        except Exception, e:
            print "Failed to get text from shape:", e
            return ""
        return ""

    def get_all_text(self, filename):
        """Get all the text from the document, including spaces"""

        self.initWord()

        doc = self.word.Documents.Open(filename)
        
        ungrouper = office.ShapeUngrouper(doc.Shapes)

        for story_range in doc.StoryRanges:
            if story_range.StoryType != wdTextFrameStory:
                for line in story_range.Text.splitlines():
                    yield line

        for shape in doc.Shapes:
            if shape.Type == msoTextBox: # 17
                for line in self.getFrameText(shape).splitlines():
                    yield line

            elif shape.Type == msoAutoShape: # 1
                try:
                    text = shape.TextFrame.TextRange.Text
                    for line in text.splitlines():
                        yield line
                except Exception, details:
                    print "Error retrieving AutoShape text:", details
                    
        doc.Close(False)

    def get_sentences(self, filename):
        """Get the segments for <filename>"""

        self.initWord()

        doc = self.word.Documents.Open(filename)
        
        ungrouper = office.ShapeUngrouper(doc.Shapes)

        for story_range in doc.StoryRanges:
            if story_range.StoryType != wdTextFrameStory:
                for line in story_range.Text.splitlines():
                    for seg in self.chunking_strategy.get_sentences(line):
                        yield seg

        for shape in doc.Shapes:
            if shape.Type == msoTextBox: # 17
                for line in self.getFrameText(shape).splitlines():
                    for seg in self.chunking_strategy.get_sentences(line):
                        yield seg
            elif shape.Type == msoAutoShape: # 1
                try:
                    text = shape.TextFrame.TextRange.Text
                    for line in text.splitlines():
                        for seg in self.chunking_strategy.get_sentences(line):
                            yield seg
                except Exception, details:
                    print "Error retrieving AutoShape text:", details
                    
                        
        doc.Close(False)

