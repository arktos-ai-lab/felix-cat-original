# coding: UTF8
"""
Encode streams

Classes:
    OutStreamEncoder
        Wraps a stream with an encoder.
        Example:
            sys.out = OutStreamEncoder(sys.out, "utf-8")

MIT license
"""

import sys

__author__ = "Ryan Ginstrom"
__version__ = "0.1"


class OutStreamEncoder(object):
    """Wraps a stream with an encoder
    
    >>> from cStringIO import StringIO as si
    >>> out = si()
    >>> # nihongo = unicode('日本語', "utf-8")
    >>> nihongo = unicode('\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e', "utf-8")
    >>> print >> out, nihongo
    Traceback (most recent call last):
      ...
        print >> out, nihongo
    UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-2: ordinal not in range(128)
    >>> out = OutStreamEncoder(out, "utf-8")
    >>> print >> out, nihongo
    >>> out.getvalue()
    '\\xe6\\x97\\xa5\\xe6\\x9c\\xac\\xe8\\xaa\\x9e\\n'
    """

    def __init__(self, outstream, encoding=None):
        self.out = outstream
        if not encoding:
            self.encoding = sys.getfilesystemencoding()
        else:
            self.encoding = encoding

    def write(self, obj):
        """Wraps the output stream, encoding unicode strings """

        if isinstance(obj, unicode):
            self.out.write(obj.encode(self.encoding))
        else:
            self.out.write(obj)

    def __getattr__(self, attr):
        """Delegate everything but write to the stream"""

        return getattr(self.out, attr)


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()