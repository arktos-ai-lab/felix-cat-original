#!/usr/bin/env python

import win32api
import sys

try:
    USER_NAME = unicode(win32api.GetUserName(), sys.getfilesystemencoding())
except:
    USER_NAME = u"Default"
