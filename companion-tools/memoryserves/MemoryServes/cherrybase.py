#coding: UTF8
"""
Enter module description here.

"""

import logging
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import model
import sys
import cherrypy
import settings
import datetime
import permissions
from functools import wraps

def get_user_role(session):
    """
    Gets the role for the user. If the user is not in the session,
    the role is `anon`.
    """

    user = session.get("user")
    if user:
        return user["role"]
    else:
        return "anon"

def requires_priv(priv):
    """
    Decorator for web methods.
    Redirects to login page on failure.
    Tries to get user role from session.
    """
    def wrap(f):

        @wraps(f)
        def wrapper(*args, **kwds):
            role = get_user_role(cherrypy.session)
            if not permissions.user_has_priv(role, priv, settings.get_privs()):
                msg = "User role %s not authorized for privilege %s" % (role, priv)
                print msg
                feedback_error(msg)
                raise cherrypy.HTTPRedirect("/users/login/?next=/users")
            return f(*args, **kwds)
        return wrapper
    return wrap


def add_message(msg):
    """
    Add a message to the cherrypy session, to
    be retrieved when the next page is shown
    """

    if "msgs" not in cherrypy.session:
        cherrypy.session["msgs"] = []
    cherrypy.session["msgs"].append(msg)

def feedback_info(msg):
    add_message("""<div class="ui-widget" style="margin-top: 10px; margin-bottom: 10px;">
        <div class="ui-state-highlight ui-corner-all"  style="padding: 0 .7em;">
            <p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em; margin-top: .3em"></span>
            %s</p>
        </div></div>""" % msg)

def feedback_error(msg):
    add_message("""<div class="ui-widget" style="margin-top: 10px; margin-bottom: 10px;">
        <div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">
            <p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em; margin-top: .3em"></span>
            %s</p>
        </div></div>""" % msg)


def get_messages():
    msg = "\n".join(cherrypy.session.get("msgs", []))
    cherrypy.session["msgs"] = []
    return msg


def init_context(**kwds):
    user = cherrypy.session.get("user")
    logged_in= bool(user)
    is_admin = logged_in and user["role"] == u"admin"
    context = dict(msg=get_messages(),
                   is_admin=is_admin,
                   logged_in=logged_in,
                   current_page=cherrypy.request.path_info,
                   version=model.VERSION)
    if logged_in:
        context["user"] = user
    context.update(kwds)
    return context

def to_date(text):
    """
    Parse the time into a time object if it's a string.
    If it's already a date, return that.
    """

    time_format = "%Y/%m/%d %H:%M:%S"

    if isinstance(text, unicode):
        return text
    if isinstance(text, basestring):
        return unicode(text, "utf-8")
    try:
        return text.strftime(time_format)
    except AttributeError:
        return datetime.datetime(*text[:6]).strftime(time_format)

def replacer(text):
    """
    Replace the forbidden character codes
    """
    if not isinstance(text, unicode):
        text = unicode(text, "utf-8")
    for code in range(1, 10):
        char = unichr(code)
        replacement = u"&#%s;" % code
        text = text.replace(char, replacement)
    return text

def get_username(session=None):
    """
    Get the username for this session.

    * If there's a logged in user (user in session), returns user.name
    * If there's a username in the session, returns that.
    * Otherwise, gets the IP of the host machine.
        + If there's an IP address in the session that matches,
          returns the login name.
        + Otherwise, returns the machine name.
    """
    session = session or {}
    user = session.get("user")
    if user:
        return user["name"]

    username = session.get("username")
    if username:
        return username

    userip = session.get("ip")
    if userip == settings.get_host():
        username = model.USER_NAME
    else:
        username = unicode(settings.HOST_NAME, sys.getfilesystemencoding())

    session["username"] = username
    return username

def log_message(message, severity=u"info"):
    log_entry = dict(message=message,
                    severity=severity,
                    user=get_username(cherrypy.session) or u"",
                    when=model.parse_time(None))
    model.Data.log.append(log_entry)

def log_info(message):
    log_message(message, u"info")

def log_warning(message):
    log_message(message, u"warn")

def log_error(message):
    log_message(message, u"error")


def log_mem_failure(memory_id):
    """
    Log a failure to find a memory
    """

    msg = "Memory with id: %s not found" % memory_id
    log_warning(msg)


def set_results_message(count):
    """
    Set the message showing whether there were matches
    for the search
    """
    if not count:
        feedback_error("Sorry, no matches")
    else:
        feedback_info("Found %d matches" % count)
