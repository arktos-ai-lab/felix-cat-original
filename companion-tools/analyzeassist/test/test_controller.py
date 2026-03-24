# coding: UTF8
"""
Unit test the controller package

"""

from nose.tools import raises

from AnalyzeAssist import controller


@raises(AssertionError)  # Ensure that the unit tests are running on this module...
def test_module():
    assert False