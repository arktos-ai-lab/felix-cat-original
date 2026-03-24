#coding: UTF8
"""
Html segmenter.

Currently uses BeautifulSoup as the HTML parser
"""

import chunker
from BeautifulSoup import BeautifulSoup as bsoup
from BeautifulSoup import BeautifulStoneSoup
import re
import chardet
import urllib2

WANT_A_TITLE = True
WANT_IMG_ALT = True
WANT_INPUT_VALUE = True
WANT_META_DESCRIPTION = True
WANT_META_KEYWORDS = True


CHARSET_FINDER = re.compile(u'<meta[\s\S]*?charset\s*=\s*([\S]+)"[^>]*?>', re.I)

PRE_PARSE_STRIPPER = re.compile(u"|".join([u"<body*?>|</body>",
                                 u"<a[^>]*?>|</a>",
                                 u"<img[^>]*?>|</img>",
                                 u"<input[^>]*?>|</input>",
                                 u"<script*?>[\s\S]*?</script>",
                                 u"<form[^>]*?>|</form>"]),
                                re.I | re.M)

TAG_SPLITTER = re.compile(u'|'.join([u"<p*?>|</p>",
                                 u"<div[^>]*?>|</div>",
                                 u"<td[^>]*?>|</td>",
                                 u"<th[^>]*?>|</th>",
                                 u"<li[^>]*?>|</li>",
                                 u"<h\d[^>]*?>|</h\d>",
                                 u"<dd[^>]*?>|</dd>",
                                 u"<dt[^>]*?>|</dt>",
                                 u"<br[^>]*?>"]),
                                 re.I | re.M)

def normalize(text):
    """Normalize whitepace in C{text}.
    
    >>> normalize(u"   spam\\n\\tspam   SPAM")
    u'spam spam SPAM'
    """

    return u' '.join(text.split())

def get_encoding(text):
    """
    Retrieve the encoding META tag, if present.
    Otherwise, use check for BOM.
    If there's no BOM, use chardet.
    """

    charset_match = CHARSET_FINDER.search(text)
    if charset_match:
        return charset_match.groups(0)[0]

    if text.startswith(chr(0xEF) + chr(0xBB) + chr(0xBF)):
        return 'utf-8'
        
    if text.startswith(chr(0xFF) + chr(0xFE)):
        return 'utf-16'

    if text.startswith(chr(0xFE) + chr(0xFF)):
        return 'UTF-16BE'
    
    # No BOM found, so use chardet
    detection = chardet.detect(text)
    return detection.get('encoding')


def get_default_wanted_attrs():
    """
    Get the wanted attribute pairs (tag, attribute)
    when the user didn't supply a list
    """
    attrs = []
    if WANT_A_TITLE:
        attrs.append("a title".split())
    if WANT_IMG_ALT:
        attrs.append("img alt".split())
    if WANT_INPUT_VALUE:
        attrs.append("input value".split())
    if WANT_META_DESCRIPTION:
        attrs.append("meta description".split())
    if WANT_META_KEYWORDS:
        attrs.append("meta keywords".split())
    return attrs

class Segmenter(object):
    """Html segmenter"""
    
    def __init__(self, default_chunker=False,
                 wanted_attrs=None):
        if not default_chunker:
            self.chunking_strategy = chunker.get_chunker()
        else:
            self.chunking_strategy = chunker.Chunker()

        if wanted_attrs is None:
            self.wanted_attrs = get_default_wanted_attrs()
        else:
            self.wanted_attrs = wanted_attrs

        # We don't segment on whitespace in HTML documents
        self.chunking_strategy.stop_chars = set()
        self.chunking_strategy.seg_on_control_chars = False
        markers = self.chunking_strategy.sentence_end_markers
        self.chunking_strategy.sentence_end_markers = [m for m in markers if m not in [u"\t", u"\n", u"\r"]]

        self.soup = None
        
    def __str__(self):
        return "HTML"
    
    def get_attributes(self, tag, attr):
        """Get all attrName values for tag tags"""
        
        attrs = []
        
        tags = self.soup.findAll(tag)
        
        for tag in tags:
            try:
                value = tag[attr]
                if value:
                    attrs.append(value)
            except KeyError:
                pass

        return attrs

    def get_sentences(self, filename):
        """Generator to yield all the segments in our HTML file"""
        
        if filename.startswith("http"):
            for chunk in self.get_sentences_from_url(filename):
                yield chunk
            return
        
        text = open(filename, "r").read()
        for chunk in self.parseChunks(text,
                                      get_encoding(text)):
            yield chunk

    def get_sentences_from_url(self, url):
        """
        This enables us to parse a file from a URL
        """

        text = urllib2.urlopen(url).read()
        for chunk in self.parseChunks(text,
                                      get_encoding(text)):
            yield chunk
        
    def parseChunks(self, html_file, encoding):
        """Parse the file into segments"""

        self.soup = bsoup(html_file, fromEncoding=encoding)
        
        big_chunks = []
        
        # document title
        if self.soup.head:
            title = self.soup.head.title
            if title:
                big_chunks.append(title.string)
        
        # image alt attributes, anchor title attributes, input value attributes
        for tag, attr in self.wanted_attrs:
            big_chunks.extend(self.get_attributes(tag, attr))

        # Parse the body text
        if self.soup.body:
            text = PRE_PARSE_STRIPPER.sub(u"", unicode(self.soup.body))
            body_chunks = TAG_SPLITTER.split(text)
            for chunk in body_chunks:
                if ".&nbsp;" in chunk and not chunk.endswith(".&nbsp;"):
                    mini_chunks = chunk.split(".&nbsp;")
                    big_chunks += [x + "." for x in mini_chunks[:-1]]
                    big_chunks.append(mini_chunks[-1])
                else:
                    big_chunks.append(chunk)

        # Further chunkify each of the big chunks we got above
        get_chunks = self.chunking_strategy.get_sentences
        for line in big_chunks:
            if line and line.strip():
                for seg in get_chunks(html2plain(line)):
                    yield normalize(seg)
                    

TAG_STRIPPER = re.compile(u"<[!\w/][\s\S]*?>", re.I | re.M)

def strip_tags(line):
    """strip the HTML tags from the line
    
    >>> strip_tags(u"<b>spam</b>")
    u'spam'
    
    """

    return TAG_STRIPPER.sub(u"", line)

def html2plain(text):
    """Strips out tags from HTML text
    
    >>> html2plain('spam&nbsp;<b>eggs</b>')
    u'spam\\xa0eggs'
    >>> html2plain('-->')
    u'-->'
    """

    entities = BeautifulStoneSoup.HTML_ENTITIES
    text = unicode(BeautifulStoneSoup(strip_tags(text),
                                      convertEntities=entities))
    return text.replace(u"&gt;", ">").replace(u"&lt;", "<")

