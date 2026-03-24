#coding: UTF8
"""
Settings in Memory Serves

"""

import sys
import os
import socket
import cPickle
import ConfigParser
from optparse import OptionParser
import logging
import pprint

import loc
from normalizer import strip, normalize_width, normalize_kana

HOST_NAME = socket.gethostname()
logger = logging.getLogger(__name__)

class Settings:
    HOST = socket.gethostbyname(HOST_NAME)
    PORT = 8765
    NUM_THREADS = 5
    MAX_NUM_RESULTS = 20

    PREFERENCES = {}


def make_lower(text):
    return text.lower()


def make_normalizer(prefs):
    """
    Creates a function to normalize queries according to the
    preferences
    """
    try:
        funcs = [strip]
        if prefs.get("normalize_width"):
            funcs.append(normalize_width)
        if prefs.get("normalize_case"):
            funcs.append(make_lower)
        if prefs.get("normalize_hira"):
            funcs.append(normalize_kana)
        def normalizer(value):
            """
            Wrapped function for normalizing queries
            """
            for func in funcs:
                value = func(value)
            return value
        return normalizer
    except Exception:
        logger.exception("Failed to create normalizer")
        return lambda x : x


def _get_prefs_filename():
    """
    Get the name of the preferences file
    """
    return os.path.join(loc.get_ms_dir("data"), "prefs.pickle")


def get_host():
    """
    Get the global HOST variable
    """
    return Settings.HOST


def get_port():
    """
    Get the global PORT variable
    """
    return Settings.PORT


def get_local_config():
    """
    Get the local configurations for configuring cherrpy
    """
    favicon = os.path.join(loc.get_media_dir(), 'favicon.ico')
    return {
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': favicon,
        },
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': loc.get_media_dir(),
        }}


def get_global_config():
    """
    Get global configurations to configure cherrpy.
    The configs will differ depending on whether we're frozen
    """

    values =  {'global': { 'autoreload.on': False,
                    'server.socket_host': Settings.HOST,
                    'server.socket_port': Settings.PORT,
                    "server.thread_pool": Settings.NUM_THREADS,
                    'server.protocol_version': 'HTTP/1.1',
                    'tools.sessions.on' : True}}
    if not loc.we_are_frozen():
        values["global"].update({'log.screen' : True})
    else:
        access_file = loc.get_log_file("access.log")
        error_file = loc.get_log_file("error.log")

        # Start the files fresh
        open(access_file, "w").close()
        open(error_file, "w").close()

        values["global"].update({'log.error_file' : error_file,
                                 'log.access_file' : access_file,
                                 'environment' : 'production',
                                 'log.screen' : False})
    return values


def serialize_to_stream(obj, stream):
    """Serialize C{obj} to C{stream}.

    >>> from cStringIO import StringIO
    >>> out = StringIO()
    >>> serialize_to_stream(dict(spam="eggs"), out)
    >>> cPickle.loads(out.getvalue())
    {'spam': 'eggs'}
    """
    cPickle.dump(obj, stream)


def load_from_stream(stream):
    """Loads a pickled object from a stream.

    Write and load dict:
    >>> from cStringIO import StringIO
    >>> out = StringIO()
    >>> data = dict(spam="eggs")
    >>> serialize_to_stream(data, out)
    >>> out.seek(0)
    >>> load_from_stream(out)
    {'spam': 'eggs'}
    """

    return cPickle.load(stream)


def get_privs():
    """
    Gets the user privilege settings.
    """
    return Settings.PREFERENCES["user_privs"]


