#coding: UTF8
"""
The segmenter package

This package is responsible for splitting files in various formats into segments
for further processing.

"""
import logging

import excelseg
import htmlseg
import pptseg
import rtfseg
import textseg
import wordseg
import xmlseg
import openofficeseg
import os
from collections import defaultdict
from AppUtils import module_path, get_local_app_data_folder
import pywintypes
import win32api
import shutil

LOGGER = logging.getLogger(__name__)


def getFileExtension(pathname):
    """Gets the file extension for pathname"""

    base,ext = os.path.splitext(pathname)

    if ext:
        return "*" + ext.lower()
    return ""

SEGMENTER_CLASSES = dict(WordFiles= wordseg.Segmenter,
                         TextFiles=textseg.Segmenter,
                         PptFiles=pptseg.Segmenter,
                         HtmlFiles=htmlseg.Segmenter,
                         RtfFiles=rtfseg.Segmenter,
                         ExcelFiles=excelseg.Segmenter,
                         XmlFiles=xmlseg.Segmenter,
                         OpenOfficeFiles=openofficeseg.Segmenter)

def get_segmenter_class_names():
    """Get a mapping of segmenter engine names to segmenter classes

    The names come from our config file.
    """

    return SEGMENTER_CLASSES

def getSegClassNames():
    """Retrieves the dictionary mapping segmenter class
    names to classes
    """

    klasses = SEGMENTER_CLASSES

    return dict((str(klass()), klass) for key, klass in klasses.items())

def parseExtensionDefLine(line):
    """Parses an extension file line into key and value pair"""

    key,vals = line.split("=")
    return (key.strip(), vals.strip())


def getExtensionsFileName():
    """Retrieves the name of the extensions config file."""

    filename = os.path.join(get_local_app_data_folder(), "extensions.txt")
    if not os.path.exists(filename):
        modfile = os.path.join(module_path(), "extensions.txt")
        if os.path.exists(modfile):
            shutil.copy(modfile, filename)
    return filename


def writeSegClassLine(output, key, val):
    """Writes a line to the seg class file.
    Format is [key = val]
    """

    print >>output, "%s = %s" % (key,val)


def writeSegClassLines(io, classLines):
    """Writes the dictionary of class description strings to the provided file object.

    @param io: file-like object for writing extension definitions to
    @param classLines: dictionary of class names to extensions

    Writes the file in the format used in the help files.

    The classnames are the names you get when you do str(klassName()).
    """

    segClasses = SEGMENTER_CLASSES

    lookup = {}
    for key,klass in segClasses.items():
        lookup[str(klass())] = key

    for klassName,vals in classLines.items():
        key = lookup[klassName]
        writeSegClassLine(io, key, vals)


def writeExtensionsFile(handlers):
    """Writes extensions to config file.

    Reacts to a broadcast that extension handlers have changed
    (from options dialog), and writes the new extensions to the
    config text file.
    """

    filename = getExtensionsFileName()

    write_extensions_file(handlers, filename)

def write_extensions_file(handlers, filename):
    LOGGER.debug(u"Writing extensions to file %s" % filename)

    outfile = open(filename, "w")
    writeSegClassLines(outfile, handlers)
    outfile.close()


def getNamesAndExtensions():
    """Retrieves the names and extensions from the extensions.txt file."""


    defaults = """XmlFiles = *.xml;*.ftm;*.fgloss
WordFiles = *.doc;*.rtf;*.docx
TextFiles = *.txt
ExcelFiles = *.xls;*.csv;*.xlsx
HtmlFiles = *.html;*.htm;*.shtml;*.mht
PptFiles = *.ppt;*.pptx
OpenOfficeFiles = *.odt;*.ods;*.odp"""

    extension_mapping = parse_extension_def_lines(defaults.splitlines())


    filename = getExtensionsFileName()

    lines = open(filename,"r")

    extension_mapping.update(parse_extension_def_lines(lines))

    return extension_mapping

def parse_extension_def_lines(lines):

    names = {}

    for line in lines:
        key,vals = parseExtensionDefLine(line)
        names[key] = vals

    return names

def getMapping():
    """Get the mapping of extensions to segmenter types
    from the file extensions.txt"""

    extension_mapping = {}

    klasses = get_segmenter_class_names()
    extensions = getNamesAndExtensions()

    for key, vals in extensions.items():
        for val in vals.split(";"):
            extension_mapping[val.strip()] = klasses[key]

    return extension_mapping

def get_associated_exe(filename):
    try:
        _, exename = win32api.FindExecutable(filename)
        return os.path.split(exename)[-1]
    except pywintypes.error, details:
        LOGGER.warn(u"Failed to get executable for %s : %s" % (filename, details))
    return None

def getSegmenterClass(filename):

    if is_url(filename):
        return htmlseg.Segmenter

    mapping = getMapping()
    ext = getFileExtension(filename)
    klass = mapping.get(ext)
    if klass:
        return klass
    assoc_exe = get_associated_exe(os.path.abspath(filename))
    if assoc_exe:
        if "winword" in assoc_exe.lower():
            return SEGMENTER_CLASSES["WordFiles"]
        elif "excel" in assoc_exe.lower():
            return SEGMENTER_CLASSES["ExcelFiles"]
        elif "powerpnt" in assoc_exe.lower():
            return SEGMENTER_CLASSES["PptFiles"]
    return SEGMENTER_CLASSES["TextFiles"]

def is_url(filename):
    return filename.lower().startswith("http")

def getSegmenterClasses(filenames):
    """
    Gets segmenters for the specified filenames.

    Creates a dictionary of SegmenterClass -> [files],
    mapping each file to the segmenter class that will segment it

    @param files: a list of file names

    @return: a dictionary of SegmenterClass -> [files]
    """

    segmenter_classes = defaultdict(list)

    for filename in filenames:
        SegmenterClass = getSegmenterClass(filename)

        if SegmenterClass:
            segmenter_classes[SegmenterClass].append(filename)

    return segmenter_classes
