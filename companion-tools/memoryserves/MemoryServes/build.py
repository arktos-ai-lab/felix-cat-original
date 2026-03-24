#coding: UTF8
"""
Setup program for Memory Serves

Uses py2exe to build a stand-alone executable.

"""
from __future__ import with_statement

from distutils.core import setup
import sys
import time
import os
import subprocess
import shutil
import modulefinder
import logging
from datetime import date

import py2exe

import main
import ClearUsers
import MemoryImporter
import sign_and_upload_exe as sign

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

BASEDIR = os.path.dirname(os.path.abspath(__file__))
MANUAL_DIR = os.path.join(BASEDIR, "media", "manual")
DATA_DIR = os.path.join(BASEDIR, "build_data")
VERSION = main.__version__
NAME = main.__progname__


def make_version_file(data):
    """
    Write the version file with our version data
    """
    logger.debug("Writing version file")
    out = open("msversion.txt", "w")
    for pair in data.items():
        out.write("%s=%s\n" % pair)
    out.close()


def make_setup_script(context):
    """
    Create the Inno setup script from our template
    """
    logger.debug("Creating the setup script for Inno Setup")
    text = open("MemoryServes.tpl").read()
    with open("MemoryServes.iss", "w") as out:
        out.write(text % context)


def build_installer():
    """
    Builds the installer by calling a .bat file
    """
    logger.debug("Building installer...")
    os.chdir(BASEDIR)

    filename = "MemoryServes_Setup_%s.exe" % VERSION
    context = dict(version=VERSION,
                   filename=filename,
                   build_date=str(date.today()))

    make_version_file(context)
    make_setup_script(context)

    logger.debug("Building setup file...")
    subprocess.call("buildinstaller.bat")
    logger.debug("Finished building setup file!")

    sign.sign_exe(r"Setup\%s" % filename)

    installer_source = "Setup/%s" % filename
    logger.debug("Copying Setup File")

    installer_dest = r"d:\dev\shared\MemoryServes_Setup.exe"
    shutil.copy(installer_source, installer_dest)
    logger.debug("... Copy finished")


def clean_dir(dir_name):
    """
    Remove all prior fields from the dist (dir_name) directory
    """

    logger.debug("Cleanging directory %s" % dir_name)

    if not os.path.exists(dir_name):
        logger.debug("%s does not exist. Skipping." % dir_name)
        return

    shutil.rmtree(dir_name)


class MemoryServesTarget(object):
    """
    The target class for the Memory Serves app
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = VERSION
        self.company_name = "Ginstrom IT Solutions (GITS)"
        self.copyright = "(C) Ginstrom IT Solutions"
        self.name = NAME


class ClearUsersTarget(object):
    """
    The target class for the ClearUsers app
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = ClearUsers.__version__
        self.company_name = "Ginstrom IT Solutions (GITS)"
        self.copyright = "(C) Ginstrom IT Solutions"
        self.name = ClearUsers.__progname__


def get_setup_dict(script, name, version=VERSION):
    """Create a dictionary to pass to setup"""

    comp_name = ''.join(name.split())

    setup_dict = {}

    base_info = get_base_info()

    memory_serves = MemoryServesTarget(
        description="Server for networked access to Felix memories",
        script=script,
        icon_resources=[(1, "./media/MemoryServes.ico")],
        dest_base=comp_name,
        version=version,
        uac_info="requireAdministrator",
        name="%s Application v %s" % (name, version),
        **base_info
    )

    clear_users = ClearUsersTarget(
        description="Clear users from Memory Serves",
        script="ClearUsers.py",
        dest_base="ClearUsers",
        version=ClearUsers.__version__,
        uac_info="requireAdministrator",
        name="Clear Users Application v %s" % ClearUsers.__version__,
        **base_info
    )

    mi_version = MemoryImporter.__version__
    memory_importer = dict(
        description="Imports memories into Memory Serves database",
        script="MemoryImporter.py",
        dest_base="MemoryImporter",
        version=MemoryImporter.__version__,
        uac_info="requireAdministrator",
        name="MemoryImporter Application v %s" % mi_version,
    )
    memory_importer.update(base_info)

    windows_apps = [memory_serves, clear_users, memory_importer]
    console_apps = []

    setup_dict['windows'] = windows_apps
    setup_dict['console'] = console_apps

    excludes = ["pywin",
                "pywin.debugger",
                "pywin.debugger.dbgcon",
                "pywin.dialogs",
                "pywin.dialogs.list",
                "Tkinter",
                "win32ui",
                "tcl"]
    packages = ["email",
                "lxml",
                "mako.cache",
                "sqlalchemy",
                "edist"]

    options = dict(optimize=2,
                   dist_dir=comp_name,
                   excludes=excludes,
                   packages=packages,
                   dll_excludes=["POWRPROF.dll", "MSVCP90.dll"])

    setup_dict['options'] = {"py2exe": options}

    return setup_dict


def get_base_info():
    """
    Returns the basic info common to all apps.
    """
    return {"company_name": "Ginstrom IT Solutions (GITS)",
            "copyright": "(C) Ginstrom IT Solutions (GITS)",
            "author": "Ginstrom IT Solutions (GITS)",
            "author_email": "support@felix-cat.com"}


def add_data_files(setup_dict):
    """
    Add the various non-exe files (dlls, license files)
    """

    logger.debug("Adding data files to exe folder. Data dir is %s" % DATA_DIR)
    setup_dict['data_files'] = [
        (".", ["MITLicense.txt",
               "MITLicenseJ.txt",
               os.path.join(DATA_DIR, "MSVCR90.DLL"),
               os.path.join(DATA_DIR, "MSVCP90.dll"),
               os.path.join(DATA_DIR, "gdiplus.dll")])]
    return setup_dict


def build_docs():
    """
    Builds the app documentation.
    """

    logger.debug("Building docs...")
    os.chdir(os.path.join(BASEDIR, "docs"))
    subprocess.call("make html")
    shutil.copytree('build/html', MANUAL_DIR)
    logger.debug("Finished building docs!")


def clean_up_dirs():
    """
    Cleans build directories from the last run. Frees them up for the current build.
    """

    clean_dir(os.path.join(BASEDIR, 'build'))
    clean_dir(os.path.join(BASEDIR, ''.join(NAME.split())))
    clean_dir(os.path.join(BASEDIR, 'media', 'manual'))


def make():
    """
    When scripted called as main
    """

    logger.info("Running make script")
    start_time = time.time()

    setup_dict = get_setup_dict(script="./main.py",
                                name=NAME)

    setup_dict = add_data_files(setup_dict)
    clean_up_dirs()

    logger.debug("Creating exe")
    setup(**setup_dict)

    clean_dir('build')
    sign.sign_exe(r"MemoryServes\MemoryServes.exe")

    logger.info("exe created in %s seconds" % (time.time() - start_time))

    build_docs()
    build_installer()


if __name__ == '__main__':  # pragma no cover
    os.chdir(BASEDIR)

    # If run without args, build executables, in quiet mode.
    if len(sys.argv) == 1:
        sys.argv.append("py2exe")
        sys.argv.append("-q")
    make()
