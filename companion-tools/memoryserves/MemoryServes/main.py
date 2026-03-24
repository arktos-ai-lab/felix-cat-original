# coding: utf-8
"""
Main module for Memory Serves application

Memory Serves uses cherrypy to serve translation memories via HTTP.

MIT License

Copyright Ryan Ginstrom
"""
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import os
import webbrowser
import threading
import urllib2
import sys
import logging

import cherrypy

import TMX.writer

import loc
import settings
import model
from model import Memory
import dataloader
from dataloader import set_up_database
import site_records
from mem_parser import get_root, get_head, get_records
import search
from search import refine_replacefrom, refine_query, do_replacement
from search import ensure_u
import cherrybase
from cherrybase import set_results_message
from presentation import format_num, render
from SysTrayIcon import show_sys_icon
from globalsearch import GlobalSearch
import admin
import api
import jsonapi
from language import LANG_CODES, get_codes
import repository
from repository import Memories, Glossaries

__version__ = model.VERSION
__author__ = "Ryan Ginstrom"
__progname__ = "Memory Serves"


logger = logging.getLogger(__name__)


class MemoryServesApp(object):
    """ App base request handler class. """

    def __init__(self):

        logger.debug("Initializing Memory Serves application")

        self.memories = Memories()
        self.glossaries = Glossaries()
        self.users = admin.Users()
        self.api = api.Api()
        self.records = site_records.Records()
        self.log = admin.Log()
        self.admin = admin.Admin()
        self.globalsearch = GlobalSearch()
        self.jsonapi = jsonapi.JsonApi()


    @cherrypy.expose
    def index(self):
        """
        /
        The base URL
        """

        if len(model.Data.users) == 0:
            raise cherrypy.HTTPRedirect("/users/welcome")

        context = cherrybase.init_context(title="Memory Serves :: Home")
        context["connection"] = "%s:%s" % (settings.get_host(), settings.get_port())
        context.update(settings.get_prefs())
        return render("index.html", context)

    @cherrypy.expose
    def help(self):
        """
        Show the help file
        """

        context = cherrybase.init_context(title="Memory Serves :: Help")
        return render("help.html", context)

    @cherrybase.requires_priv("site_admin")
    @cherrypy.expose
    def editprefs(self, **kwds):
        """
        Edit the preferences
        """

        prefs = settings.get_prefs()

        data_folder = kwds.get("data_folder")
        if not os.path.isdir(data_folder) or not os.path.exists(data_folder):
            cherrybase.feedback_error("Data folder %s does not exist" % data_folder)
            raise cherrypy.HTTPRedirect("/preferences")

        prefs["normalize_case"] = bool(kwds.get("case"))
        prefs["normalize_width"] = bool(kwds.get("width"))
        prefs["normalize_hira"] = bool(kwds.get("hira"))
        prefs["show_systray_icon"] = bool(kwds.get("systray"))
        prefs["one_trans_per_source"] = bool(kwds.get("one_trans_per_source"))
        prefs["data_folder"] = data_folder

        repository.reflect_one_trans(prefs["one_trans_per_source"])

        settings.serialize_prefs(prefs)
        cherrybase.add_message("""<div class="success">
                         Changed preferences
                         </div>""")
        raise cherrypy.HTTPRedirect("/")


    @cherrybase.requires_priv("site_admin")
    @cherrypy.expose
    def preferences(self):
        """
        Show the edit preferences form
        """

        prefs = settings.get_prefs()

        title = "Memory Serves :: Preferences"
        context = cherrybase.init_context(title=title)
        context["connection"] = "%s:%s" % (settings.get_host(), settings.get_port())
        context.update(prefs)
        return render("preferences.html", context)

    @cherrypy.expose
    def backdoor(self):
        """
        /exit
        Quits the application
        """

        # Only allow this in non-frozen builds
        if loc.we_are_frozen():
            raise cherrypy.HTTPRedirect("/")

        context = cherrybase.init_context(title="Memory Serves :: Quit")
        model.SHOULD_QUIT = True
        dataloader.SHOULD_QUIT = True
        return render("exit.html", context)

    @cherrypy.expose
    def exit(self):
        """
        /exit
        Quits the application
        """

        context = cherrybase.init_context(title="Memory Serves :: Quit")
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to exit the program.
                             </div>""")
            raise cherrypy.HTTPRedirect("/")

        model.SHOULD_QUIT = True
        dataloader.SHOULD_QUIT = True
        return render("exit.html", context)

def configure_application(server, SessionClass):
    """
    Set up the cherrypy application
    """

    # Update the global CherryPy configuration
    server.config.update(settings.get_global_config())

    dataloader.load_data(SessionClass)

    # Set up our directory structure
    app = MemoryServesApp()

    # mount the application on the '/' base path
    server.tree.mount(app, '/', config=settings.get_local_config())

    server.response.timeout = 1200
    server.server.socket_timeout = 120


def set_up_logging(loc, logging):
    """
    Configures logging according to whether we are frozen.

    When the app is not frozen, set level to debug.
    """

    if loc.we_are_frozen():
        format = '%(asctime)-15s %(name)s %(message)s'
        message_file = loc.get_log_file("message.log")
        logging.basicConfig(filename=message_file, format=format)

    else:
        format = '%(asctime)-15s %(name)s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=format)


def launch_app(cherrypy, cherrybase, url):
    """
    Memory Serves is not already running, so we set it up and launch it.
    """

    threading.Timer(1, dataloader.background_save).start()

    loc.ensure_resource_files()

    configure_application(cherrypy, set_up_database(loc.get_data_file()))

    # Start the CherryPy HTTP server
    cherrypy.engine.subscribe('start', lambda:  webbrowser.open(url))
    cherrypy.engine.start()

    set_up_logging(loc, logging)

    if settings.get_prefs()["show_systray_icon"]:
        show_sys_icon(cherrybase)

    # Wait for events
    cherrypy.engine.wait()


def main():
    """
    The main function called for the application.

    If MemoryServes is already running, we launch the browser.
    Otherwise, we launch the app.
    """

    # load the configurations (possibly from the command line)
    settings.get_config()
    url = "http://%s:%s/" % (settings.get_host(), settings.get_port())
    try:
        # see if we can open the url (if the app is already running)
        urllib2.urlopen(url)
    except:
        launch_app(cherrypy, cherrybase, url)
    else:
        # Start the CherryPy engine
        print >> sys.stderr, "Already running. Launching web browser."
        webbrowser.open(url)


if __name__ == '__main__':  # pragma nocover
    main()
