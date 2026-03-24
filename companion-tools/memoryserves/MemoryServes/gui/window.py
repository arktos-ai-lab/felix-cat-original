__author__ = 'Ryan'


class WrappedWindow(object):
    def __init__(self, window):
        self.window = window

    def __getattr__(self, item):
        return getattr(self.window, item)