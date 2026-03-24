#coding: UTF-8
"""
Class for /records/ on website
"""

import cherrypy
import cherrybase
import settings
from presentation import render
import simplejson
import model
import api


def set_memtype(memory, context):
    if memory.mem["memtype"] == u"m":
        context["dirname"] = "memories"
        context["memtype"] = "Memory"
    else:
        context["dirname"] = "glossaries"
        context["memtype"] = "Glossary"

class Records(object):
    """Web interface to records in database"""

    def __init__(self):
        pass

    @cherrybase.requires_priv("rec_read")
    @cherrypy.expose
    def view(self, memid, recid, page=0):
        """View a record"""

        memid = int(memid)
        recid = int(recid)

        memory = model.Data.memories[memid]
        record = model.rec_by_id(memory, recid)

        context = cherrybase.init_context()
        context["title"] = "Memory Serves :: Records :: View"
        context["record"] = record
        context["mem_id"] = memid
        set_memtype(memory, context)
        context["page"] = page

        return render("records/view.html", context)

    @cherrybase.requires_priv("site_admin")
    @cherrypy.expose
    def edit(self, memid, recid, page=0):
        """
        edit a record
        """

        recid = int(recid)
        memid = int(memid)
        memory = model.Data.memories[memid]
        record = model.rec_by_id(memory, recid)

        context = cherrybase.init_context()
        context["title"] = "Memory Serves :: Records :: Edit"

        context["record"] = record
        context["mem_id"] = memid
        set_memtype(memory, context)
        context["page"] = page

        return render("records/edit.html", context)

    @cherrybase.requires_priv("rec_create")
    @cherrypy.expose
    def add(self, memid):
        """
        add a record
        """

        memid = int(memid)

        context = cherrybase.init_context()
        context["title"] = "Memory Serves :: Records :: Add"

        memory = model.Data.memories[memid]
        context["mem_name"] = memory.mem["name"]
        set_memtype(memory, context)
        context["mem_id"] = memid


        return render("records/add.html", context)

    @cherrybase.requires_priv("rec_update")
    @cherrypy.expose
    def editinplace(self, memid, recid, **kwds):
        """
        submit target for in-place edit page.
        Updates record based on form values.
        """

        recid = int(recid)
        memid = int(memid)
        memory = model.Data.memories[memid]
        record = model.rec_by_id(memory, recid)

        if not kwds.get("last_modified"):
            kwds["last_modified"] = model.get_now()
        if not kwds.get("modified_by"):
            kwds["modified_by"] = cherrybase.get_username(cherrypy.session)

        settings.normalize = settings.make_normalizer(settings.get_prefs())

        memory.remove_record(record)
        record.update(kwds)
        memory.add_record(record)

        message = """<div class="success">
                         Edited record with id %s
                         </div>""" % record.id

        data = model.rec2d(record)
        data["date_created"] = str(data["date_created"])
        data["last_modified"] = str(data["last_modified"])
        data["validated"] = str(data["validated"])
        data["message"] = message

        cherrypy.response.headers['Content-Type'] = 'application/json'
        return simplejson.dumps(data)


    @cherrybase.requires_priv("rec_update")
    @cherrypy.expose
    def submitedit(self, memid, recid, **kwds):
        """
        submit target for edit page.
        Updates record based on form values.
        """

        recid = int(recid)
        memid = int(memid)
        memory = model.Data.memories[memid]
        record = model.rec_by_id(memory, recid)

        if not kwds.get("last_modified"):
            kwds["last_modified"] = model.get_now()
        if not kwds.get("modified_by"):
            kwds["modified_by"] = cherrybase.get_username(cherrypy.session)

        settings.normalize = settings.make_normalizer(settings.get_prefs())

        memory.remove_record(record)
        record.update(kwds)
        memory.add_record(record)

        cherrybase.add_message("""<div class="success">
                         Edited record
                         </div>""")

        raise cherrypy.HTTPRedirect("/records/view/%s/%s" % (memid, recid))

    @cherrybase.requires_priv("rec_create")
    @cherrypy.expose
    def submitadd(self, memid, **record):
        """
        submit target for add-record page.
        Updates record based on form values.
        """

        record["date_created"] = record["last_modified"] = model.get_now()
        record["created_by"] = record["modified_by"] = cherrybase.get_username(cherrypy.session)

        memid = int(memid)

        memory = model.Data.memories[memid].mem
        records = memory["records"]

        rec = model.MemoryRecord(**record)
        rec.memory_id = memid
        rec.id = model.get_next_recid()
        key = model.MAKE_KEY(rec)
        records[key] = rec

        cherrybase.add_message("""<div class="success">
                         Added record
                         </div>""")

        raise cherrypy.HTTPRedirect("/records/view/%s/%s" % (memid, rec.id))


    @cherrybase.requires_priv("rec_delete")
    @cherrypy.expose
    def delete(self, memid, recid, next):
        """
        Delete the record with the specified ID

        - :memid: The ID of the memory
        - :recid: The ID of the record to delete
        - :next: The URL to navigate to next. Relative to root.
        """

        recid = int(recid)
        memid = int(memid)
        memory = api.get_mem_by_id(memid)
        if not memory:
            cherrybase.log_mem_failure(memid)
            cherrybase.feedback_error("Memory/Glossary not found")
            raise cherrypy.HTTPRedirect(next)

        record = model.rec_by_id(memory, recid)

        if not record:
            cherrybase.feedback_error("Record not found")
            raise cherrypy.HTTPRedirect(next)

        memory.remove_record(record)

        cherrybase.add_message("""<div class="success">
                         Deleted record
                         </div>""")
        while next.endswith("/"):
            next = next[:-1]
        raise cherrypy.HTTPRedirect(next)
