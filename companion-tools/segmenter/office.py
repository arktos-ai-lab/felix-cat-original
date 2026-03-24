#coding: UTF8
"""
MS Office constants and utilities

"""
from pywintypes import com_error

# Office constants
msoShapeTypeMixed = -2
msoAutoShape = 1
msoCallout = 2
msoChart = 3
msoComment = 4
msoFreeform = 5
msoGroup = 6
msoEmbeddedOLEObject = 7
msoFormControl = 8
msoLine = 9
msoLinkedOLEObject = 10
msoLinkedPicture = 11
msoOLEControlObject = 12
msoPicture = 13
msoPlaceholder = 14
msoTextEffect = 15
msoMedia = 16
msoTextBox = 17
msoScriptAnchor = 18
msoTable = 19
msoCanvas = 20
msoDiagram = 21


# enum WdStoryType
wdMainTextStory = 1
wdFootnotesStory = 2
wdEndnotesStory = 3
wdCommentsStory = 4
wdTextFrameStory = 5
wdEvenPagesHeaderStory = 6
wdPrimaryHeaderStory = 7
wdEvenPagesFooterStory = 8
wdPrimaryFooterStory = 9
wdFirstPageHeaderStory = 10
wdFirstPageFooterStory = 11

ppWindowNormal = 1
ppWindowMinimized = 2
ppWindowMaximized = 3
ppArrangeTiled = 1
ppArrangeCascade = 2

####################
# ShapeUngrouper
####################

class ShapeUngrouper(object):
    """Ungroup all the shapes on the slide,
    so we can examine each shape individually"""

    def __init__(self, s):
        self.shapes = s
        while self.hasGroupedShapes():
            pass

    def hasGroupedShapes(self):
        """We should split this up into return value/side effect"""
        
        result = False
        for shape in self.shapes:
            if shape.Type == msoGroup:
                try:
                    shape.Ungroup()
                    result = True
                except com_error:
                    pass
        return result

