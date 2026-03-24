# coding: UTF8
"""
Wizard controller

"""
import logging

from AnalyzeAssist import broadcaster
from AnalyzeAssist import model
from AnalyzeAssist import file_analysis

LOGGER = logging.getLogger(__name__)


def on_wizard_completed(data, frame):
    """
    Respond to wizard completed event
    """

    match_ranges, fuzzy_options, analyze_numbers = data['prefs']
    broadcaster.Broadcast("match ranges", "changed", match_ranges)

    model.set_fuzzy_options(fuzzy_options)
    model.set_analyze_numbers(analyze_numbers)

    results = file_analysis.get_results(sorted(data['files']), data['memories'], data['prefs'])

    if not results:
        LOGGER.warn("No results to show!")
        return

    frame.addReport(results)


def _test():
    import doctest

    doctest.testmod()


if __name__ == "__main__":
    _test()