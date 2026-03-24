# coding: UTF8
"""
Unit test the frame module

"""

from nose.tools import raises
from AnalyzeAssist import broker
from AnalyzeAssist.controller import frame
from AnalyzeAssist import broadcaster


@raises(AssertionError)
def test_module():
    """Make sure that unit tests for this module are working"""

    assert False


class TestRegistration:
    # Help menu
    def test_help_about(self):
        listeners = broadcaster.listeners[('event', 'on_about')]
        assert (frame.on_about, tuple()) in listeners, listeners

    def test_help_license(self):
        listeners = broadcaster.listeners[('event', 'on_license')]
        assert (frame.on_license, tuple()) in listeners, listeners

    def test_help_help(self):
        listeners = broadcaster.listeners[('event', 'on_help')]
        assert (frame.on_help, tuple()) in listeners, listeners

    # Tools menu
    def test_tools_options(self):
        listeners = broadcaster.listeners[('event', 'on_options')]
        assert (frame.on_options, tuple()) in listeners, listeners

    # File menu
    def test_file_wiz_complete(self):
        listeners = broadcaster.listeners[('wizard', 'completed')]
        assert (frame.on_analysis_wiz_complete, tuple()) in listeners, listeners
        
    
    
