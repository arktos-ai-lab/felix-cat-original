"""
The admin interface to Memory Serves.

    - /admin/
    - /users/
    - /log/
"""
from __future__ import with_statement

import warnings

warnings.simplefilter("ignore", DeprecationWarning)

import cherrypy
import cherrybase
from presentation import render
import model
import loc
import settings
from model import ensure_u


def user_by_name(users, name):
    """
    Retrieve user by username

    :param users: List of user dict objects
    :param name: The username to search for
    :return: The user object, if found. Otherwise None.
    """
    for user in users:
        if user["name"] == name:
            return user


def user_by_id(users, user_id):
    """
    Retrieve user by ID

    :param users: List of user dict objects
    :param user_id: The user ID to search for
    :return: The user object, if found. Otherwise None.
    """
    for user in users:
        if user["id"] == user_id:
            return user


class Admin(object):
    """
    Represents the log directory
    """

    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        """
        Show admin interface
        """
        context = cherrybase.init_context()
        context.update(dict(title="Memory Serves :: Admin"))
        return render("admin_index.html", context)


class Log(object):
    """
    Represents the log directory
    """

    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        """
        Show log
        """
        entries = model.Data.log

        context = cherrybase.init_context()
        context.update(dict(title="Memory Serves :: Log",
                            entries=entries))
        return render("log_index.html", context)

    @cherrypy.expose
    def errorlog(self):
        """
        Show server error log
        """
        context = cherrybase.init_context()
        context["title"] = "Memory Serves :: Server Error Log"
        context["errlog"] = loc.get_log_file_text("error.log")

        return render("log_error.html", context)

    @cherrypy.expose
    def serverlog(self):
        """
        Show server error log
        """
        context = cherrybase.init_context()
        context["title"] = "Memory Serves :: Server Access Log"
        context["accesslog"] = loc.get_log_file_text("access.log")
        return render("log_server.html", context)

    @cherrypy.expose
    def clear(self):
        """Clears the log"""

        context = cherrybase.init_context()
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to clear the log.
                             </div>""")
            raise cherrypy.HTTPRedirect("/log/")

        model.Data.log = []
        cherrybase.add_message("""<div class="success">
                         Cleared log.
                         </div>""")

        raise cherrypy.HTTPRedirect("/log/")


class Users(object):
    """
    Controls user accounts
    """

    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        """
        List users
        """

        context = cherrybase.init_context()
        context["title"] = "Memory Serves :: Users"
        context["users"] = model.Data.users.values()
        return render("users_index.html", context)

    @cherrypy.expose
    def add(self):
        """
        Show the add user page
        """

        context = cherrybase.init_context()
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to add a user.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/")

        context.update(dict(title="Memory Serves :: Add User"))
        return render("users_add.html", context)

    @cherrypy.expose
    def submitwelcome(self, **kwds):
        """
        Called by welcome page
        """

        if not kwds["name"] or not kwds["password"]:
            cherrybase.add_message("""<div class="error">
                             Name or password field empty
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/welcome")

        if kwds["password"] != kwds["confirm"]:
            cherrybase.add_message("""<div class="error">
                             Passwords did not match
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/welcome")

        user = model.User(name=kwds["name"].decode("utf-8"),
                          password=kwds["password"].decode("utf-8"),
                          role="admin",
                          ip=cherrypy.request.remote.ip)

        user.id = model.get_next_userid()
        user = model.user2d(user)
        model.Data.users[user["id"]] = user
        cherrybase.log_info(u"User '%(name)s' logged in" % user)

        cherrypy.session["user"] = user
        cherrybase.add_message("""<div class="success">
                         Successfully created admin account for %(name)s.
                         </div>""" % user)
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def submitadd(self, **kwds):
        """
        Called by submit button on
        add page
        """

        context = cherrybase.init_context()
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to add a user.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/")

        if kwds["password"] != kwds["confirm"]:
            cherrybase.add_message("""<div class="error">
                             Passwords did not match
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/add")

        userobj = model.User(name=kwds["name"].decode("utf-8"),
                             password=kwds["password"].decode("utf-8"),
                             role=kwds["role"].decode("utf-8"),
                             ip=u"")

        with model.Data.lock:
            userobj.id = model.get_next_id(model.Data.users.keys())
            user = model.user2d(userobj)
            model.Data.users[userobj.id] = user

        cherrybase.log_info(u"Created new user account: %(name)s" % user)

        cherrybase.add_message("""<div class="success">
                         Successfully created account.
                         </div>""")
        raise cherrypy.HTTPRedirect("/users/view/%(id)s" % user)

    @cherrypy.expose
    def logout(self, next):
        """
        Log out the current user
        """
        user = cherrypy.session["user"]
        user["ip"] = u""

        cherrybase.log_info(u"User '%(name)s' logged out" % user)

        del cherrypy.session["user"]
        cherrybase.add_message("""<div class="success">
                         You have been logged out.
                         </div>""")
        raise cherrypy.HTTPRedirect(next)

    @cherrypy.expose
    def welcome(self):
        """
        Show the welcome page
        (When there are no users in the database)
        """

        context = cherrybase.init_context(title="Memory Serves :: Welcome")
        return render("users_welcome.html", context)

    @cherrybase.requires_priv("site_admin")
    @cherrypy.expose
    def delete(self, userid):
        """
        Delete user `userid`
        """

        context = cherrybase.init_context()
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to delete a user.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/")

        user = model.Data.users[int(userid)]
        del model.Data.users[int(userid)]

        cherrybase.log_info(u"Deleted user '%(name)s'" % user)
        cherrybase.add_message("""<div class="success">
                         Deleted user '%(name)s'.
                         </div>""" % user)
        raise cherrypy.HTTPRedirect("/users/")


    @cherrypy.expose
    def edit(self, userid):
        """
        Show the user edit page for `userid`
        """

        context = cherrybase.init_context()
        if not context["logged_in"]:
            cherrybase.add_message("""<div class="error">
                             You must be logged in to edit account info.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/")

        edituser = user_by_id(model.Data.users.values(), int(userid))
        if not context["is_admin"]:
            sessionuser = cherrypy.session.get("user")
            if edituser["id"] != sessionuser["id"]:
                cherrybase.add_message("""<div class="error">
                                 You must be an admin to edit another user's account.
                                 </div>""")
                raise cherrypy.HTTPRedirect("/users/")

        context["title"] = "Memory Serves :: Edit Info for User %(name)s" % edituser
        context["edituser"] = edituser

        return render("users_edit.html", context)

    @cherrypy.expose
    def submitedit(self, userid, **kwds):
        """
        Called by submit button on add page. Submits edit for user `userid`.
        """
        context = cherrybase.init_context()
        if not context["logged_in"]:
            cherrybase.add_message("""<div class="error">
                             You must be logged in to edit account info.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/")

        userid = int(userid)
        user = model.Data.users[userid]

        if not context["is_admin"]:
            sessionuser = cherrypy.session.get("user")
            if user["id"] != sessionuser["id"]:
                cherrybase.add_message("""<div class="error">
                                 You must be an admin to edit another user's account.
                                 </div>""")
                raise cherrypy.HTTPRedirect("/users/")

            if kwds["role"] == "admin":
                cherrybase.add_message("""<div class="error">
                                 You cannot change your role to admin.
                                 </div>""")
                raise cherrypy.HTTPRedirect("/users/")

        if kwds["password"] and kwds["confirm"]:
            if kwds["password"] != kwds["confirm"]:
                cherrybase.add_message("""<div class="error">
                                 Passwords did not match
                                 </div>""")
                raise cherrypy.HTTPRedirect("/users/edit/%s" % userid)
            user["password"] = kwds["password"].decode("utf-8")

        user["name"] = kwds["name"].decode("utf-8")
        user["role"] = kwds["role"].decode("utf-8")

        cherrybase.log_info(u"Edited user account: %(name)s" % user)

        cherrybase.add_message("""<div class="success">
                         Successfully edited account.
                         </div>""")
        raise cherrypy.HTTPRedirect("/users/view/%(id)s" % user)

    @cherrypy.expose
    def view(self, userid):
        """
        View the user information for `userid`.
        """

        context = cherrybase.init_context()
        user = user_by_id(model.Data.users.values(), int(userid))
        context["title"] = "Memory Serves :: View User %(name)s" % user
        context["viewuser"] = user

        return render("users_view.html", context)

    @cherrypy.expose
    def login(self, next):
        """Show the login page
        """
        context = cherrybase.init_context(title="Memory Serves :: Log in",
                                          next=next)
        return render("login.html", context)

    @cherrypy.expose
    def submitlogin(self, next, name, password):
        """Called by the login form on the login page
        """

        if not isinstance(name, unicode):
            name = name.decode("utf-8")

        users = model.Data.users
        user = user_by_name(users.values(), name)

        if not user:
            cherrybase.add_message("""<div class="error">
                             User name or password incorrect.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/login/?next=%s" % next)

        password = ensure_u(password)
        hashed = model.make_hash(password)

        if user["password"] != hashed:
            cherrybase.add_message("""<div class="error">
                             User name or password incorrect.
                             </div>""")
            raise cherrypy.HTTPRedirect("/users/login/?next=%s" % next)

        print "authenticated"

        cherrypy.session["user"] = user

        cherrybase.log_info(u"User '%(name)s' logged in" % user)

        cherrybase.add_message("""<div class="success">
                         Welcome, %(name)s.
                         </div>""" % user)
        raise cherrypy.HTTPRedirect(next)

    @cherrybase.requires_priv("site_admin")
    @cherrypy.expose
    def permissions(self):
        context = cherrybase.init_context(title="Memory Serves :: Users :: Permissions")
        context["privs"] = settings.get_privs()
        return render("users_permissions.html", context)

    @cherrybase.requires_priv("site_admin")
    @cherrypy.expose
    def submitpermissions(self, **kwds):
        privs = settings.get_privs()
        set_privs(privs, kwds)
        settings.serialize_prefs(settings.Settings.PREFERENCES)
        cherrybase.add_message("""<div class="success">
                         Configured user preferences.
                         </div>""")
        raise cherrypy.HTTPRedirect("/users/")


def set_privs(privs, data):
    for role in privs.keys():
        for action in privs[role].keys():
            privs[role][action] = role + '.' + action in data
