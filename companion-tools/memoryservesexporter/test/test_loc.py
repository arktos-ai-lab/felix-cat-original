__author__ = 'Ryan'

from MemoryServesExporter import loc
import unittest
import mock
import os

class TestWeAreFrozen(unittest.TestCase):
    """
    Test the function to tell if we are frozen with py2exe.
    """
    def not_frozen(self):
        assert not loc.we_are_frozen()

class TestModulePath(unittest.TestCase):
    def test_drive(self):
        mod_path = loc.module_path()
        expected = "d:\\dev\\python\\MemoryServesExporter"

        norm = lambda x : os.path.normcase(os.path.abspath(x))
        assert norm(mod_path) == norm(expected), mod_path

    def test_frozen(self):
        """
        Make sure we get the D dir when getting the executable!
        """
        with mock.patch.object(loc, 'we_are_frozen', return_value=True):
            mod_path = loc.module_path().lower()
            expected = "d:\\python27"
            assert mod_path == expected, mod_path

