# coding: UTF8
"""
Unit tests for analyze_files

"""

from nose.tools import raises
from AnalyzeAssist import analyze_files


def test_range2item():
    """Test the range2item function in analyze_files"""
    r2i = analyze_files.range2item
    assert r2i((100, 100)) == "100%"
    assert r2i((90, 100)) == "90-100%", range2item((90, 100))
    assert r2i((0, 0)) == "0%"
    assert r2i((0, 59)) == "0-59%"
    assert r2i((40, 60)) == "40-60%"


@raises(TypeError)
def test_funkyrange2item1():
    assert analyze_files.range2item(100) == "100%"


@raises(ValueError)
def test_funkyrange2item1():
    """Too many values to unpack"""
    assert analyze_files.range2item("repetitions") == "Repetitions"


def test_run():
    analyze_files.main(["-o",
                        "analysis.txt",
                        "-f",
                        "/test/a.txt",
                        "-m",
                        "/test/a.xml"])