# coding: UTF8
"""
Setup program for AnalyzeAssist

Uses py2exe to build a stand-alone executable.

Todo: Unit tests!
"""

from distutils.core import setup
import sys

import py2exe
import glob
import os
from shutil import copytree
import time
import main
import model
import ShowLogs

VERSION = main.__version__
WX_DIR = os.path.abspath(r"D:\Python27\Lib\site-packages\wx-3.0-msw\wx")


def clean_dir(dir_name):
    """Remove all prior fields from the dist (dir_name) directory"""

    print "-" * 20
    print "Cleaning directory", dir_name
    from os.path import join

    for root, dirs, files in os.walk(dir_name, topdown=False):
        for name in files:
            os.remove(join(root, name))
        for name in dirs:
            os.rmdir(join(root, name))
    print "-" * 20


def get_setup_dict(script, name):
    """Create a dictionary to pass to setup"""

    app_name = name
    app_version = VERSION

    setup_dict = {}

    base_info = dict(version=app_version,
                     company_name="Ginstrom IT Solutions (GITS)",
                     copyright="(C) Ginstrom IT Solutions (GITS)",
                     author="Ginstrom IT Solutions (GITS)",
                     author_email="software@ginstrom.com")

    analyze_assist = dict(
        description="Analyzes source files for translation pre-processing",
        script=script,
        icon_resources=[(1, "./res/AnalyzeAssist.ico")],
        dest_base=app_name,
        version=app_version,
        name="%s Application v %s" % (app_name, app_version),
    )

    show_logs = dict(
        description="Shows Analyze Assist log file",
        script="ShowLogs.py",
        dest_base=ShowLogs.APP_NAME,
        version=ShowLogs.__version__,
        name="%s Application v %s" % (ShowLogs.APP_NAME, ShowLogs.__version__),
    )

    c_extract_segments = dict(
        description="Outputs infiles into newline-delimited segments in outfiles",
        script="./extract_segments.py",
        dest_base="extract_segments",
        version=app_version,
        name="extract_segments Application v %s" % (app_version,),
    )

    c_analyze_files = dict(
        description="Analyzes input files against supplied memories",
        script="./analyze_files.py",
        dest_base="analyze_files",
        version=app_version,
        name="analyze_files Application v %s" % (app_version,),
    )

    windows_apps = [analyze_assist, show_logs]
    console_apps = [c_extract_segments, c_analyze_files]

    for app_dict in windows_apps + console_apps:
        app_dict.update(base_info)

    setup_dict['windows'] = windows_apps
    setup_dict['console'] = console_apps

    excludes = ["pywin", "pywin.debugger", "pywin.debugger.dbgcon",
                "pywin.dialogs", "pywin.dialogs.list", "win32com.server",
                "email"]

    packages = ["lxml"]

    options = dict(optimize=2,
                   dist_dir=app_name,
                   excludes=excludes,
                   packages=packages,
                   dll_excludes=["POWRPROF.dll"])

    setup_dict['options'] = {"py2exe": options}

    return setup_dict


def add_data_files(setup_dict):
    setup_dict['data_files'] = [
        ("res", glob.glob("./res/*.*")),
        ("res/img", glob.glob("./res/img/*.*")),
        (".", ["extensions.txt",
               "pdflib_license.txt",
               "segrules.txt",
               "match_ranges.txt",
               "MITLicense.txt",
               "MITLicenseJ.txt",
               "%s/gdiplus.dll" % WX_DIR,
               r"D:\dev\python\MemoryServes\MemoryServes/MSVCP90.dll",
               r"D:\dev\python\MemoryServes\MemoryServes/MSVCR90.DLL"]),
    ]
    return setup_dict


def patch_module_finder():
    """ModuleFinder can't handle runtime changes to __path__,
    but win32com uses them"""

    try:
        # if this doesn't work, try import modulefinder
        import py2exe.mf as modulefinder
        import win32com

        for p in win32com.__path__[1:]:
            modulefinder.AddPackagePath("win32com", p)
        for extra in ["win32com.shell"]:  #,"win32com.mapi"
            __import__(extra)
            m = sys.modules[extra]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(extra, p)
    except ImportError:
        print "no build path setup, no worries."
        pass


def setup_main():
    patch_module_finder()

    if '__file__' in globals():
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # If run without args, build executables, in quiet mode.
    if len(sys.argv) == 1:
        sys.argv.append("py2exe")
        sys.argv.append("-q")
    """Run setup when called as main"""

    start_time = time.time()

    setup_dict = get_setup_dict("./main.py", "AnalyzeAssist")
    setup_dict = add_data_files(setup_dict)

    clean_dir('build')
    clean_dir("AnalyzeAssist")

    print "Creating exe..."
    setup(
        **setup_dict
    )

    copytree("help", "AnalyzeAssist/help")
    clean_dir('build')

    print
    print "=" * 30
    print "exe created in", time.time() - start_time, "seconds"
    print "=" * 30
    print


if __name__ == '__main__':
    setup_main()
