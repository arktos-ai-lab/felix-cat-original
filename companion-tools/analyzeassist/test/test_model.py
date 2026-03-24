# coding: UTF8
"""
Unit test the model package

"""

from nose.tools import raises
from AnalyzeAssist import model
import os

_ = model._

@raises(AssertionError)  # Ensure that the unit tests are running on this module...
def test_module():
    assert False


def test_load():
    dir = os.path.dirname(__file__)
    fname = os.path.join(dir, "prefs.database")
    prefs = model.load(fname)
    print prefs
    analyze_nums = prefs.get("analyze numbers")
    assert analyze_nums == True or analyze_nums == False
    fuzzy_options = prefs.get("fuzzy options")
    assert fuzzy_options


class TestLanguage:
    def setup(self):
        self.old_trans = model.language.trans
        self.old_language = model.language.language

    def teardown(self):
        model.language.trans = self.old_trans
        model.language.language = self.old_language

    def test_nonexistent(self):
        trans = model.language.get_translation("nonexistent string")
        assert trans == u"nonexistent string", trans

    def test_english(self):
        model.language.trans = dict(foo={'en': 'foo', 'ja': 'bar'},
                                    bar={'en': 'spam', 'ja': 'eggs'})

        model.language.language = "English"
        trans = model.language.get_translation("foo")
        assert trans == u"foo", trans

    def test_japanese(self):
        model.language.trans = dict(foo={'en': u'foo', 'ja': u'日本語'},
                                    bar={'en': u'spam', 'ja': u'eggs'})

        model.language.language = "Japanese"
        trans = model.language.get_translation("foo")
        assert trans == u"日本語", trans

    def test_Asian(self):
        asian = _("Asian")

        assert isinstance(asian, unicode)


def test_analyze_numbers():
    model.set_analyze_numbers(False)
    analyze_numbers = model.get_analyze_numbers()
    assert not analyze_numbers

    model.set_analyze_numbers(True)
    analyze_numbers = model.get_analyze_numbers()
    assert analyze_numbers

    model.set_analyze_numbers(False)
    analyze_numbers = model.get_analyze_numbers()
    assert not analyze_numbers


def test_analyze_numbers_with_broadcaster():
    old_an = model.get_analyze_numbers()

    model.set_analyze_numbers(False)
    analyze_numbers = model.get_analyze_numbers()
    assert not analyze_numbers

    model.set_analyze_numbers(True)
    analyze_numbers = model.get_analyze_numbers()
    assert analyze_numbers

    model.set_analyze_numbers(False)
    analyze_numbers = model.get_analyze_numbers()
    assert not analyze_numbers

    model.set_analyze_numbers(old_an)


class TestNomatchExtension:
    def setup(self):
        self.oldextension = model.get_fuzzy_options()

    def teardown(self):
        model.set_fuzzy_options(self.oldextension)

    def test_extension(self):
        model.set_fuzzy_options(dict(a=1))
        extension = model.get_fuzzy_options()
        assert extension == dict(a=1), extension

    def test_extension_ii(self):
        model.set_fuzzy_options(dict(a=2))
        extension = model.get_fuzzy_options()
        assert extension == dict(a=2), extension


def test_get_preferences():
    prefs = model.get_preferences()

    keys = ["language", "stop chars",
            "recurse subdirs", "count numbers",
            "check_updates", "ask_about_updates",
            "last_update_check"]
    for key in keys:
        assert key in prefs, (key, prefs)


def test_set_preferences():
    oldprefs = model.get_preferences()

    if "a" in oldprefs:
        del oldprefs["a"]
        model.serialize(oldprefs, model.PREF_FILENAME)
    if "b" in oldprefs:
        del oldprefs["b"]
        model.serialize(oldprefs, model.PREF_FILENAME)

    model.set_preference("a", 1)
    model.set_preference("b", 2)

    newprefs = model.get_preferences()

    assert newprefs['a'] == 1, newprefs
    assert newprefs['b'] == 2, newprefs

    model.save_preferences(oldprefs)


class TestSetPreference:
    def setup(self):
        prefs = model.get_preferences()
        if "foo" in prefs:
            del prefs["foo"]
            model.serialize(prefs, model.PREF_FILENAME)

    def teardown(self):
        prefs = model.get_preferences()
        if "foo" in prefs:
            del prefs["foo"]
            model.serialize(prefs, model.PREF_FILENAME)

    def test_init(self):
        assert "foo" not in model.get_preferences()

    def test_foo(self):
        model.set_preference("foo", "bar")
        prefs = model.get_preferences()
        assert prefs["foo"] == "bar", prefs


