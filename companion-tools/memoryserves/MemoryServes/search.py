# coding: utf-8
"""
search features
"""
import logging
import datetime
import re
import itertools
import model
import urllib
import os

import settings
from normalizer import strip
from presentation import format_num
from model import ensure_u

PAGE_SIZE = 20  # The number of records per page
PAGE_RANGE = 10  # The range of pages to display in navigation

logger = logging.getLogger(__name__)

def make_xml_filename(name, is_memory):
    """
    Make sure the download filename has an .xml extension
    """
    ext = "fgloss"
    if is_memory:
        ext = "ftm"

    name = name.strip().replace(" ", "_")

    if name.lower().endswith("."):
        return name + ext

    base = os.path.splitext(name)[0]
    return base + "." + ext


def make_tmx_filename(name):
    """
    Make sure the download filename has an .xml extension
    """

    name = name.strip().replace(" ", "_")

    if name.lower().endswith("."):
        return name + "tmx"
    base = os.path.splitext(name)[0]
    return base + ".tmx"


def mem_truther(value):
    """
    Convert truth value into string.

    Anything that is not a variant of "true" is "false"
    """

    try:
        return {True : "true",
                False: "false",
                "True": "true",
                "False": "false",
                "true": "true",
                "false": "false"}[value]
    except KeyError:
        return "false"


def slice_recs(records, context):
    """
    Gets a slice of the records from the context dict.
    """
    return list(records[context["page_start"]:context["page_end"]])


def get_page_range(current, total):
    """
    Get the page range to show.

    So if we are on page 50 out of 100, it will show us 45 to 55.
    >>> get_page_range(50, 100)
    [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]

    If we are at the beginning of the range, it will shift the range forward.
    >>> get_page_range(1, 100)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    Similarly, if we are at the send of the range, it will shift the range back.
    >>> get_page_range(99, 100)
    [90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]

    If the total page count is less than 10, we just show that range.
    >>> get_page_range(5, 6)
    [1, 2, 3, 4, 5, 6]
    """
    if total < PAGE_RANGE:
        return range(1, total+1)

    half_range = PAGE_RANGE / 2

    start = max(1, current-half_range)
    end = min(total+1, current+half_range+1)
    if start == 1:
        end = min(PAGE_RANGE+1, total+1)
    if end == total+1:
        start = max(1, total-PAGE_RANGE)

    return range(start, end)


def set_pagination(context, page, count):
    """
    Set the pagination information for search and browse pages
    """

    page = int(page)

    start = max(0, (page-1)) * PAGE_SIZE

    context["num"] = format_num(count)
    context["page"] = page
    end = start + PAGE_SIZE

    context["has_next"] = count > end
    context["next_page"] = page+1
    context["has_prev"] = page > 1
    context["prev_page"] = page-1
    context["page_size"] = PAGE_SIZE
    context["page_start"] = start
    context["page_end"] = end

    extra = min(1, count % PAGE_SIZE)
    num_pages = (count / PAGE_SIZE) + extra
    context["last_page"] = num_pages
    context["pages"] = get_page_range(page, num_pages)

    context["num_pages"] = format_num(num_pages)
    return context


def smooth_queryfilters(queryfilters):
    """
    Make sure that all our queryfilters are unicode
    """
    if isinstance(queryfilters, basestring):
        return [ensure_u(queryfilters)]
    else:
        return [ensure_u(qf) for qf in queryfilters]


def exclude(qf, queryfilters):
    """
    Exclude the term qf from the query filters
    """
    return [t.encode("utf-8") for t in queryfilters if t != qf]


def make_querylink(terms):
    """
    Make a link for the given query terms
    """

    link = "&amp;".join(["queryfilters=%s" % urllib.quote_plus(term)
                         for term in terms])
    if link:
        return u"?" + link.decode("utf-8")
    return u""


def get_queryfilters(search_query, queryfilters):
    """
    Get the list of query filters from the supplied
    search term and queryfilters parameter
    """

    queryfilters = queryfilters or []
    if isinstance(queryfilters, basestring):
        queryfilters = [ensure_u(queryfilters)]
    else:
        queryfilters = [ensure_u(qf) for qf in queryfilters]

    search_query = ensure_u(search_query)

    if search_query:
        queryfilters.append(search_query)
    return queryfilters


