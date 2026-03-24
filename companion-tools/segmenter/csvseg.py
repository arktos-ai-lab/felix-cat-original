#coding: UTF8
"""
text file segmenter

"""

import sys
import chardet
import csv

def bytes2unicode(bytes, errors='replace'):
    """Convert a byte string into Unicode"""
    
    if bytes.startswith(chr(0xEF) + chr(0xBB) + chr(0xBF)):
        return unicode(bytes[3:], 'utf-8', errors=errors)
        
    if bytes.startswith(chr(0xFF) + chr(0xFE)):
        return unicode(bytes[2:], 'utf-16', errors=errors)

    if bytes.startswith(chr(0xFE) + chr(0xFF)):
        return unicode(bytes[2:], 'UTF-16BE', errors=errors)
    
    # No BOM found, so use chardet
    detection = chardet.detect(bytes)
    encoding = detection.get('encoding', 'utf-16')
    return unicode(bytes, encoding, errors=errors)

def unicode_csv_reader(unicode_csv_data):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data))
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        for cell in row:
            yield unicode(cell, 'utf-8')

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data.splitlines():
        yield line.encode('utf-8')
    
class Segmenter(object):
    """Text file segmenter"""

    def __str__(self):
        return "CSV"
        
    def get_sentences(self, filename):
        """Get all text from file (for wordcount)"""

        raw_text = open(filename,"rb").read()

        for chunk in self.get_chunks(raw_text):
            yield chunk
    
    def get_chunks(self, raw_text):
        text = bytes2unicode(raw_text, 'replace')
        for cell in unicode_csv_reader(text):
            yield cell
    
