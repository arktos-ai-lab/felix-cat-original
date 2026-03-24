#coding: UTF8
"""
Used for logging and other debugging stuff

"""
import winpaths
import datetime
import time
import traceback
import os
import AppUtils
from AppUtils import get_data_folder
import sys

OUTFILE = None

def get_now():
    return datetime.datetime(*time.localtime()[:6]).strftime("%Y-%m-%d %H:%M:%S")

def log(severity, msg):
    if isinstance(msg, unicode):
        msg = msg.encode("utf-8")
    OUTFILE.write("%s\t%s\t%s\n" % (severity, get_now(), msg))
    OUTFILE.flush()

def debug(msg):
    log("INFO", msg)
def warn(msg):
    log("WARN", msg)
def error(msg):
    log("ERROR", msg)

def log_err(msg = None):
    if msg:
        error(msg)
    for i, line in enumerate(traceback.format_exc().splitlines()):
        if not msg and not i:
            try:
                error(unicode(line))
            except:
                error(repr(line))
        else:
            try:
                print "\t\t%s" % unicode(line)
            except:
                print "\t\t%s" % repr(line)

def get_logfile(filename):
    return os.path.join(get_data_folder(),
                        filename)

if AppUtils.we_are_frozen():
    OUTFILE = open(get_logfile("analyze_assist.log"), "w")
else:
    OUTFILE = sys.stdout
