# coding: UTF8
"""
Utilities for unit tests

"""
from AnalyzeAssist import broadcaster


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class MockBroadcastListener:
    def __init__(self, source, title):
        self.numClicked = 0
        self.data = []
        broadcaster.Register(self.onClick, source, title)

    def onClick(self):
        self.numClicked += 1
        self.data.append(broadcaster.CurrentData())

