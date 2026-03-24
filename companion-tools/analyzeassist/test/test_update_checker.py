# coding: UTF8
"""
Enter module description here.

"""

from AnalyzeAssist.view import update_checker


def test_init():
    assert True


lastest_newer = update_checker.latest_is_newer


def tov(v):
    return dict(version=v)


class TestLatestIsNewer:
    def test_equal(self):
        assert not lastest_newer(tov("1.0"), tov("1.0"))
        assert not lastest_newer(tov("1.0"), tov("1.0"))
        assert not lastest_newer(tov("1.0"), tov("1.0"))

    def test_this_newer(self):
        assert not lastest_newer(tov("1.0"), tov("0.9"))
        assert not lastest_newer(tov("1.1"), tov("1.0.9"))
        assert not lastest_newer(tov("1.5.5"), tov("1.5.4"))

    def test_latest_newer(self):
        assert lastest_newer(tov("1.0"), tov("1.0.1"))
        assert lastest_newer(tov("1.0"), tov("1.1"))
        assert lastest_newer(tov("0.9"), tov("1.0"))