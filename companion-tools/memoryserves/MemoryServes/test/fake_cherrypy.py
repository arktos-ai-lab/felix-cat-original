#coding: UTF8
"""
Enter module description here.

"""

class FakeRemote(object):
    def __init__(self, ip=u""):
        self.ip = ip

class FakeRequest(object):
    def __init__(self, path_info=""):
        self.path_info = path_info
        self.remote = FakeRemote()

class FakeResponse(object):
    def __init__(self, headers=None):
        self.headers = headers or {}

class FakeTree(object):
    def __init__(self):
        self.mounted = None
    def mount(self, app, path, config):
        self.mounted = dict(app=app,
                            path=path,
                            config=config)

class FakeServer(object):
    def quickstart(self):
        pass

class FakeEngine(object):

    def __init__(self):
        self.blocking = None
        self.subscriptions = []

    def subscribe(self, label, callback):
        self.subscriptions.append((label, callback))

    def start(self, blocking=False):
        self.blocking = blocking

    def wait(self):
        pass

    def block(self):
        pass

class FakeCherryPy(object):
    def __init__(self,
                 session=None,
                 request=None,
                 response=None,
                 tree=None,
                 server=None,
                 engine=None):
        self.session = session or {}
        self.request = request or FakeRequest()
        self.response = response or FakeResponse()
        self.config = {}
        self.tree = tree or FakeTree()
        self.server = server or FakeServer()
        self.engine = engine or FakeEngine()

    class HTTPRedirect(Exception):
        def __init__(self, dest):
            self.dest = dest

class FakeResult:
    def __init__(self, items):
        self.items = items

    def all(self):

        return self.items

    def fetchone(self):
        return self.items[0]

class FakeConnection:
    def execute(self, *args):
        return FakeResult([[1]])

class FakeBind:
    def connect(self):
        return FakeConnection()

class FakeSqlAlchemySession:
    items = []
    bind = FakeBind()

    def __init__(self):
        pass

    def query(self, model):
        return FakeResult([x for x in FakeSqlAlchemySession.items if isinstance(x, model)])

    @staticmethod
    def remove():
        pass


class FakeRenderer:
    def __init__(self):
        self.page = None
        self.context = {}
    def render(self, page, context):
        self.page = page
        self.context = context
        return page
