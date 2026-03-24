# coding: UTF8
"""
Unit tests for loc module.
"""

import unittest

import os
from .. import loc


class TestGetFakedDirs(unittest.TestCase):
    def setUp(self):
        self.old_isdir = loc.os.path.isdir
        self.old_common = loc.winpaths.get_common_appdata
        self.old_local = loc.winpaths.get_local_appdata
        self.old_get_local_app_data_folder = loc.get_local_app_data_folder

        self.fullpath = None

        self.old_we_are_frozen = loc.we_are_frozen
        self.old_module_path = loc.module_path
        self.old_get_local_app_data_folder = loc.get_local_app_data_folder
        self.old_makedirs = loc.os.makedirs

    def tearDown(self):
        loc.os.path.isdir = self.old_isdir
        loc.winpaths.get_common_appdata = self.old_common
        loc.winpaths.get_local_appdata = self.old_local

        loc.we_are_frozen = self.old_we_are_frozen
        loc.module_path = self.old_module_path
        loc.get_local_app_data_folder = self.old_get_local_app_data_folder

        loc.os.makedirs = self.old_makedirs
        loc.get_local_app_data_folder = self.old_get_local_app_data_folder

    def makedirs(self, fullpath):
        self.fullpath = fullpath

    def test_get_local_app_data_folder_common(self):
        loc.os.path.isdir = lambda x: True
        loc.winpaths.get_common_appdata = lambda: "c:\\common"

        actual = loc.get_local_app_data_folder()
        assert actual == "c:\\common\\MemoryServes", actual

    def test_get_local_app_data_folder_local(self):
        loc.os.path.isdir = lambda x: False
        loc.winpaths.get_local_appdata = lambda: "c:\\local"

        actual = loc.get_local_app_data_folder()
        assert actual == "c:\\local\\MemoryServes", actual

    def test_get_ms_dir_not_frozen_exists(self):
        loc.we_are_frozen = lambda: False
        loc.os.path.isdir = lambda x: True
        loc.module_path = lambda: "c:\\module"
        fullpath = loc.get_ms_dir("test", "ms")
        assert not self.fullpath, self.fullpath
        assert fullpath == "c:\\module\\test\\ms", fullpath

    def test_get_ms_dir_frozen_exists(self):
        loc.we_are_frozen = lambda: True
        loc.os.path.isdir = lambda x: True
        loc.get_local_app_data_folder = lambda: "c:\\local"
        fullpath = loc.get_ms_dir("test", "ms")
        assert not self.fullpath, self.fullpath
        assert fullpath == "c:\\local\\test\\ms", fullpath

    def test_get_ms_dir_not_frozen_doesnt_exist(self):
        loc.we_are_frozen = lambda: False
        loc.os.path.isdir = lambda x: False
        loc.os.makedirs = self.makedirs
        loc.module_path = lambda: "c:\\module"
        fullpath = loc.get_ms_dir("test", "ms")
        assert self.fullpath == fullpath, (fullpath, self.fullpath)
        assert fullpath == "c:\\module\\test\\ms", fullpath

    def test_get_ms_dir_frozen_doesnt_exist(self):
        loc.we_are_frozen = lambda: True
        loc.os.path.isdir = lambda x: False
        loc.get_local_app_data_folder = lambda: "c:\\local"
        loc.os.makedirs = self.makedirs
        fullpath = loc.get_ms_dir("test", "ms")
        assert self.fullpath == fullpath, (fullpath, self.fullpath)
        assert fullpath == "c:\\local\\test\\ms", fullpath


class TestGetDir(unittest.TestCase):
    def test_media(self):
        dirname = loc.get_media_dir().lower()

        assert os.path.exists(dirname)
        assert os.path.isdir(dirname)
        expected = r"D:\dev\python\MemoryServes\MemoryServes\media".lower()
        assert dirname == expected, dirname

    def test_log(self):
        filename = loc.get_log_file("log.txt").lower()
        expected = r"D:\dev\python\MemoryServes\MemoryServes\log.txt".lower()

        assert filename == expected, filename

    def test_errlog(self):
        filename = loc.get_log_file("err_log.txt").lower()

        assert not os.path.isdir(filename)
        expected = r"D:\dev\python\MemoryServes\MemoryServes\err_log.txt".lower()
        assert filename == expected, filename

    def test_data(self):
        filename = loc.get_data_file().lower()

        assert not os.path.isdir(filename)
        expected = r"D:\dev\python\MemoryServes\MemoryServes\data\data.db".lower()
        assert filename == expected, filename

    def test_template(self):
        dirname = loc.get_template_dir().lower()

        assert os.path.exists(dirname)
        assert os.path.isdir(dirname)
        expected = r"D:\dev\python\MemoryServes\MemoryServes\templates".lower()
        assert dirname == expected, dirname

    def test_module(self):
        dirname = loc.get_module_dir().lower()

        assert os.path.exists(dirname)
        assert os.path.isdir(dirname)
        expected = r"d:\dev\python\MemoryServes\MemoryServes\modules".lower()
        assert dirname == expected, dirname


class TestGetModulePath(unittest.TestCase):
    def setUp(self):
        self._old_frozen = loc.we_are_frozen

    def tearDown(self):
        loc.we_are_frozen = self._old_frozen

    def test_plain(self):
        assert loc.module_path().lower() == r"d:\dev\python\MemoryServes\MemoryServes".lower(), loc.module_path()

    def test_frozen(self):
        loc.we_are_frozen = lambda: True
        assert loc.module_path().lower() == r"D:\dev\python\MemoryServes\venv\Scripts".lower(), loc.module_path()


