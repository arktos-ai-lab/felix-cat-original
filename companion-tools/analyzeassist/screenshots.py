# coding: UTF8
"""
Enter module description here.

"""

from win32com.client import Dispatch
import os
import subprocess
from PIL import Image
import glob

from pywinauto import application
from pywinauto import clipboard

import win32api, win32con
import time


def make_thumbs():
    size = 256, 256

    for infile in glob.glob("website/*.png"):
        base, ext = os.path.splitext(infile)
        im = Image.open(infile)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(base + "-small" + ext, "png")


def clear_images():
    for filename in glob.glob("website/*.png"):
        os.remove(filename)


def main():
    clear_images()

    executable = r'"C:/Program Files/AnalyzeAssist/AnalyzeAssist.exe"'
    app = application.Application.start(executable)

    align_assist = app["Analyze Assist"]

    align_assist.TypeKeys("%TLE")
    align_assist.TypeKeys("%FX")

    # now it's English
    app = application.Application.start(executable)
    time.sleep(.2)  # wait for the contents to be rendered...
    # python is slow, after all :)
    align_assist = app["Analyze Assist"]
    align_assist.CaptureAsImage().save("website/AnalyzeAssist.png")

    app["Align Assist"].TypeKeys("%FX")

    make_thumbs()


if __name__ == "__main__":
    main()