# coding: UTF8
"""
app utilities
"""
import os
import sys
import cPickle
import traceback
import datetime
import time
import winpaths

APP_NAME = u"AnalyzeAssist"


def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")


# module_path
def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable,
                                       sys.getfilesystemencoding()))

    return os.path.dirname(unicode(__file__,
                                   sys.getfilesystemencoding()))


def file_name(fname):
    """Returns the name of a file relative to the module path"""

    return os.path.join(module_path(), fname)


def resource_file_name(fname):
    """Returns the name of a resource file relative to module_path()/res"""

    return os.path.join(module_path(), "res", fname)


def load_from_stream(stream):
    """Loads a pickled object from a stream.

    Write and load dict:
    >>> from cStringIO import StringIO
    >>> out = StringIO()
    >>> data = dict(spam="eggs")
    >>> serialize_to_stream(data, out)
    >>> out.seek(0)
    >>> load_from_stream(out)
    {'spam': 'eggs'}
    """

    return cPickle.load(stream)


def load(fname):
    """
    Loads a pickled object from C{fname}.
    """

    try:
        database = open(fname, "r")
        value = load_from_stream(database)
        database.close()
        return value
    except EOFError:
        return None


def serialize_to_stream(obj, stream):
    """Serialize C{obj} to C{stream}.

    >>> from cStringIO import StringIO
    >>> out = StringIO()
    >>> serialize_to_stream(dict(spam="eggs"), out)
    >>> cPickle.loads(out.getvalue())
    {'spam': 'eggs'}
    """
    cPickle.dump(obj, stream)


def serialize(obj, fname):
    """Serialize obj to fname using cPickle

    @param obj: The object (data) to serialize
    @param fname: The name of the output file
    """

    database = open(fname, "w")
    serialize_to_stream(obj, database)
    database.close()


def get_local_app_data_folder():
    app_data = winpaths.get_local_appdata()
    return os.path.join(app_data, APP_NAME)


def get_data_folder():
    if not we_are_frozen():
        data_folder = module_path()
    else:
        data_folder = get_local_app_data_folder()
        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)

    return data_folder


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()
