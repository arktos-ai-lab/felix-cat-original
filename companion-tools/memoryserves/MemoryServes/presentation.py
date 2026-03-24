#coding: UTF8
"""
Helpers for data presentation
"""

import locale
from mako.lookup import TemplateLookup
from loc import get_template_dir
from loc import get_module_dir
import model

def format_num(num):
    """Format a number according to given places
    
    @param num: A number (either string or int) to format

    Format a number according to locality and given places
    
    >>> format_num("spam日本語")
    u'spam\\u65e5\\u672c\\u8a9e'

    """

    try:
        inum = int(num)
        locale.setlocale(locale.LC_NUMERIC, "")
        return locale.format("%.*f", (0, inum), True)

    except (ValueError, TypeError):
        if not isinstance(num, unicode):
            return unicode(str(num), "utf8")
        else:
            return num


_lookup = TemplateLookup(directories=[get_template_dir()],
                         module_directory=get_module_dir(),
                         output_encoding='utf-8',
                         encoding_errors='replace',
                         filesystem_checks=model.DEBUG_MODE)

def render(template, context):
    return _lookup.get_template(template).render(**context)
