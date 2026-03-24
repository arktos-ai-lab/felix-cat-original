#!/usr/bin/env python
import cherrypy

import model
from model import get_all_records
import cherrybase

from cherrybase import set_results_message
from presentation import format_num, render
from operator import attrgetter
import datetime
import cgi

import search
from search import term_to_date, refine_replacefrom, refine_query, do_replacement
from search import get_queryfilters, make_querylink, smooth_queryfilters, exclude
from search import set_pagination
from search import ensure_u


class GlobalSearch(object):
    """
    Handler for global searches
    """

    @cherrypy.expose
    def index(self, page="1", tofind="", queryfilters=None):
        """
        Search the memory or glossary
        """

        page = int(page)
        queryfilters = get_queryfilters(tofind, queryfilters)

        tofind = ensure_u(tofind)

        records = get_all_records()

        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)

        records = list(records)
        if queryfilters:
            set_results_message(len(records))

        context = cherrybase.init_context()
        self.set_querylinks(context, queryfilters)
        context["search"] = tofind

        context = set_pagination(context, page, len(records))

        if queryfilters:
            context["records"] = search.slice_recs(records, context)
            for record in context["records"]:
                mem = model.Data.memories.get(record.memory_id)
                if mem:
                    memdict = mem.mem
                    record.mem = memdict
                else:
                    record.mem = dict(memtype="m", id=0, name="")

        else:
            context["records"] = []

        return render("search/globalsearch.html", context)

    @cherrypy.expose
    def replace(self, queryfilters=None):
        """
        Search and replace in the repo
        """

        print "Replace"
        queryfilters = queryfilters or []

        records = get_all_records()

        queryfilters = smooth_queryfilters(queryfilters)

        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)

        context = cherrybase.init_context()
        mql = make_querylink

        context["queryfilters"] = [dict(term=qf,
                                        removelink=mql(exclude(qf,
                                                               queryfilters)))
                                   for qf in queryfilters]

        context["replacefrom"] = u""
        context["replaceto"] = u""
        context["nth_item"] = "0"

        return render("search/globalreplace.html", context)

    @cherrypy.expose
    def replace_find(self,
                     replacefrom="",
                     replaceto="",
                     queryfilters=None,
                     nth_item="0"):
        """Find the next match in the repo"""

        print "Replace-find"
        nth_item = int(nth_item)

        records = get_all_records()

        queryfilters = smooth_queryfilters(queryfilters or [])

        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)
        records = refine_replacefrom(records, ensure_u(replacefrom))

        records = (record for record in records if record.id > nth_item)
        records = list(sorted(records, key=attrgetter("id")))
        if records:
            found = records[0]
        else:
            found = None

        if not found:
            cherrybase.feedback_info("""No more matches""")
            print " ... handing back to replace"
            return self.replace(queryfilters)

        context = cherrybase.init_context()

        context["replacefrom"] = ensure_u(replacefrom)
        context["replaceto"] = ensure_u(replaceto)
        context["found"] = found

        context["nth_item"] = found.id
        context["result"] = do_replacement(context)
        print " ... found:", found.id

        context["num_matches"] = len(records)

        queryfilters = [cgi.escape(qf) for qf in queryfilters]
        mql = make_querylink
        context["queryfilters"] = [dict(term=qf,
                                        removelink=mql(exclude(qf,
                                                               queryfilters)))
                                   for qf in queryfilters]

        return render("search/globalreplace.html", context)

    @cherrypy.expose
    def replace_replace(self,
                        replacefrom="",
                        replaceto="",
                        queryfilters=None,
                        nth_item="0"):
        """
        Replace a single record in the repo
        """

        print "Replace-replace"

        nth_item = int(nth_item)

        found = model.global_rec_by_id(model.Data.memories.itervalues(), nth_item)

        if not found:
            cherrybase.feedback_error("No more records found with these criteria")
            path = "/globalsearch/replace/"
            raise cherrypy.HTTPRedirect(path)

        mem = model.Data.memories[found.memory_id]

        context = cherrybase.init_context()
        context["replacefrom"] = ensure_u(replacefrom)
        context["replaceto"] = ensure_u(replaceto)
        context["found"] = found

        oldkey = (found.source, found.trans)

        result = do_replacement(context)

        key = (result.source, result.trans)

        dup = mem.mem["records"].get(key)
        if dup and dup.id != result.id:
            print "Found duplicate record"
            msg = """There was another record with the same information.
                    Replaced with your changes."""
            cherrybase.feedback_info(msg)
        else:
            cherrybase.feedback_info("""Made replacement""")

        mem.remove_record(found)
        mem.add_record(result)

        if found.last_modified == result.last_modified:
            result.last_modified = datetime.datetime.now()

        return self.replace_find(replacefrom, replaceto, queryfilters, nth_item)

    @cherrypy.expose
    def replace_all(self,
                    replacefrom="",
                    replaceto="",
                    queryfilters=None,
                    nth_item=0):
        """
        Replace all instances in the repo
        """

        nth_item = int(nth_item)
        records = get_all_records()

        queryfilters = smooth_queryfilters(queryfilters or [])
        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)
        records = refine_replacefrom(records, ensure_u(replacefrom))
        records = list(records)

        replaceto = ensure_u(replaceto)

        if replaceto == u"action:delete":
            for result in records:
                mem = model.Data.memories.get(result.memory_id)
                if not mem:
                    cherrybase.log_mem_failure(result.memory_id)
                else:
                    if not mem.remove_record(result):
                        cherrybase.log_warning("Record not found in memory")
            cherrybase.feedback_info("Deleted %s records" % len(records))
        else:
            for found in records:
                context = {}
                context["replacefrom"] = ensure_u(replacefrom)
                context["replaceto"] = replaceto
                context["found"] = found

                oldkey = (found.source, found.trans)
                result = do_replacement(context)
                key = (result.source, result.trans)

                mem = model.Data.memories.get(found.memory_id)
                if not mem:
                    cherrybase.log_mem_failure(found.memory_id)
                else:
                    mem.remove_record(found)
                    mem.add_record(result)

                if found.last_modified == result.last_modified:
                    result.last_modified = datetime.datetime.now()

            cherrybase.feedback_info("Made %s replacements" % len(records))
        path = "/globalsearch/replace/"
        raise cherrypy.HTTPRedirect(path)

    @cherrypy.expose(alias="search-help")
    def search_help(self):
        """Show the search help"""
        context = cherrybase.init_context(title="Search Help :: Memory Serves")
        return render("search/help.html", context)

    def set_querylinks(self, context, queryfilters):
        mql = make_querylink
        context["queryfilters"] = [dict(term=qf,
                                        removelink=mql(exclude(qf,
                                                               queryfilters)))
                                   for qf in queryfilters]
        context["replacelink"] = mql([x.encode("utf-8") for x in queryfilters])[1:]

    @cherrypy.expose
    def download(self, queryfilters):
        """
        Download records matching our search criteria
        """
        queryfilters = get_queryfilters("", queryfilters)
        records = get_all_records()

        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)

        records = list(records)

        context = cherrybase.init_context()
        get_user = cherrybase.get_username
        context["item"] = dict(creator=get_user(cherrypy.session),
                               created_on=model.get_now())
        context["truther"] = search.mem_truther
        context["is_memory"] = "true"
        context["replacer"] = cherrybase.replacer
        context["to_date"] = cherrybase.to_date
        context["records"] = sorted(records, key=attrgetter("id"))
        context["num_records"] = len(records)

        content = render("memory.xml", context)

        cherrypy.response.headers['Content-Type'] = 'application/xml'
        cherrypy.response.headers['Content-Length'] = len(content)
        disp = 'attachment; filename=%s' % search.make_xml_filename("search_results", True)
        cherrypy.response.headers['Content-Disposition'] = disp
        cherrypy.response.headers['filename'] = 'application/xml'
        cherrypy.response.headers['pragma'] = ""
        cherrypy.response.headers['content-cache'] = ""

        return content