class TestGetDirFrozen(unittest.TestCase):
    def setUp(self):
        self._old_frozen = loc.we_are_frozen
        loc.we_are_frozen = lambda: True

    def tearDown(self):
        loc.we_are_frozen = self._old_frozen

    def test_log(self):
        filename = loc.get_log_file("log.txt").lower()
        expected1 = r"d:\Users\Ryan\AppData\Local\MemoryServes\log.txt".lower()
        expected2 = r"d:\ProgramData\MemoryServes\log.txt".lower()
        assert filename == expected1 or filename == expected2, filename

    def test_errlog(self):
        filename = loc.get_log_file("err_log.txt").lower()

        assert not os.path.isdir(filename)
        expected1 = r"d:\Users\Ryan\AppData\Local\MemoryServes\err_log.txt".lower()
        expected2 = r"d:\ProgramData\MemoryServes\err_log.txt".lower()
        assert filename == expected1 or filename == expected2, filename

    def test_media(self):
        dirname = loc.get_media_dir().lower()

        assert os.path.exists(dirname)
        assert os.path.isdir(dirname)
        expected1 = r"d:\Users\Ryan\AppData\Local\MemoryServes\media".lower()
        expected2 = r"d:\ProgramData\MemoryServes\media".lower()
        assert dirname == expected1 or dirname == expected2, dirname

    def test_data(self):
        filename = loc.get_data_file().lower()

        assert not os.path.isdir(filename)
        expected1 = r"d:\ProgramData\MemoryServes\data\data.db".lower()
        expected2 = r"d:\Users\Ryan\AppData\Local\MemoryServes\data\data.db".lower()
        assert filename == expected1 or filename == expected2, filename

    def test_template(self):
        dirname = loc.get_template_dir().lower()

        assert os.path.exists(dirname)
        assert os.path.isdir(dirname)
        expected1 = r"D:\Users\Ryan\AppData\Local\MemoryServes\templates".lower()
        expected2 = r"D:\ProgramData\MemoryServes\templates".lower()
        assert dirname == expected1 or dirname == expected2, dirname

    def test_module(self):
        dirname = loc.get_module_dir().lower()

        assert os.path.exists(dirname)
        assert os.path.isdir(dirname)
        expected1 = r"D:\Users\Ryan\AppData\Local\MemoryServes\modules".lower()
        expected2 = r"D:\ProgramData\MemoryServes\modules".lower()
        assert dirname == expected1 or dirname == expected2, dirname


class TestEnsureResDir(unittest.TestCase):
    def setUp(self):
        self.old_glob = loc.glob.glob
        self.old_isdir = loc.os.path.isdir
        self.old_rmdir = loc.os.rmdir
        self.old_copytree = loc.shutil.copytree
        self.old_module_path = loc.module_path
        self.old_get_local_app_data_folder = loc.get_local_app_data_folder

        loc.os.rmdir = self.fake_rmdir
        loc.shutil.copytree = self.fake_copytree
        loc.module_path = lambda: "d:\\module_path"
        loc.get_local_app_data_folder = lambda: "d:\\get_local_app_data_folder"
        self.removed_dir = None
        self.copy_source = None
        self.copy_dest = None

    def tearDown(self):
        loc.glob.glob = self.old_glob
        loc.os.path.isdir = self.old_isdir
        loc.os.rmdir = self.old_rmdir
        loc.shutil.copytree = self.old_copytree
        loc.module_path = self.old_module_path
        loc.get_local_app_data_folder = self.old_get_local_app_data_folder

    def fake_rmdir(self, dirname):
        self.removed_dir = dirname.lower()

    def fake_copytree(self, source, dest):
        self.copy_source = source.lower()
        self.copy_dest = dest.lower()

    def test_yesglob(self):
        loc.glob.glob = lambda x: "foo bar spam egg".split()

        loc.ensure_res_dir("test")
        assert self.removed_dir is None, self.removed_dir
        assert self.copy_source is None, self.copy_source
        assert self.copy_dest is None, self.copy_dest

    def test_noglob_nodir(self):
        loc.glob.glob = lambda x: list()
        loc.os.path.isdir = lambda x: False

        loc.ensure_res_dir("test")
        assert self.removed_dir is None, self.removed_dir
        assert self.copy_source == "D:\\module_path\\test".lower(), self.copy_source
        assert self.copy_dest == "D:\\get_local_app_data_folder\\test".lower(), self.copy_dest

    def test_noglob_yesdir(self):
        loc.glob.glob = lambda x: list()
        loc.os.path.isdir = lambda x: True

        loc.ensure_res_dir("test")
        assert self.removed_dir == "D:\\get_local_app_data_folder\\test".lower(), self.removed_dir
        assert self.copy_source == "D:\\module_path\\test".lower(), self.copy_source
        assert self.copy_dest == "D:\\get_local_app_data_folder\\test".lower(), self.copy_dest

    def test_ensure_resource_files(self):
        loc.glob.glob = lambda x: "foo bar spam egg".split()
        loc.ensure_resource_files()
        assert self.removed_dir is None, self.removed_dir
        assert self.copy_source is None, self.copy_source
        assert self.copy_dest is None, self.copy_dest
