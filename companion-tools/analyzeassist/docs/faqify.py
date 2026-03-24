"""
faqify.py

Creates HTML 
"""
import textile
import re

ITEMLIST_TMPL = u"<li><a href=\"#item_%(num)s\">%(title)s</a></li>\n"

ITEM_TMPL = u"""<a id=\"item_%(num)s\"></a>
<h2>%(num)s. %(title)s</h2>
%(body)s
<p><a href="#top">Back to top</a></p>"""

FAQ_TMPL = u"""<a name="top"></a>
<!-- FAQ Contents -->
<ol>
%s</ol>
<hr />
<!-- FAQ Items Start Here -->
%s
<!-- FAQ Items End Here -->
"""


def faq_iter(text):
    for item in re.split(u"={3,}", text, re.M):
        try:
            head, body = re.split(u"-{3,}", item, re.M)
            yield head.strip(), body.strip()
        except ValueError:
            raise StopIteration  # we're done


def textile_body(body):
    return textile.textile(body.encode("utf-8"), encoding="utf-8").decode("utf-8")


def get_faq_items(content, markup_func=None, encoding="utf-8"):
    itemlist = []
    items = []

    for i, pair in enumerate(faq_iter(content)):
        title, body = pair
        if markup_func:
            body = markup_func(body)
        num = i + 1

        itemlist.append(ITEMLIST_TMPL % locals())
        items.append(ITEM_TMPL % locals())

    return itemlist, items


def faqify(content):
    itemlist, items = get_faq_items(content, textile_body, "utf-8")

    return FAQ_TMPL % (u"".join(itemlist), u"\n".join(items))
