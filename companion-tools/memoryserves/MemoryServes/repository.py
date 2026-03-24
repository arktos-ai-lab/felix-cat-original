# coding: UTF-8
"""
Represents the repository web API.
"""

import cgi
import datetime
import itertools
import logging
from operator import attrgetter

import cherrypy

import TMX.writer

import loc
import settings
import model
from model import Memory
import dataloader
import site_records

from mem_parser import get_root, get_head, get_records

import search
from search import refine_replacefrom, refine_query, do_replacement
from search import set_pagination
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

__author__ = 'Ryan'

DEFAULT_CODE = (("--Select Language--", "Default"),)
logger = logging.getLogger(__name__)


def set_is_memory(item, context):
    """
    Set the memory value for a TM
    """

    if item.mem["memtype"] == u"m":
        is_memory = "true"
    else:
        is_memory = "false"
    context["is_memory"] = is_memory


def create_download_file(item):
    """
    Create a memory/glossary for download
    """

    context = cherrybase.init_context(item=item.mem)
    context["num_records"] = len(item.mem["records"])
    context["truther"] = search.mem_truther
    set_is_memory(item, context)
    context["replacer"] = cherrybase.replacer
    context["to_date"] = cherrybase.to_date
    context["records"] = sorted(item.mem["records"].itervalues(),
                                key=attrgetter("id"))
    content = render("memory.xml", context)
    return content


def reflect_one_trans(one_trans):
    """
    Reflect the setting of "one translation per source."
    """

    if one_trans:
        model.MAKE_KEY = model.make_key_source
    else:
        model.MAKE_KEY = model.make_key_both


