"""
broadcaster.py
"""

import logging
from collections import defaultdict
import inspect

__all__ = ['Register', 'Broadcast',
           'CurrentSource', 'CurrentTitle', 'CurrentData',
           'registerBroadcastListeners']

listeners = defaultdict(list)
currentSources = []
currentTitles = []
currentData = []

DEBUG = False
LOGGER = logging.getLogger(__name__)


def Register(listener, source=None, title=None, arguments=()):
    """
    register a broadcast message
    """
    LOGGER.debug(u'registering message: %s, %s, %s, %s', listener, source, title, arguments)
    key = (source, title)
    item = (listener, arguments)

    if "create_and_show_analysis_wizard" in repr(listeners[key]):
        LOGGER.debug("Already there! %s", listeners[key])
        return

    if "write_analyze_numbers" in repr(listeners[key]):
        LOGGER.debug("Already there! %s", listeners[key])
        return

    listeners[key].append(item)


def Unregister(listener, source=None, title=None, arguments=()):
    LOGGER.debug(u'unregistering message: %s, %s, %s, %s', listener, source, title, arguments)
    key = (source, title)
    unreg_item = (listener, arguments)
    listeners[key] = [item for item in listeners[key] if unreg_item != item]


def Broadcast(source, title, data={}):
    LOGGER.debug(u'broadcasting message: %s, %s, %s', source, title, data)

    currentSources.append(source)
    currentTitles.append(title)
    currentData.append(data)

    listenerList = listeners.get((source, title), [])[:]
    if source:
        listenerList += listeners.get((None, title), [])
    if title:
        listenerList += listeners.get((source, None), [])

    for listener, arguments in listenerList:
        if DEBUG:
            print "Listener:", listener
        apply(listener, arguments)

    currentSources.pop()
    currentTitles.pop()
    currentData.pop()


def CurrentSource():
    return currentSources[-1]


def CurrentTitle():
    return currentTitles[-1]


def CurrentData():
    return currentData[-1]


## Lifted shamelessly from WCK (effbot)'s wckTkinter.bind
def EventHandlerMethod(source, title):
    """
    Dectorator for event-handling methods
    """

    def decorator(func):
        func.BroadcasterEvent = (source, title)
        return func

    return decorator


def EventHandlerFunction(source, title):
    """A decorator for broadcaster handlers
    
    @param title: the title to provide
    
    the decorated function must take no arguments
    (it can retrieve them using CurrentData())
    """

    def decorator(func):
        Register(func, source, title)
        return func

    return decorator


def registerBroadcastListeners(listener):
    for key in dir(listener):
        method = getattr(listener, key)
        if hasattr(method, "BroadcasterEvent") and callable(method):
            source, title = method.BroadcasterEvent
            Register(method,
                     source=source,
                     title=title)


def unregisterBroadcastListener(listener):
    for name, method in inspect.getmembers(listener, callable):
        if hasattr(method, "BroadcasterEvent"):
            source, title = method.BroadcasterEvent
            Unregister(method,
                       source=source,
                       title=title)

