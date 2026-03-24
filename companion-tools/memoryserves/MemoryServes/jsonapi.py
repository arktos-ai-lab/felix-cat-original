#!/usr/bin/env python

import api
import simplejson
import datetime

def encode_dict(obj):
    """
    The fallback encoder for transforming Python objects to JSON objects.
    """

    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(repr(obj) + " is not JSON serializable")

class JsonApi(api.Api):
    """
    This API provides data in JSON format instead of pickled Python objects.

    Mainly for interop with other languages (JavaScript and C++)
    """

    def __init__(self):
        api.Api.__init__(self, "jsonapi")

    def dumps(self, obj):
        return simplejson.dumps(obj, default=encode_dict)