class Repository(object):
    """
    Base class for both Memory and Glossary subdirs
    """
    title_string = None

    def __init__(self, memtype):
        self.memtype = memtype

    def create_memory(self, name, data):
        """
        Create a new TM/glossary on Memory Serves
        """

        memtype = self.memtype[0]
        mem = Memory(name=name,
                     memtype=memtype,
                     **data)
        memid = model.get_next_memid()
        mem.id = memid
        mem.records = []
        mem = model.mem2d(mem)
        model.Data.memories[memid] = model.TranslationMemory(mem)
        return model.Data.memories[memid]

    def add_repo(self, source):
        """
        Add an uploaded file as a memory/glossary
        """

        item = dict(name=ensure_u(source.filename))

        root = get_root(source.file)

        head = get_head(root)

        try:
            head["creator"] = ensure_u(head["creator"])
        except (TypeError, KeyError):
            pass

        prefs = settings.get_prefs()

        head.update(prefs)
        mem = self.create_memory(item["name"], head)

        memid = int(mem.mem["id"])
        next_recid = model.get_next_recid
        for record in get_records(root):
            if "id" in record:
                del record["id"]
            rec = model.MemoryRecord(**record)
            rec.memory_id = memid
            rec.id = next_recid()
            mem.add_record(rec)

        item["id"] = memid
        item["memtype"] = mem.mem["memtype"]
        cherrybase.add_message(self.create_add_msg(item, head))

        return item

    def create_add_msg(self, item, head):
        """
        Create the feedback for adding a memory
        """

        msg = """<div class="success">
            Added %s: %s<br />""" % (self.memtype.encode("utf-8"),
                                     item["name"].encode("utf-8"))

        msg += "<br />".join(["%s : %s" % pair for pair in head.items()])
        if item["memtype"] == u"m":
            dirname = "memories"
            memname = "Memory"
        else:
            dirname = "glossaries"
            memname = "Glossary"

        msg_fmt = '<p><a href="/%s/view/%s" style="color:blue">View %s</a></p>'
        msg += msg_fmt  % (dirname, item["id"], memname)
        msg += "</div>"

        return msg

    def delete_item(self, memid):
        """
        Delete memory with id memid
        """
        del model.Data.memories[memid]

    def get_item(self, memid):
        """
        Get the memory with the specified ID
        """
        return model.Data.memories.get(int(memid))

    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose
    def view(self, memid):
        """
        View a specific memory or glossary
        """

        context = cherrybase.init_context()
        self.set_dirname(context)

        memory = self.get_item(int(memid))
        if not memory:
            cherrybase.feedback_error("Memory with id %s not found" % memid)
            raise cherrypy.HTTPRedirect("/%s/" % context["dirname"])

        memory = memory.mem

        title_info = dict(repotype=self.title_string)
        title_info.update(memory)

        title = "Memory Serves :: %(repotype)s :: View :: %(name)s" % title_info
        context["title"] = title
        item = dict(**memory)
        item["validated"] = int(model.percent_validated(memory)*100)
        low, high, ave = model.reliability_stats(memory)
        item["reliability"] = dict(low=low, high=high, ave="%.3f" % ave)
        context["item"] = item
        context["num"] = format_num(len(memory["records"]))
        context["format"] = format_num
        context["host"] = settings.get_host()
        context["port"] = settings.get_port()

        return render("view.html", context)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def merge(self, memid):
        """
        Upload and merge a memory/glossary file with this one
        """

        logger.info("Merging TM")
        context = cherrybase.init_context()
        self.set_dirname(context)

        memory_holder = self.get_item(int(memid))
        if not memory_holder or not memory_holder.mem:
            cherrybase.feedback_error("Memory with id %s not found" % memid)
            raise cherrypy.HTTPRedirect("/%s/" % context["dirname"])

        memory = memory_holder.mem

        title_info = dict(repotype=self.title_string)
        title_info.update(memory)

        title = "Memory Serves :: %(repotype)s :: Merge :: %(name)s" % title_info
        context["title"] = title
        item = dict(**memory)
        item["validated"] = int(model.percent_validated(memory)*100)
        low, high, ave = model.reliability_stats(memory)
        item["reliability"] = dict(low=low, high=high, ave="%.3f" % ave)
        context["item"] = item
        context["num"] = format_num(len(memory["records"]))
        context["format"] = format_num
        context["host"] = settings.get_host()
        context["port"] = settings.get_port()

        context["mem_gloss_type"] = self.type_name

        logger.debug("Rendering merger.html")
        return render("merge.html", context)


    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose(alias="list-mems")
    def index(self):
        """
        List of all memories/glossaries
        """

        context = cherrybase.init_context()
        title = "Memory Serves :: %s" % self.title_string
        context["title"] = title
        memtype = self.memtype[0]
        context["items"] = [m.mem
                            for m in model.Data.memories.itervalues()
                            if m.mem["memtype"] == memtype]
        # ensure that all items have ids
        for item in context["items"]:
            if not item.get('id'):
                item['id'] = model.get_next_memid()
        context["format"] = format_num
        context["host"] = settings.get_host()
        context["port"] = settings.get_port()

        return render("%s/index.html" % self.title_string.lower(), context)

    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose
    def browse(self, memid, page):
        """
        Browse the records in the repo
        """

        # page must be at least 1
        page = max(int(page), 1)

        memid = int(memid)
        item = self.get_item(memid).mem
        context = cherrybase.init_context()
        context["item"] = item
        title = u" :: ".join([u"Memory Serves",
                             self.title_string,
                             u"Browse",
                             item["name"],
                             u"Page %s" % page])
        context["title"] = title

        records = item["records"].itervalues()

        start = (page-1) * search.PAGE_SIZE
        stop = start+search.PAGE_SIZE
        context = set_pagination(context, page, len(item["records"]))

        context["records"] = list(itertools.islice(records, start, stop))
        self.set_dirname(context)

        return render("browse.html", context)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def replace(self, memid, queryfilters=None):
        """
        Search and replace in the repo
        """

        logger.info("Replace")
        queryfilters = queryfilters or []

        memory = self.get_item(int(memid)).mem
        records = memory["records"].itervalues()

        queryfilters = search.smooth_queryfilters(queryfilters)

        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)

        context = cherrybase.init_context()
        context["item"] = memory
        context["title"] = self.title_string
        mql = search.make_querylink

        context["queryfilters"] = [dict(term=qf,
                                        removelink=mql(search.exclude(qf,
                                                               queryfilters)))
                                   for qf in queryfilters]

        context["replacefrom"] = u""
        context["replaceto"] = u""
        context["nth_item"] = "0"

        self.set_dirname(context)

        return render("search/replace.html", context)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def replace_find(self,
                     memid,
                     replacefrom="",
                     replaceto="",
                     queryfilters=None,
                     nth_item="0"):
        """
        Find the next match in the repo
        """

        logger.info("Replace-find")
        nth_item = int(nth_item)

        memory = self.get_item(int(memid)).mem

        records = memory["records"].itervalues()

        queryfilters = search.smooth_queryfilters(queryfilters or [])

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
            logger.debug(" ... handing back to replace")
            return self.replace(memid, queryfilters)

        context = cherrybase.init_context()
        context["item"] = memory
        context["title"] = self.title_string

        context["replacefrom"] = ensure_u(replacefrom)
        context["replaceto"] = ensure_u(replaceto)
        context["found"] = found

        context["nth_item"] = found.id
        context["result"] = do_replacement(context)
        logger.debug(" ... found: %s" % found.id)

        context["num_matches"] = len(records)

        queryfilters = [cgi.escape(qf) for qf in queryfilters]
        mql = search.make_querylink
        context["queryfilters"] = [dict(term=qf,
                                        removelink=mql(search.exclude(qf,
                                                               queryfilters)))
                                   for qf in queryfilters]

        self.set_dirname(context)

        return render("search/replace.html", context)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def replace_replace(self,
                        memid,
                        replacefrom="",
                        replaceto="",
                        queryfilters=None,
                        nth_item="0"):
        """
        Replace a single record in the repo
        """

        logger.info("Replace-replace")

        nth_item = int(nth_item)
        memid = int(memid)
        mem = self.get_item(memid)

        if not mem:
            cherrybase.feedback_error("Memory with id %s not found" % memid)
            path = "/%s/" % self.get_dirname()
            raise cherrypy.HTTPRedirect(path)

        found = model.rec_by_id(mem, nth_item)

        if not found:
            cherrybase.feedback_error("No more records found with these criteria")
            path = "/%s/replace/%s" % (self.get_dirname(), memid)
            raise cherrypy.HTTPRedirect(path)

        context = cherrybase.init_context()
        context["replacefrom"] = ensure_u(replacefrom)
        context["replaceto"] = ensure_u(replaceto)
        context["found"] = found

        result = do_replacement(context)

        key = (result.source, result.trans)

        dup = mem.mem["records"].get(key)
        if dup and dup.id != result.id:
            logger.info("Found duplicate record: %s" % dup)
            cherrybase.feedback_info("""There was another record with the
                            same information. Replaced with your changes.""")
        else:
            cherrybase.feedback_info("""Made replacement""")

        mem.remove_record(found)
        mem.add_record(result)

        if found.last_modified == result.last_modified:
            result.last_modified = datetime.datetime.now()

        return self.replace_find(memid,
                                 replacefrom,
                                 replaceto,
                                 queryfilters,
                                 nth_item)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def replace_all(self,
                    memid,
                    replacefrom="",
                    replaceto="",
                    queryfilters=None,
                    nth_item=0):
        """
        Replace all instances in the repo
        """

        nth_item = int(nth_item)
        memid = int(memid)
        mem = model.Data.memories[memid].mem
        records = mem["records"].itervalues()

        queryfilters = search.smooth_queryfilters(queryfilters or [])
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

                del mem["records"][oldkey]
                mem["records"][key] = result

                if found.last_modified == result.last_modified:
                    result.last_modified = datetime.datetime.now()

            cherrybase.feedback_info("Made %s replacements" % len(records))
        path = "/%s/replace/%s" % (self.get_dirname(), memid)
        raise cherrypy.HTTPRedirect(path)

    @cherrypy.expose(alias="search-help")
    def search_help(self):
        """
        Show the search help
        """
        context = cherrybase.init_context(title="Search Help :: Memory Serves")
        return render("search/help.html", context)

    def get_search_results(self, memid, queryfilters):
        """
        Generic method to get search results for given query terms
        """

        memory = self.get_item(int(memid)).mem
        if not memory:
            cherrybase.log_info(u"Memory id %s does not exist" % memid)
            records = []
        else:
            records = memory["records"].itervalues()

        for queryfilter in queryfilters:
            records = refine_query(records, queryfilter)

        return list(records)


    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose
    def searchdownload(self, memid, queryfilters):
        """
        Download matching entries
        """
        queryfilters = search.get_queryfilters("", queryfilters)
        records = self.get_search_results(memid, queryfilters)
        logger.info("Search results: %s" % len(records))
        memory = self.get_item(int(memid))

        context = cherrybase.init_context()
        get_user = cherrybase.get_username
        context["item"] = dict(creator=get_user(cherrypy.session),
                               created_on=model.get_now())
        context["truther"] = search.mem_truther
        set_is_memory(memory, context)
        context["replacer"] = cherrybase.replacer
        context["to_date"] = cherrybase.to_date
        context["records"] = sorted(records, key=attrgetter("id"))
        context["num_records"] = len(records)
        content = render("memory.xml", context)

        filename = search.make_xml_filename("search_results", True)
        self.set_download_headers(cherrypy.response.headers, content, filename)

        return content

    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose
    def search(self, memid, page="1", tofind="", queryfilters=None):
        """
        Search the memory or glossary
        """

        logger.info("Search")

        page = int(page)
        queryfilters = search.get_queryfilters(tofind, queryfilters)

        records = self.get_search_results(memid, queryfilters)

        if queryfilters:
            set_results_message(len(records))

        context = cherrybase.init_context()
        context["item"] = self.get_item(int(memid)).mem
        context["title"] = self.title_string
        mql = search.make_querylink
        context["queryfilters"] = [dict(term=qf,
                                        removelink=mql(search.exclude(qf,
                                                               queryfilters)))
                                   for qf in queryfilters]
        context["replacelink"] = mql([x.encode("utf-8")
                                      for x in queryfilters])
        context["search"] = ensure_u(tofind)

        context = set_pagination(context, page, len(records))

        if queryfilters:
            context["records"] = search.slice_recs(records, context)
        else:
            context["records"] = []
        self.set_dirname(context)

        logger.debug("Rendering search/search.html")
        return render("search/search.html", context)


    def get_dirname(self):
        """
        Get the base directory name based on the memory type
        """
        if self.memtype.lower().startswith(u"m"):
            return "memories"
        else:
            return "glossaries"

    def set_dirname(self, context):
        """
        Set whether the dirname is memories or glossaries
        """
        context["dirname"] = self.get_dirname()

    @cherrybase.requires_priv("tm_create")
    @cherrypy.expose
    def create(self):
        """
        /memories/create
        """

        context = cherrybase.init_context()
        title = "Memory Serves :: Create %s" % self.title_string
        context["title"] = title
        context["typename"] = self.memtype.capitalize()

        return render("create_repo.html", context)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def edit(self, memid):
        """
        /memories/edit

        Edit the info for the TM/glossary
        """

        context = cherrybase.init_context()
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to delete %s.
                             </div>""" % self.title_string.lower())
            title = self.title_string.lower()
            raise cherrypy.HTTPRedirect("/%s/view/%s" % (title,
                                                         memid))

        item = self.get_item(int(memid)).mem

        context = cherrybase.init_context()
        title = self.title_string
        context["title"] = "Memory Serves :: Edit %s" % title
        context["item"] = item
        context["typename"] = self.memtype.capitalize()

        return render("edit_repo.html", context)

    @cherrybase.requires_priv("tm_delete")
    @cherrypy.expose
    def delete(self, memid):
        """
        Delete the memory/glossary with the specified ID
        """

        context = cherrybase.init_context()
        if not context["is_admin"]:
            cherrybase.add_message("""<div class="error">
                             You must be an admin to delete %s.
                             </div>""" % self.title_string.lower())
            title = self.title_string.lower()
            raise cherrypy.HTTPRedirect("/%s/view/%s" % (title,
                                                         memid))

        name = self.get_item(int(memid)).mem["name"]
        self.delete_item(int(memid))
        cherrybase.add_message("""<div class="success">
                         Deleted memory %s (id: %s)
                         </div>""" % (name, memid))

        cherrybase.log_info(u"Deleted memory %s" % name)

        raise cherrypy.HTTPRedirect("/%s/" % self.title_string.lower())

    def set_download_headers(self, headers, content, filename):
        headers['Content-Type'] = 'application/xml'
        headers['Content-Length'] = len(content)
        disp = 'attachment; filename=%s' % filename
        headers['Content-Disposition'] = disp
        headers['filename'] = 'application/xml'
        headers['pragma'] = ""
        headers['content-cache'] = ""

    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose
    def download(self, memid):
        """
        Download the specified memory/glossary as a Felix XML file
        """

        item = self.get_item(int(memid))
        content = create_download_file(item)

        filename = search.make_xml_filename(item.mem["name"], item.mem["memtype"] == "m")
        self.set_download_headers(cherrypy.response.headers, content, filename)

        return content

    @cherrybase.requires_priv("tm_read")
    @cherrypy.expose(alias="download-tmx")
    def download_tmx(self, memid):
        """
        Download a TMX file
        """

        item = self.get_item(int(memid)).mem

        sourcelang = item.get("source_language")
        translang = item.get("target_language")

        logger.info("source language: %s" % sourcelang)
        logger.info("target language: %s" % translang)

        src_code, trans_code = get_codes(sourcelang, translang)
        logger.info("src_code: %s" % src_code)
        logger.info("trans_code: %s" % trans_code)

        if not src_code or not trans_code:
            context = cherrybase.init_context(title="Select Languages for TMX file :: Memory Serves")
            context["languages"] = LANG_CODES
            context["item"] = item
            context["dirname"] = self.get_dirname()
            return render("download_tmx.html", context)

        content = self.make_tmx_download(item)
        if sourcelang:
            item["source_language"] = sourcelang
        if translang:
            item["target_language"] = translang
        return content

    def make_tmx_download(self, item):
        """
        Create a TMX file for download
        """

        sourcelang = item.get("source_language")
        translang = item.get("target_language")

        src_code, trans_code = get_codes(sourcelang, translang)
        item["source_language"] = src_code
        item["target_language"] = trans_code

        filename = search.make_tmx_filename(item["name"])

        filename = ensure_u(filename)
        logger.info("Downloading file: %s" % filename.encode("utf-8"))

        content = TMX.writer.create_tmx(item, (model.rec2d(r) for r in item["records"].itervalues()))
        self.set_download_headers(cherrypy.response.headers, content, filename)

        return content

    @cherrybase.requires_priv("tm_create")
    @cherrypy.expose
    def submittmx(self, memid, source, trans):
        """
        Download as a TMX file
        """

        item = self.get_item(int(memid)).mem

        if source == "Default" or trans == "Default":
            cherrybase.feedback_error("Please select source and translation languages")
            context = cherrybase.init_context(title="Select Languages for TMX file :: Memory Serves")
            context["languages"] = DEFAULT_CODE + LANG_CODES
            context["item"] = item
            context["dirname"] = self.get_dirname()
            return render("download_tmx.html", context)

        item["source_language"] = source
        item["target_language"] = trans

        return self.make_tmx_download(item)

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def submitedit(self, memid, **kwds):
        """
        /memories/submitedit

        Shows add memory form
        """

        item = self.get_item(int(memid)).mem
        for key, val in kwds.items():
            item[key] = model.make_unicode(val)

        cherrybase.add_message("""<div class="success">
                         Edited memory %(name)s
                         </div>""" % item)
        title = self.title_string.lower()
        raise cherrypy.HTTPRedirect("/%s/view/%s" % (title,
                                                     item["id"]))

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def submitcreate(self, **kwds):
        """
        /memories/submitcreate

        handles add memory form submit
        """

        kwds["memtype"] = self.memtype[0]
        kwds["creator"] = cherrybase.get_username(cherrypy.session)
        mem = Memory(**kwds)
        mem.id = model.get_next_memid()
        model.Data.memories[mem.id] = model.TranslationMemory(model.mem2d(mem))

        cherrybase.add_message("""<div class="success">
                         Created memory %s
                         </div>""" % mem.name)
        title = self.title_string.lower()
        raise cherrypy.HTTPRedirect("/%s/view/%s" % (title,
                                                     mem.id))

    @cherrybase.requires_priv("tm_update")
    @cherrypy.expose
    def submitmerge(self, memid, memory_file):
        """Add a new glossary"""

        memid = int(memid)
        memory = self.get_item(memid)

        if not memory_file.filename:
            cherrybase.feedback_error(u"Please select a file to upload")
            title = self.title_string.lower()
            raise cherrypy.HTTPRedirect("/%s/merge/%s" % (title,
                                                         memid))

        memory = memory.mem
        name = ensure_u(memory_file.filename)

        root = get_root(memory_file.file)

        records = memory["records"]
        old_len = len(records)
        next_recid = model.get_next_recid
        for record in get_records(root):
            if "id" in record:
                del record["id"]
            rec = model.MemoryRecord(**record)
            rec.memory_id = memid
            rec.id = next_recid()
            key = model.MAKE_KEY(dict(source=rec.source, trans=rec.trans))
            records[key] = rec

        num_added = len(records) - old_len

        cherrybase.feedback_info(u"Merged %s records from '%s'" % (num_added, name))
        title = self.title_string.lower()
        raise cherrypy.HTTPRedirect("/%s/view/%s" % (title,
                                                     memid))


class Memories(Repository):
    """
    Memory routing class
    """

    def __init__(self):
        Repository.__init__(self, u"memory")
        self.title_string = "Memories"
        self.type_name = "Memory"

    @cherrybase.requires_priv("tm_create")
    @cherrypy.expose
    def add(self, memory_file=None):
        """
        /memories/add

        Shows add memory form
        """

        item = None
        if memory_file is not None:
            try:
                item = self.add_repo(memory_file)
            except (AttributeError, TypeError), details:
                cherrybase.feedback_error(u"Failed to add memory: %s" % details)

        title = "Memory Serves :: Memories :: Add New"
        context = cherrybase.init_context(title=title,
                               item=item)

        return render("memories/add.html", context)


class Glossaries(Repository):
    """
    Controls glossaries
    """

    def __init__(self):
        Repository.__init__(self, u"glossary")
        self.title_string = "Glossaries"
        self.type_name = "Glossary"

    @cherrybase.requires_priv("tm_create")
    @cherrypy.expose
    def add(self, memory_file=None):
        """Add a new glossary"""

        item = None
        try:
            item = self.add_repo(memory_file)
        except (AttributeError, TypeError):
            logger.exception("Error adding glossary")

        title = "Memory Serves :: Glossaries :: Add New"
        context = cherrybase.init_context(title=title,
                               item=item)

        return render("glossaries/add.html", context)