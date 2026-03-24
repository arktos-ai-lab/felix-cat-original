#coding: UTF8
"""
Enter module description here.

"""

import unittest
import socket

import mock

from .. import loc
from .. import settings


class TestNormalizer(unittest.TestCase):
    def setUp(self):
        self.old_normalizer = settings.normalize

    def tearDown(self):
        settings.normalize = self.old_normalizer

    def test_plain(self):
        normalizer = settings.make_normalizer({})
        val = normalizer(u"SPAM")
        assert val == u"SPAM", val

    def test_plain_html(self):
        normalizer = settings.make_normalizer({})
        val = normalizer(u"<strong>SPAM</strong>")
        assert val == u"SPAM", val

    def test_case(self):
        normalizer = settings.make_normalizer(dict(normalize_case=True))
        val = normalizer(u"SPAM")
        assert val == u"spam", val

    def test_width_numbers(self):
        normalizer = settings.make_normalizer(dict(normalize_width=True))
        val = normalizer(u"１２３")
        assert val == u"123", val

    def test_width_letters(self):
        normalizer = settings.make_normalizer(dict(normalize_width=True))
        val = normalizer(u"ＡＢＣ")
        assert val == u"ABC", val

    def test_width_and_case_letters(self):
        normalizer = settings.make_normalizer(dict(normalize_case=True,
                                                   normalize_width=True))
        val = normalizer(u"ＡＢＣ")
        assert val == u"abc", val

    def test_width_katakana(self):
        normalizer = settings.make_normalizer(dict(normalize_width=True))
        val = normalizer(u"ｶｷｸ")
        assert val == u"カキク", val

    def test_hira_hira(self):
        normalizer = settings.make_normalizer(dict(normalize_hira=True))
        val = normalizer(u"あいうえお")
        assert val == u"アイウエオ", val.encode("utf-8")

    def test_hira_kata(self):
        normalizer = settings.make_normalizer(dict(normalize_hira=True))
        val = normalizer(u"ぴーす")
        assert val == u"ピース", val.encode("utf-8")

    def test_hira_and_width(self):
        normalizer = settings.make_normalizer(dict(normalize_width=True,
                                                   normalize_hira=True))
        val = normalizer(u"ｶｷｸﾞかきぐ")
        assert val == u"カキグカキグ", val.encode("utf-8")


class TestGetLocalConfig(unittest.TestCase):
    def test_favicon(self):
        config = settings.get_local_config()
        favicon = config['/favicon.ico']
        assert favicon['tools.staticfile.on']
        filename = favicon['tools.staticfile.filename'].lower()
        expected = r"d:\dev\python\MemoryServes\MemoryServes\media\favicon.ico".lower()
        print expected
        assert filename == expected, filename

    def test_media(self):
        config = settings.get_local_config()
        media = config['/media']
        assert media['tools.staticdir.on']
        dirname = media['tools.staticdir.dir'].lower()
        expected = r"d:\dev\python\MemoryServes\MemoryServes\media".lower()
        print expected
        assert dirname == expected, dirname


class TestGetGlobalConfig(unittest.TestCase):
    def setUp(self):
        self.old_waf = loc.we_are_frozen

    def tearDown(self):
        loc.we_are_frozen = self.old_waf

    def test_not_frozen(self):
        config = settings.get_global_config()
        assert config["global"]["log.screen"], config

    def test_frozen(self):
        loc.we_are_frozen = lambda: True
        config = settings.get_global_config()
        assert not config["global"]["log.screen"], config
        assert config["global"]['log.access_file'].endswith("access.log"), config


class TestGetPrefs(unittest.TestCase):
    def setUp(self):
        self.old_getter = settings._get_prefs_filename

    def tearDown(self):
        settings._get_prefs_filename = self.old_getter

    def test_normal(self):
        prefs = settings.get_prefs()
        for key in "normalize_case normalize_hira normalize_width".split():
            assert key in prefs, prefs

    def test_bogus_file(self):
        settings._get_prefs_filename = lambda: "c:\\does_not_exist.txt"
        prefs = settings.get_prefs()
        expected = {'normalize_hira': True,
                    'show_systray_icon': True,
                    'normalize_case': True,
                    'normalize_width': True}
        for key, val in expected.items():
            assert expected[key] == prefs[key], (key, expected[key], prefs[key])


class TestSerializationPrefs(unittest.TestCase):
    def test_serialize(self):
        old_prefs = settings.get_prefs()
        try:
            settings.serialize_prefs({"spam": "egg"})
            new_prefs = settings.get_prefs()
            assert new_prefs["spam"] == "egg", new_prefs
            for key in old_prefs.keys():
                assert new_prefs[key] == new_prefs[key], (new_prefs[key], old_prefs[key])
        finally:
            settings.serialize_prefs(old_prefs)


class TestGetWeb(unittest.TestCase):
    def test_get_host(self):
        host = settings.get_host()
        expected = socket.gethostbyname(socket.gethostname())
        assert host == expected, (host, expected)

    def test_get_port(self):
        port = settings.get_port()
        assert port == settings.Settings.PORT, port


class TestGetCommandLineConfig(unittest.TestCase):
    """
    Tests for `get_command_line_config` function.
    """
    def test_port(self):
        settings.Settings.PORT = 1
        options = settings.get_command_line_config(settings.get_get_config(), "--port 9500".split())
        settings.reflect_command_line_options(options)
        assert settings.Settings.PORT == 9500, settings.Settings

    def test_threads(self):
        settings.Settings.NUM_THREADS = 1
        options = settings.get_command_line_config(settings.get_get_config(), "--threads 10".split())
        settings.reflect_command_line_options(options)
        assert settings.Settings.NUM_THREADS == 10, settings.Settings

    def test_echo(self):
        with mock.patch("MemoryServes.settings.pprint") as mpprint:
            options = settings.get_command_line_config(settings.get_get_config(), ["--echo-settings"])
            settings.reflect_command_line_options(options)
            mpprint.pprint.assert_called_once_with(settings.Settings.PREFERENCES)