class SearchQuery:
    """
    Represents a search query.
    """

    def __init__(self, query):
        self.querytype = "general"
        self.isregex = False
        self.query = query

        self.parse_query(query)

    def parse_query(self, term):
        """
        Parses a user search query. Supports tags: regex, source, etc.
        """
        if term.startswith(u"regex:"):
            self.isregex = True
            term = term[len("regex:"):]

        if term.startswith(u"source:"):
            self.querytype = "source"
            self.query = term[len("source:"):]

        elif term.startswith(u"trans:"):
            self.querytype = "trans"
            self.query = term[len("trans:"):]

        elif term.startswith(u"context:"):
            self.querytype = "context"
            self.query = term[len("context:"):]

        # created
        elif term.startswith(u"created-by:"):
            self.querytype = "created-by"
            self.query = term[len("created-by:"):]

        elif term.startswith(u"created-before:"):
            self.querytype = "created-before"
            self.query = term[len("created-before:"):]

        elif term.startswith(u"created-after:"):
            self.querytype = "created-after"
            self.query = term[len("created-after:"):]

        # modified
        elif term.startswith(u"modified-by:"):
            self.querytype = "modified-by"
            self.query = term[len("modified-by:"):]

        elif term.startswith(u"modified-before:"):
            self.querytype = "modified-before"
            self.query = term[len("modified-before:"):]

        elif term.startswith(u"modified-after:"):
            self.querytype = "modified-after"
            self.query = term[len("modified-after:"):]

        # reliability
        elif term.startswith(u"reliability-gt:"):
            self.querytype = "reliability-gt"
            self.query = term[len("reliability-gt:"):]

        elif term.startswith(u"reliability-gte:"):
            self.querytype = "reliability-gte"
            self.query = term[len("reliability-gte:"):]

        elif term.startswith(u"reliability-lt:"):
            self.querytype = "reliability-lt"
            self.query = term[len("reliability-lt:"):]

        elif term.startswith(u"reliability-lte:"):
            self.querytype = "reliability-lte"
            self.query = term[len("reliability-lte:"):]

        elif term.startswith(u"reliability:"):
            self.querytype = "reliability"
            self.query = term[len("reliability:"):]

        # validated
        elif term.startswith(u"validated:"):
            self.querytype = "validated"
            self.query = term[len("validated:"):]

        # ref_count
        elif term.startswith(u"refcount:"):
            self.querytype = "refcount"
            self.query = term[len("refcount:"):]

        elif term.startswith(u"refcount-gt:"):
            self.querytype = "refcount-gt"
            self.query = term[len("refcount-gt:"):]

        elif term.startswith(u"refcount-gte:"):
            self.querytype = "refcount-gte"
            self.query = term[len("refcount-gte:"):]

        elif term.startswith(u"refcount-lt:"):
            self.querytype = "refcount-lt"
            self.query = term[len("refcount-lt:"):]

        elif term.startswith(u"refcount-lte:"):
            self.querytype = "refcount-lte"
            self.query = term[len("refcount-lte:"):]

        else:
            self.querytype = "general"
            self.query = term

        if self.query.startswith(u"regex:"):
            self.isregex = True
            self.query = self.query[len("regex:"):]


    def __str__(self):  # pragma: no cover
        """
        Conversion to string for debugging.
        """
        return "[%s] [%s] %s" % (self.querytype, self.isregex, self.query)


def term_to_date(term):
    """
    Parse a search term into a date
    """
    year, month, day = re.split("[:/-]", term)
    return datetime.datetime(int(year), int(month), int(day))


def refine_replacefrom(records, term):
    """
    Refine query for replace
    """

    for dontcare in "created: reliability: validated: refcount: modified:".split():
        if term.startswith(dontcare):
            return records

    return refine_query(records, term)


