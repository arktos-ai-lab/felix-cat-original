#coding: UTF8
"""
text file segmenter

"""
import logging

import chunker
import chardet

LOGGER = logging.getLogger(__name__)


def bytes2unicode(bytes, errors='replace'):
    """Convert a byte string into Unicode"""

    if isinstance(bytes, unicode):
        return bytes

    if not bytes:
        return u""

    if bytes.startswith(chr(0xEF) + chr(0xBB) + chr(0xBF)):
        return unicode(bytes[3:], 'utf-8', errors=errors)

    if bytes.startswith(chr(0xFF) + chr(0xFE)):
        return unicode(bytes[2:], 'utf-16', errors=errors)

    if bytes.startswith(chr(0xFE) + chr(0xFF)):
        return unicode(bytes[2:], 'UTF-16BE', errors=errors)

    # No BOM found, so use chardet
    detection = chardet.detect(bytes)
    encoding = detection.get('encoding', 'utf-16')
    return unicode(bytes, encoding or 'utf-16', errors=errors)


class Segmenter(object):
    """
    Text file segmenter
    """

    def __init__(self, default_chunker=False):
        ## Chunking strategy
        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

    def __str__(self):
        return "Text"

    def get_all_text(self, filename):
        """Get all text from file (for wordcount)"""

        text = bytes2unicode(open(filename,"rb").read(), 'replace')

        for line in text.splitlines():
            if line.strip():
                yield line

    def get_sentences(self, filename):
        """Get chunks for filename

        @param filename: The name of the file to process
        """

        text = bytes2unicode(open(filename, "rb").read())

        for seg in self.get_text_segs(text):
            yield seg

    def get_text_segs(self, text):
        get_sentences = self.chunking_strategy.get_sentences
        for line in text.splitlines():
            if line.strip():
                for seg in get_sentences(line):
                    yield seg


