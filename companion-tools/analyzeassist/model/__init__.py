# coding: UTF8
"""
Model package for AnalyzeAssist app

"""

import os
import cPickle
import logging

from AnalyzeAssist import broadcaster
from AnalyzeAssist.AppUtils import get_data_folder
import wx
from wx import Locale


VERSION = "1.5"
PREF_FILENAME = "prefs.database"
STRINGS_FILENAME = "stringres.database"
DEFAULT_GUI_LANGUAGE = "English"
LOGGER = logging.getLogger(__name__)


def load(fname):
    """
    Loads a picked object from fname
    returns None if the file is empty.

    Will raise IOError if the file doesn't exist

    @param fname: Name of file to load
    """

    full_path = os.path.join(get_data_folder(), fname)

    try:
        database = open(full_path, "r")
        obj = cPickle.load(database)
        database.close()
        return obj
    except EOFError:
        LOGGER.exception("Error loading pickle object")

        return None


def serialize(obj, fname):
    """Serialize obj to fname using cPickle

    @param obj: The object to serialize
    @param fname: The name of the file to serialize it to
    """

    full_path = os.path.join(get_data_folder(), fname)

    database = open(full_path, "w")
    cPickle.dump(obj, database)
    database.close()


def save_preferences(prefs):
    serialize(prefs, PREF_FILENAME)


def get_language():
    """Retrieves the current preferred language"""

    return language.language


def on_japanese():
    """Responds to command to turn GUI to Japanese"""

    language.change_language("Japanese")


def on_english():
    """Responds to command to turn GUI to English"""

    language.change_language("English")


def get_default_prefs():
    defaults = {"language": DEFAULT_GUI_LANGUAGE,
                "stop chars": u".!?。．！？" + unichr(0x133) + unichr(0x8230),
                "recurse subdirs": False,
                "count numbers": True,
                "fuzzy options": {}}
    defaults.update(dict(check_updates=True,
                         ask_about_updates=True,
                         last_update_check=None,
                         check_interval=14))
    defaults["html_seg_options"] = dict(want_a_title=True,
                                        want_img_alt=True,
                                        want_input_value=True,
                                        want_meta_description=True,
                                        want_meta_keywords=True)
    return defaults


def get_preferences():
    """
    Get application prefrences
    """

    prefs = get_default_prefs()

    try:
        prefs.update(load(PREF_FILENAME))
        if not prefs["fuzzy options"]:
            prefs["fuzzy options"] = {}
    except IOError:
        LOGGER.exception("Failure loading preferences")
    finally:
        return prefs


def set_preference(key, val):
    prefs = get_preferences()
    LOGGER.debug("Setting preference %s from '%s' to '%s'", key, prefs.get(key), val)
    prefs[key] = val
    save_preferences(prefs)


# html_seg_options
def get_html_seg_options():
    prefs = get_preferences()
    return prefs["html_seg_options"]


def set_html_seg_options(options):
    set_preference("html_seg_options", options)


# analyze_numbers
def get_analyze_numbers():
    """Get analyze_numbers preference
    """

    prefs = get_preferences()
    return prefs.get("analyze numbers")


def set_analyze_numbers(analyze_numbers):
    """Set analyze_numbers preference"""

    set_preference("analyze numbers", analyze_numbers)


# fuzzy_options
def get_fuzzy_options():
    """Retrieves the fuzzy options from the preferences
    """

    prefs = get_preferences()
    return prefs["fuzzy options"]


def set_fuzzy_options(options):
    set_preference("fuzzy options", options)


def set_last_update(last_update):
    set_preference("last_update_check", last_update)


#############################
# Language setting
#############################


class Language(object):
    """This class handles string localization in the application"""

    def __init__(self, dbname=STRINGS_FILENAME):
        """
        @param dbname: Name of string database
        """

        self.path = get_data_folder()
        self.language = DEFAULT_GUI_LANGUAGE
        self.trans = {}

        self.set_preferred_language()
        self.load_translations(dbname)

    def set_preferred_language(self):

        system_language = Locale.GetSystemLanguage()
        if system_language == wx.LANGUAGE_JAPANESE:
            default = "Japanese"
        else:
            default = "English"

        self.language = get_preferences().get("language", default)

    def load_translations(self, dbname):
        """Load translations from database file"""

        try:
            self.dbname = os.path.join(self.path, dbname)
            self.trans = load(self.dbname)

        except IOError:
            log_err("Failed to load translation database")

    def get_translation(self, msgid):
        """Retrieve translation for msgid from the database

        @param msgid: A string to be translated
        """

        key = unicode(msgid)
        term = self.trans.get(key)
        if not term:
            return key

        if self.language == 'English':
            return term['en']
        return term['ja']

    def on_shutdown(self):
        """Reacts to shutdown broadcast by serializing the language
        preference
        """
        set_preference("language", self.language)

    def change_language(self, language):
        self.language = language
        LOGGER.debug(u"Language changed to %s", self.language)
        set_preference("language", language)
        broadcaster.Broadcast('language', 'changed')


language = Language()
# Install _ in the builtins
_ = language.get_translation