def refine_query(records, term):
    """
    Narrow a query from a given set
    """

    sq = SearchQuery(term)

    if sq.querytype == u"source":
        if sq.isregex:
            def filterfun(record):
                return re.search(sq.query, strip(record.source))
            return itertools.ifilter(filterfun, records)
        else:
            search_query = settings.normalize(sq.query)
            if search_query.strip() == "*":
                return records
            def filterfun(record):
                return search_query in record.source_cmp
            return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"trans":
        if sq.isregex:
            def filterfun(record):
                return re.search(sq.query, strip(record.trans))
            return itertools.ifilter(filterfun, records)
        else:
            search_query = settings.normalize(sq.query)
            if search_query.strip() == "*":
                return records
            def filterfun(record):
                return search_query in record.trans_cmp
            return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"context":
        if sq.isregex:
            def filterfun(record):
                return re.search(sq.query, strip(record.context))
            return itertools.ifilter(filterfun, records)
        else:
            normalize = settings.normalize
            search_query = normalize(sq.query)
            if search_query.strip() == "*":
                return records
            def filterfun(record):
                return search_query in normalize(record.context)
            return itertools.ifilter(filterfun, records)

    # created
    elif sq.querytype == u"created-by":
        if sq.isregex:
            def filterfun(record):
                return re.search(sq.query, record.created_by)
            return itertools.ifilter(filterfun, records)
        else:
            search_query = sq.query.lower()
            if search_query.strip() == "*":
                return records
            def filterfun(record):
                "Local filter function"
                return search_query in record.created_by.lower()
            return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"created-before":
        search_query = term_to_date(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.date_created < search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"created-after":
        search_query = term_to_date(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.date_created > search_query
        return itertools.ifilter(filterfun, records)

    # modified
    elif sq.querytype == u"modified-by":
        if sq.isregex:
            def filterfun(record):
                return re.search(sq.query, record.modified_by)
            return itertools.ifilter(filterfun, records)
        else:
            search_query = sq.query.lower()
            if search_query.strip() == "*":
                return records
            def filterfun(record):
                "Local filter function"
                return search_query in record.modified_by.lower()
            return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"modified-before":
        search_query = term_to_date(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.last_modified < search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"modified-after":
        search_query = term_to_date(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.last_modified > search_query
        return itertools.ifilter(filterfun, records)

    # reliability
    elif sq.querytype == u"reliability-gt":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.reliability > search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"reliability-gte":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.reliability >= search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"reliability-lt":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.reliability < search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"reliability-lte":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.reliability <= search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"reliability":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.reliability == search_query
        return itertools.ifilter(filterfun, records)

    # validated
    elif sq.querytype == u"validated":
        search_query = sq.query.lower()
        validated = dict(true=True,
                         false=False).get(search_query, False)
        def filterfun(record):
            "Local filter function"
            return record.validated == validated
        return itertools.ifilter(filterfun, records)

    # ref_count
    elif sq.querytype == u"refcount":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.ref_count == search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"refcount-gt":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.ref_count > search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"refcount-gte":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.ref_count >= search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"refcount-lt":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.ref_count < search_query
        return itertools.ifilter(filterfun, records)

    elif sq.querytype == u"refcount-lte":
        search_query = int(sq.query)
        def filterfun(record):
            "Local filter function"
            return record.ref_count <= search_query
        return itertools.ifilter(filterfun, records)

    # general
    if sq.isregex:
        def filterfun(record):
            in_source = re.search(sq.query, strip(record.source))
            in_trans = re.search(sq.query, strip(record.trans))
            return in_source or in_trans
        return itertools.ifilter(filterfun, records)
    else:
        search_query = settings.normalize(sq.query)
        if search_query == u"*":
            return records
        def filterfun(record):
            "Local filter function"
            return search_query in record.source_cmp or search_query in record.trans_cmp
        return itertools.ifilter(filterfun, records)


def do_replacement(context):
    """
    Perform a replacement in search and replace
    """

    result = model.MemoryRecord(**model.rec2d(context["found"]))
    replacefrom = context["replacefrom"]
    replaceto = context["replaceto"]

    fromquery = SearchQuery(replacefrom)
    toquery = SearchQuery(replaceto)

    if fromquery.querytype in u"source trans".split():
        key = fromquery.querytype

        if fromquery.isregex:
            tochange = getattr(result, key)
            changed = re.sub(fromquery.query,
                             toquery.query,
                             tochange)
            setattr(result, key, changed)
            norm_changed = settings.normalize(changed)
            setattr(result, key + "_cmp", norm_changed)
            return result


        else:
            search_query = fromquery.query
            if search_query == u"*":
                setattr(result, key, replaceto)
            else:
                setattr(result, key, getattr(result, key).replace(search_query,
                                                                  replaceto))
            setattr(result, key + "_cmp", settings.normalize(getattr(result,
                                                                     key)))
            return result

    if fromquery.querytype in u"context created-by modified-by".split():
        key = fromquery.querytype
        key = key.replace(u"-", u"_")

        if fromquery.isregex:
            tochange = getattr(result, key)
            changed = re.sub(fromquery.query,
                             toquery.query,
                             tochange)
            setattr(result, key, changed)
            return result
        else:
            search_query = replacefrom[len(key)+1:]
            if search_query == u"*":
                setattr(result, key, replaceto)
            else:
                setattr(result, key, (getattr(result, key).replace(search_query,
                                                                   replaceto)))
            return result

    # created
    if replacefrom.startswith(u"created:"):
        result.date_created = term_to_date(replaceto)
        return result

    # modified
    if replacefrom.startswith(u"modified:"):
        result.last_modified = term_to_date(replaceto)
        return result

    # reliability
    elif replacefrom.startswith(u"reliability:"):
        result.reliability = int(replaceto)
        return result

    # validated
    elif replacefrom.startswith(u"validated:"):
        validated = dict(true=True,
                         false=False).get(replaceto, False)
        result.validated = validated
        return result

    # ref_count
    elif replacefrom.startswith(u"refcount:"):
        result.ref_count = int(replaceto)
        return result

    # general
    key = fromquery.querytype

    if fromquery.isregex:
        #source
        result.source = re.sub(fromquery.query,
                         toquery.query,
                         result.source)
        result.source_cmp = settings.normalize(result.source)

        # trans
        result.trans = re.sub(fromquery.query,
                         toquery.query,
                         result.trans)
        result.trans_cmp = settings.normalize(result.trans)

        return result

    else:
        result.source = result.source.replace(replacefrom, replaceto)
        result.trans = result.trans.replace(replacefrom, replaceto)

        result.source_cmp = settings.normalize(result.source)
        result.trans_cmp = settings.normalize(result.trans)

        return result
