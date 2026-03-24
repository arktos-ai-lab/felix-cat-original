# coding: UTF8
"""
Enter module description here.

"""

from glob import glob
import os
import jinja2 as jinja
from jinja2 import Environment, FileSystemLoader
import itertools

import re
import faqify

top = "getting-started.html analysis.html analysiswizard.html"
bottom = "preferences.html utilities.html faq.html"
subfiles = "analyze_files.html extract_segments.html dump-text.html"


def index_cmp(itema, itemb):
    a = os.path.split(itema["filename"])[-1]
    b = os.path.split(itemb["filename"])[-1]

    if a in top:
        if b not in top:
            return -1
        else:
            return cmp(top.index(a), top.index(b))
    elif a in bottom:
        if b not in bottom:
            return 1
        else:
            return cmp(bottom.index(a), bottom.index(b))
    elif b in top:
        return 1
    elif b in bottom:
        return -1
    else:
        return cmp(a, b)


def gather_titles(filenames):
    titles = []

    for filename in filenames:

        if filename.endswith('index.html'):
            continue
        if filename.split("\\")[-1] in subfiles:
            print filename, "is a subfile"
            continue
        text = open(filename).read()
        title = re.search(r'<h1 class="title">(?P<title>[^<]*)</h1>', text)
        assert title
        description = re.search(r"{% block description %}(?P<description>[^\{]*){% endblock %}", text)
        # assert description
        if description:
            d = description.group('description')
        else:
            d = "none"
        titles.append(dict(filename=os.path.split(filename)[-1],
                           title=title.group('title'),
                           description=d))

    return sorted(titles, index_cmp)


def make_output(filenames, context):
    env = Environment(loader=FileSystemLoader('templates'))
    for filename in filenames:
        dest = os.path.split(filename)[-1]
        print dest
        tpl = env.get_template(dest)
        out = open(os.path.join("output", dest), "w")
        out.write(tpl.render(context).encode("utf-8"))
        out.close()


def main():
    if not os.path.isdir("output"):
        os.makedirs("output")

    filenames = glob("templates/*.html")

    context = {}
    context["index"] = gather_titles(filenames)

    faqtext = open("faq.txt").read()
    context["faq"] = faqify.faqify(faqtext)

    make_output(filenames, context)


if __name__ == "__main__":
    main()
