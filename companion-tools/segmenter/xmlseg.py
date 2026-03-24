#coding: UTF8
"""
XML file segmenter module
"""

import chunker
from lxml import etree
from lxml.html import soupparser

def get_soup_root(filename):
    """Use ElementSoup to parse the XML

    @param filename: the name of the XML file to parse

    """

    return soupparser.parse(filename)

def get_soup_root_text(fileobj):
    """Use ElementSoup to parse the XML"""

    return soupparser.fromstring(fileobj.read())

class Segmenter(object):
    """XML file segmenter"""

    def __init__(self, default_chunker=False):
        """Cache the Word object.
        """
        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

        self.segs = []

    def __str__(self):

        return "XML"

    def get_sentences(self, filename):
        """Get the segments for <filename>

        @param filename: the name of the file to chunkify

        @return: a list of segmented text chunks

        """

        return self.get_chunks(open(filename).read())

    def get_chunks(self, text):
        """Retrieves the chunks for the supplied text"""

        try:
            root = etree.fromstring(text)
        except:
            root = soupparser.fromstring(text)

        self.segs = [x for x in root.itertext() if x.strip()]
        return self.segs

    def chunkKids(self, node):
        """Recursively traverse nodes, collecting each text node

        @param node: the current node
        """

        if node.text and node.text.strip():
            self.segs += [x for x in self.chunking_strategy.get_sentences(node.text)]

        for kid in node.getchildren():
            self.chunkKids(kid)


