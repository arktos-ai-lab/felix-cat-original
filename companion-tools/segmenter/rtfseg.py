#coding: UTF8
"""RTF segmenter

"""

import chunker
import re

controlChars = { "bullet" : '\u0095',
                 "endash" : u'\u2013',
                 "emdash" : u'\u2014',
                 "enspace" : u'\u2002',
                 "emspace" : u'\u2003',
                 "lquote" : u'\u2018',
                 "rquote" : u'\u2019',
                 "ldblquote" : u'\u201c',
                 "rdblquote" : u'\u201d',
                "\r" : u'\r', # [return] -- ignored (unless preceded by an escaping backslash)
                "\n" : u'\n', # [linefeed] -- ignored (unless preceded by an escaping backslash)
                "tab" : u'\t',
                "par" : u'\r\n',
                "line" : u'\n',
                "\\" : u'\\', # a backslash   (same as \'5c)
                "{" : u'{', # an open-brace (same as \'7b)
                "}" : u'}', # a close-brace (same as \'7d)
                "~" : u'\u2002', # non-breaking space
                "-" : u'-', # optional hyphen (!)
                "_" : u'-', # non-breaking hyphen
}
"""Various RTF control characters that we map into Unicode characters
"""

matchEscape1 = re.compile(r"^'[a-f0-9]{2}[\s\\]", re.IGNORECASE)
matchEscape2 = re.compile(r"^'[a-f0-9]{2}$", re.IGNORECASE)
codepageMatcher = re.compile('[\s\S]*ansicpg(\d+)[\s\S]*')

def isEscapedChar(text):
    """ \'XX -- escaped character """

    return matchEscape1.match(text) or \
        matchEscape2.match(text)

class listMaker(object):
    """Parses an RTF file into a nested list structure, then
    parses the text portions into segments
    """

    def __init__(self, text):
        
        self.text = text

        self.structure = []
        self.index = 0
        """Our position in the file
        """

        self.encoding = 'ascii'

        while self.current() != '{':
            self.index += 1

        assert self.current() == '{'

        self.index += 1
        self.structure = self._parse()
        
    def current(self):
        """The current character in the file
        
        @return: The character that self.index is currently pointing at
        """

        return self.text[self.index]

    def _parse(self):
        """Parses the input file into a nested list structure
        
        Called recursively as we parse the various nesting levels
        
        @return: a nested list structure for parsing the text bits
        """

        substructure = []
        atom = ''

        while 1:
            if self.current() == '}': # end of the structure
                self.index += 1
                if atom:
                    substructure.append(atom)
                return substructure

            elif self.current() == '{':
                self.index += 1
                if atom:
                    if atom.startswith('\\rtf'):
                        m = codepageMatcher.match(atom)
                        if m:
                            print "Found codepage:", m.group(1)
                            self.codepage = m.group(1)
                        pass # print atom
                    
                    elif atom.startswith('\\paperw'):
                        pass # print "'\\paperw' -- ignoring"
                    elif atom.startswith('\\fet'):
                        pass # print "'\\fet' -- ignoring"
                    elif atom == '\n':
                        pass
                    else:
                        substructure.append(atom)
                    atom = ''
                sub = self._parse()
                if sub:
                    if sub[0].startswith('\\fonttbl'):
                        pass # print "Font table -- ignoring"
                    elif sub[0].startswith('\\colortbl'):
                        pass # print "Color table -- ignoring"
                    elif sub[0].startswith('\\stylesheet'):
                        pass # print "Style sheet -- ignoring"
                    elif sub[0].startswith('\\*\\latentstyles'):
                        pass # print "Latent styles -- ignoring"
                    elif sub[0].startswith('\\*\\rsidtbl'):
                        pass # print "rsidtbl -- ignoring"
                    elif sub[0].startswith('\\*\\generator'):
                        pass # print "generator -- ignoring"
                    elif sub[0].startswith('\\info'):
                        pass # print "Doc info -- ignoring"
                    elif sub[0].startswith('\\upr'):
                        pass # print "upr -- ignoring"
                    elif sub[0].startswith('\\*\\pnseclvl'):
                        pass # print "Default list format instructions -- ignoring"
                    else:
                        substructure.append(sub)

            else:
                atom += self.current()
                self.index += 1

    def segText(self, text):
        """Parses out the text from the control statements and other mess.
        
        Converts control characters into Unicode along the way. Breaks
        into chunks based on tabs and newlines.
        
        @param text: a chunk of text, possibly with RTF control
        statements embedded
        
        @return: yields cleaned-up text segments
        """

        chunks = []
        elements = text.split()

        for element in elements:
            if element.startswith('\\'): # control
                try:
                    command = element[1:].split('\\')[0].strip()
                    char = controlChars[command]
                    
                    if char in [u'\t', u'\n', u'\r', u'\r\n']:
                        yield u' '.join(chunks)
                        chunks = []
                    else:
                        chunks.append(char)
                        
                except KeyError, e:
                    pass

            else:
                chunks.append(unicode(element, self.encoding))

        if chunks:
            yield u' '.join(chunks)

    def segSub(self, sub):
        """Yields text segments from parsed RTF structure.
        
        Goes through our nested list structure, yielding out
        segment chunks for string elements
        """
        for element in sub:
            if isinstance(element, basestring):
                for seg in self.segText(element):
                    yield seg
            else:
                for seg in self.segSub(element):
                    yield seg
                    
                
    def get_sentences(self):
        """Gets the text chunks from the RTF file.
        
        Calls the recursive L{segSub} method.
        """

        for seg in self.segSub(self.structure):
            yield seg


class Segmenter(object):
    """RTF segmenter"""
    
    def __init__(self):
        
        self.chunking_strategy = chunker.get_chunker()
        """Our chunking strategy"""
    
    def __str__(self):
        return "RTF"

    def get_sentences(self, filename):
        """Retrieve the segments in filename
        
        @param filename: the name of the RTF file to parse
        
        """

        text = open(filename, "rb").read()

        for chunk in self.get_sentences_from_text(text):
            yield chunk

    def get_sentences_from_text(self, text):
        maker = listMaker(text)
        
        for seg in maker.get_sentences():
            for chunk in self.chunking_strategy.get_sentences(seg):
                yield chunk
