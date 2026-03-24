# ####################################################################
# broker.py
#

__all__ = ['Register', 'Request',
           'CurrentTitle', 'CurrentData']

providers = {}
currentTitles = []
currentData = []


def BrokerRequestHandler(title):
    """A decorator for broadcaster handlers
    
    @param title: the title to provide
    
    the decorated function must take no arguments
    (it can retrieve them using CurrentData())
    """

    def decorator(func):
        Register(title, func)
        return func

    return decorator


def Register(title, provider, arguments=()):
    """Register a provider
    
    @param title: the name of the data to provide
    @param provider: the provider of the data
    @type provider: a callable
    @param arguments: arguments to pass to the provider
    
    There can only be one provider for each title
    """

    if title in providers:
        return

    providers[title] = (provider, arguments)


def Request(title, data={}):
    """Request the data for C{title}.
    
    @param title: the name of the data requested
    @param data: data to pass to the provider
    """

    currentTitles.append(title)
    currentData.append(data)

    result = apply(apply, providers.get(title))

    currentTitles.pop()
    currentData.pop()

    return result


def CurrentTitle():
    """The currently requested title"""

    return currentTitles[-1]


def CurrentData():
    """Data passed to current Request"""

    return currentData[-1]
