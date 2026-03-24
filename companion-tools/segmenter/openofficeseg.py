#!/usr/bin/env python

import zipfile

import lxml.etree

import chunker


class Segmenter(object):
    """
    OpenOffice (LibreOffice) file segmenter
    """

    def __init__(self, default_chunker=False):
        ## Chunking strategy
        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

    def __str__(self):
        return "OpenOffice"

    def get_sentences(self, filename):
        """
        Get chunks for filename

        `filename` - The name of the file to process.
        """

        file_obj = open(filename, 'rb')
        zipped_files = zipfile.ZipFile(file_obj)
        file_text = zipped_files.read('content.xml')

        for chunk in self.get_sentences_from_text(file_text):
            yield chunk

    def get_sentences_from_text(self, file_text):
        """
        Get chunks from text string.
        `file_text` should be an OpenOffice file.
        """

        tree = lxml.etree.fromstring(file_text)

        get_sentences = self.chunking_strategy.get_sentences

        xpath = ".//{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"
        for p in tree.findall(xpath):
            if p.find(xpath) is None:
                text = u"".join(list(p.itertext()))
                for line in text.splitlines():
                    if line.strip():
                        for seg in get_sentences(line):
                            yield seg

