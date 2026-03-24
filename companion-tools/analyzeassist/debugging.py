# coding: UTF8
"""
Used for logging and other debugging stuff

"""
import os
import AppUtils
from AppUtils import get_data_folder
import sys

OUTFILE = None


def get_logfile(filename):
    return os.path.join(get_data_folder(),
                        filename)


if AppUtils.we_are_frozen():
    OUTFILE = open(get_logfile("analyze_assist.log"), "w")
else:
    OUTFILE = sys.stdout
