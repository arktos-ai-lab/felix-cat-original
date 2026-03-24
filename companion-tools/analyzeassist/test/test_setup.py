# coding: UTF8
"""
Unit tests for the setup module

"""

from nose.tools import raises
# If we leave this as setup, nose will try to run it!
from AnalyzeAssist import make_setup as aa_setup


@raises(AssertionError)
def test_module():
    """Ensure that the unit tests are running on this module..."""
    assert False


def test_get_setup_dict():
    setup_dict = aa_setup.get_setup_dict("main.py", "spam")
    assert setup_dict


def test_add_data_files():
    setup_dict = aa_setup.add_data_files({})
    assert "data_files" in setup_dict, setup_dict

