# coding: UTF-8

__author__ = 'Ryan'

import sys
import os

def we_are_frozen():
    """
    Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located.
    """

    return hasattr(sys, "frozen")

def absdir(x):
    '''
    compose these guys for convenience
    '''

    return os.path.abspath(os.path.dirname(x))

def frozen_path():
    """
    The path when "frozen" using py2exe
    """
    return absdir(unicode(sys.executable, sys.getfilesystemencoding()))

def thawed_path(filename):
    """
    The path when run as a python script.
    """
    return absdir(unicode(filename, sys.getfilesystemencoding()))

# module_path
def module_path():
    """
    This will get us the program's directory,
    even if we are frozen using py2exe
    """

    if we_are_frozen():
        return frozen_path()

    return thawed_path(__file__)