def get_default_prefs():
    """
    Gets the default preferences.
    """

    keys = """site_admin tm_create tm_read tm_update tm_delete
    rec_create rec_read rec_update rec_delete""".split()

    user_anon = dict((key, True) for key in keys)
    user_guest = dict((key, True) for key in keys)
    user_user = dict((key, True) for key in keys)
    user_admin = dict((key, True) for key in keys)

    user_privs = dict(anon=user_anon,
                      guest=user_guest,
                      user=user_user,
                      admin=user_admin)

    prefs = dict(normalize_case=True,
                 normalize_hira=True,
                 normalize_width=True,
                 show_systray_icon=True,
                 one_trans_per_source=False,
                 data_folder=loc.get_ms_dir("data"),
                 user_privs=user_privs)

    return prefs


def get_data_folder():
    """
    Returns the folder where data files are stored.
    """
    data_folder = get_prefs().get("data_folder", loc.get_ms_dir("data"))
    return data_folder


def get_data_file(filename):
    return os.path.join(get_data_folder(), filename)


def get_prefs():
    """
    Get the preferences from disk
    """
    if Settings.PREFERENCES:
        return Settings.PREFERENCES

    Settings.PREFERENCES = get_default_prefs()

    try:
        with open(_get_prefs_filename(),"r") as database:
            Settings.PREFERENCES.update(load_from_stream(database))
    except (EOFError, IOError):
        logger.exception("Failed to load prefs file")
    finally:
        return Settings.PREFERENCES

normalize = make_normalizer(get_prefs())


def serialize(obj, fname):
    """Serialize obj to fname using cPickle

    @param obj: The object (data) to serialize
    @param fname: The name of the output file
    """

    database = open(fname, "w")
    serialize_to_stream(obj, database)
    database.close()


def serialize_prefs(prefs):
    """
    Save preferences to disk
    """
    Settings.PREFERENCES.update(prefs)

    serialize(prefs, _get_prefs_filename())
    global normalize
    normalize = make_normalizer(prefs)


def get_config():
    """
    Gets the MemoryServes configurations.

    Allows setting configs in config file, or from command line.
    """
    try:
        get_config = get_get_config()

        options = get_command_line_config(get_config, sys.argv[1:])
        reflect_command_line_options(options)
    except Exception:
        logger.exception("Failed to get configs")


def get_get_config():
    """
    Gets the function for retrieving the default configurations.
    """
    dirname = loc.get_local_app_data_folder()
    configfile = os.path.join(dirname, "settings.cfg")
    if os.path.exists(configfile):

        config = ConfigParser.ConfigParser()
        config.read(configfile)

        get_config = lambda x: config.get("General", x)

    else:
        config = dict(port="8765",
                      num_threads="5")
        get_config = lambda x: config.get(x)
    return get_config


def get_command_line_config(get_config, args):
    """
    Gets configurations from the command line.
    """

    parser = OptionParser()
    parser.add_option("-p",
                      "--port",
                      dest="port",
                      help="The MemoryServes port",
                      default=get_config("port"))
    parser.add_option("-t",
                      "--threads",
                      dest="threads",
                      help="The number of threads",
                      default=get_config("num_threads"))
    parser.add_option("-m",
                      "--max-matches",
                      dest="max_matches",
                      help="The maximum number of search matches",
                      default=get_config("max_matches"))
    parser.add_option("--data-folder",
                      dest="data_folder",
                      help="The location of the data folder",
                      default=get_data_folder())
    parser.add_option("--echo-settings",
                      dest="echo_settings",
                      action="store_true",
                      help="Prints the preferences to the console",
                      default=False)
    return parser.parse_args(args)[0]


def reflect_command_line_options(options):
    """
    Reflect the command line options in the settings.
    """
    if options.port is not None:
        Settings.PORT = int(options.port)
    if options.threads is not None:
        Settings.NUM_THREADS = int(options.threads)
    if options.max_matches is not None:
        Settings.MAX_NUM_RESULTS = int(options.max_matches)
    if options.data_folder is not None:
        Settings.PREFERENCES["data_folder"] = options.data_folder
    if options.echo_settings:
        pprint.pprint(Settings.PREFERENCES)


if __name__ == '__main__':  # pragma no cover
    get_config()
