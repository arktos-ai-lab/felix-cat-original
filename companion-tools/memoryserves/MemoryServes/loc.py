#coding: UTF8
"""
Locations used by app

"""

import os
import sys
import winpaths
import glob
import shutil

MODULE_NAME = u"MemoryServes"

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")

# module_path
def module_path(filename=None):
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""

    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable,
                                       sys.getfilesystemencoding()))

    if not filename:
        filename = __file__
    return os.path.abspath(os.path.dirname(unicode(filename,
                                   sys.getfilesystemencoding())))

def get_local_app_data_folder():
    """
    First see if there's a MemoryServes directory in
    the Common App Data folder.
    If there is, return it.
    If not, return the Local App Data directory
    """

    common = winpaths.get_common_appdata()
    datafolder = os.path.join(common, MODULE_NAME)
    if os.path.isdir(datafolder):
        return datafolder
    app_data = winpaths.get_local_appdata()
    return os.path.join(app_data, MODULE_NAME)

def get_ms_dir(*folders):
    """
    Get a subdirectory of the Memory Serves
    app data directory
    """

    if not we_are_frozen():
        basepath = module_path()
    else:
        basepath = get_local_app_data_folder()

    fullpath = os.path.join(basepath, *folders)
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)
        
    return fullpath

def get_media_dir():
    """
    The directory for "media", i.e. static files
    """
    return get_ms_dir("media")

def get_log_file(filename):
    """
    Get the log file at the proper path
    """
    return os.path.join(get_ms_dir(), filename)

def get_log_file_text(filename):
    return open(get_log_file(filename)).read()

def ensure_res_dir(dirname):
    """
    Make sure that we have directory dirname, with the needed files.
    This will be missing if a different user installed the program
    locally, e.g. when an admin needs to install software.

    If the directory is missing, create it, and copy over the files from
    the Program Files directory.
    """

    directory = os.path.join(get_local_app_data_folder(), dirname)
    glob_query = os.path.join(directory, "*.*")
    if not glob.glob(glob_query):
        if os.path.isdir(directory):
            os.rmdir(directory)
        source_dir = os.path.join(module_path(), dirname)
        shutil.copytree(source_dir, directory)

def ensure_resource_files():
    """
    Make sure that we have the required resource files
    """
    ensure_res_dir("templates")
    ensure_res_dir("media")

def get_data_file(filename="data.db"):
    """
    Get the name of the MemoryServes/data dir
    """
    return os.path.join(get_ms_dir("data"), filename)

def get_template_dir():
    """
    Get the name of the templates dir in the data dir
    """
    return get_ms_dir("templates")

def get_module_dir():
    """
    Get the name of the modules dir from the data dir
    """
    return get_ms_dir("modules")
