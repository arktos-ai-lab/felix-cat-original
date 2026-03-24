"""
Manages permissions
"""

from functools import wraps
import settings
import model


class NotAuthorizedError(Exception):
    """
    Raised when an access is not authorized.
    """
    pass


def get_user_role(token):
    """
    Get the user's role from the token.
    If the token in invalid, returns lowest-ranked role.
    """
    user = model.Data.logins.get(token)
    if not user:
        return "anon"
    return user["role"]

def user_has_priv(role, priv, prefs):
    """
    Does the user have privilege `priv` for role `role`?
    """
    return prefs[role][priv]


def requires_priv(priv):
    """
    Decorator for API methods.
    Raises NotAuthorizedError if user not authorized for privilege.
    Gets user from token in args.

    - `priv` is the privilege to check for.
    """
    def wrap(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            role = get_user_role(kwds.get("token"))
            if not user_has_priv(role, priv, settings.get_privs()):
                msg = "User role `%s` not authorized for privilege `%s`" % (role, priv)
                raise NotAuthorizedError(msg)
            return f(*args, **kwds)
        return wrapper
    return wrap
