# coding: UTF8
"""
Code for the API class

"""
from __future__ import with_statement

import warnings

warnings.simplefilter("ignore", DeprecationWarning)

import itertools
import cPickle
import uuid

import cherrypy
import edist

import search
from search import ensure_u
import cherrybase
import admin
import settings
from permissions import requires_priv
import model
from model import is_key_valid
from model import rec2d


def gloss_sort_key(record):
    """
    The function for sorting glossary entries.
    """
    return len(record.source_cmp)


def gloss_matches_sorted(matches):
    """
    Get sorted glossary matches.
    """
    return list(reversed(sorted(matches, key=gloss_sort_key)))


def are_different(prefs, mem):
    """
    Are the preferences different from the
    memory settings?
    """
    for key in ["normalize_case", "normalize_hira", "normalize_width"]:
        if prefs[key] != mem.mem[key]:
            return True
    return False


def get_mem_by_id(memid):
    """
    Gets a memory by its ID.
    """

    return model.Data.memories.get(int(memid))


def get_rec_by_id_global(recid):
    """
    Gets a record by its ID, regardless of what memory it's in.
    """

    for mem in model.Data.memories.itervalues():
        for rec in mem.mem["records"].itervalues():
            if rec.id == recid:
                return rec
    return None


def make_query(query):
    """
    Create the query
    """
    return settings.normalize(ensure_u(query))


def make_token():
    '''
    Create a token.
    '''
    return unicode(uuid.uuid1())


class Api(object):
    """
    API for web service
    """

    MAX_NUM_RESULTS = 20

    def __init__(self, base_tmpl="api"):
        self.base = "http://%s:%s/%s" % (settings.get_host(), settings.get_port(), base_tmpl)
        self.MAX_NUM_RESULTS = settings.Settings.MAX_NUM_RESULTS

    def dumps(self, obj):
        """
        Dumps the value as a python pickle object.
        """

        return cPickle.dumps(obj)

    def get_item(self, memid):
        """
        Gets the memory with the specified id
        """

        return get_mem_by_id(memid)

    def synch_prefs_and_mem(self, prefs, mem):
        """
        Synchronizes the memory to the search preferences
        """

        mem.synch_prefs(prefs)

    def ensure_synched(self, prefs, mem):
        """
        Makes sure that the memory is synched to the preferences
        """
        if are_different(prefs, mem):
            self.synch_prefs_and_mem(prefs, mem)

    def get_info(self, memid):
        """Generic memory info method"""

        cherrybase.log_info("Getting info for repo ID %s" % memid)

        mem = self.get_item(int(memid))
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return None

        memdata = mem.mem
        info = {}
        info.update(memdata)
        del info["records"]
        info["size"] = len(memdata["records"])
        info["creator"] = info["creator"] or memdata.get("created_by")
        info["version"] = model.VERSION

        return info

    @requires_priv("tm_create")
    @cherrypy.expose
    def addmem(self, **kwds):
        """
        Add a memory
        """

        mem = model.Memory(**kwds)
        memid = model.get_next_memid()
        mem.id = memid
        model.Data.memories[memid] = model.TranslationMemory(model.mem2d(mem))
        return self.dumps(self.get_info(memid))

    @requires_priv("tm_delete")
    @cherrypy.expose
    def delmem(self, memid, token=None):
        """Delete the memory"""

        memid = int(memid)
        if memid not in model.Data.memories:
            return self.dumps(len(model.Data.memories))

        del model.Data.memories[memid]
        return self.dumps(len(model.Data.memories))

    @requires_priv("tm_read")
    @cherrypy.expose
    def info(self, memid, token=None):
        """Get info for the memory"""
        return self.dumps(self.get_info(int(memid)))

    @cherrypy.expose
    def mems(self, memid):
        """
        Get the memory with the id

        :param memid: The ID of the TM/glossary to connect to
        """

        memid = int(memid)

        cherrybase.log_info("Connecting to repo ID %s" % memid)

        mem = self.get_item(memid)
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        prefs = settings.get_prefs()
        self.ensure_synched(prefs, mem)

        base = self.base
        commands = dict(add="%s/add/%s/" % (base, memid),
                        update="%s/update/" % base,
                        search="%s/search/%s/" % (base, memid),
                        get_page="%s/get_page/%s/" % (base, memid),
                        get_range="%s/getrange/%s/" % (base, memid),
                        num_pages="%s/num_pages/",
                        rsearch="%s/rsearch/%s/" % (base, memid),
                        gloss="%s/gloss/%s/" % (base, memid),
                        concordance="%s/concordance/%s/" % (base, memid),
                        rconcordance="%s/rconcordance/%s/" % (base, memid),
                        delete="%s/delete/" % base,
                        info="%s/info/%s/" % (base, memid),
                        login="%s/login/" % base,
                        mem_info=self.get_info(memid),
                        rec_by_id="%s/rec_by_id/%s/" % (base, memid),
                        )

        return self.dumps(commands)

    @requires_priv("rec_read")
    @cherrypy.expose
    def rec_by_id(self, memid, rec_id, token=None):
        """
        Get a record by its ID
        """
        mem = self.get_item(int(memid))
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)
        rec = model.rec_by_id(mem, int(rec_id))
        if not rec:
            cherrybase.log_warning("Record with id %s in mem id %s not found" % (rec_id, memid))
            return self.dumps(None)
        return self.dumps(rec2d(rec))

    @cherrypy.expose
    def login(self, username, password):
        """
        Log into Memory Serves via the API. Get a token in return.
        """

        username = ensure_u(username)
        password = ensure_u(password)

        cherrybase.log_info("Logging in user %s" % username)

        user = admin.user_by_name(model.Data.users.values(), username)
        print user

        if not user:
            cherrybase.log_warning("Requested user not found")
            raise Exception("Failed to find user with login name %s" % username.encode("utf-8"))

        hashed = model.make_hash(password)
        print "Hashed:", hashed
        if user["password"] != hashed:
            cherrybase.log_warning("Password incorrect")
            raise Exception("Password does not match for login name %s" % username.encode("utf-8"))

        hashid = make_token()
        model.Data.logins[hashid] = user
        cherrybase.log_info("Logged in user: %s" % user)

        return self.dumps(hashid)

    @requires_priv("rec_read")
    @cherrypy.expose
    def getrange(self, memid, start, end, token=None):
        """
        Get a range of records
        """
        memid = int(memid)
        mem = self.get_item(memid)
        start = int(start)
        end = int(end)

        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps([])

        records = mem.mem["records"].values()[start:end]
        return self.dumps([rec2d(rec) for rec in records])

    @requires_priv("rec_read")
    @cherrypy.expose
    def get_page(self, memid, page, token=None):
        """
        Get a range of records
        """
        memid = int(memid)
        mem = self.get_item(memid)
        # page must be at least 1
        page = max(int(page), 1)
        start = (page - 1) * search.PAGE_SIZE
        end = start + search.PAGE_SIZE

        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps([])

        records = itertools.islice(mem.mem["records"].itervalues(), start, end)
        return self.dumps([rec2d(rec) for rec in records])

    @requires_priv("rec_read")
    @cherrypy.expose
    def num_pages(self, memid, token=None):
        """
        Get a range of records
        """
        memid = int(memid)
        mem = self.get_item(memid)

        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(0)

        num_records = len(mem.mem["records"])
        num_pages = num_records / search.PAGE_SIZE
        # if there is a remainder, add one
        if num_records - (num_records / search.PAGE_SIZE):
            num_pages += 1

        return self.dumps(num_pages)

    @requires_priv("rec_read")
    @cherrypy.expose
    def gloss(self, memid, query, minscore, token=None):
        """
        Do a glossary search
        If minscore is 1.0, then the search is for perfect matches.
        Otherwise, do a fuzzy search.
        """

        memid = int(memid)
        mem = self.get_item(memid)
        minscore = float(minscore)
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        prefs = settings.get_prefs()
        self.ensure_synched(prefs, mem)

        query_cmp = make_query(query)

        records = mem.mem["records"].itervalues()
        if minscore == 1.0:
            matches = [r for r in records if r.source_cmp in query_cmp]
        else:
            edist.set_minscore(minscore)
            get_score = edist.get_subscore
            matches = [r for r in records if get_score(r.source_cmp, query_cmp) >= minscore]
        if len(matches) > self.MAX_NUM_RESULTS:
            matches = gloss_matches_sorted(matches)
        return self.dumps([rec2d(m) for m in matches[:self.MAX_NUM_RESULTS]])

    @requires_priv("rec_delete")
    @cherrypy.expose
    def delete(self, **kwargs):
        """
        Delete a record
        """

        rec_id = int(kwargs.get('id'))

        rec = get_rec_by_id_global(rec_id)
        if not rec:
            cherrybase.log_warning(u"Tried to delete nonexistent record id : %s" % rec_id)
            return self.dumps(len(model.Data.memories))

        memid = rec.memory_id

        mem = self.get_item(memid)
        if not mem:
            cherrybase.log_warning(u"Tried to delete record from nonexistent memory %s" % memid)
            return self.dumps(0)

        mem.remove_record(rec)

        return self.dumps(len(mem.mem["records"]))

    def getuser(self):
        """
        Get the current user.
        Start by checking for IP address in list of cached users.
        Then try getting from the cherrypy session.
        """
        for user in model.Data.users.itervalues():
            if user["ip"] == cherrypy.request.remote.ip:
                return user["name"]
        return cherrybase.get_username(cherrypy.session)

    @requires_priv("rec_create")
    @cherrypy.expose
    def add(self, memid, **kwds):
        """
        Add a new record
        If the record is a duplicate, then we update it using the
        supplied values.
        """

        key = model.MAKE_KEY(kwds)
        if not is_key_valid(key):
            return self.dumps(None)

        memid = int(memid)
        mem = model.Data.memories.get(memid)

        if not mem:
            cherrybase.log_warning(u"Memory %s not found" % memid)
            return self.dumps(None)

        if not kwds.get("modified_by"):
            kwds["modified_by"] = self.getuser()
        if not kwds.get("created_by"):
            kwds["created_by"] = self.getuser()

        if key in mem.mem["records"]:
            # we are updating
            rec = mem.mem["records"][key]
            rec.update(kwds)
            return self.dumps(rec2d(rec))

        rec = model.MemoryRecord(**kwds)
        rec.id = model.get_next_recid()
        rec.memory_id = memid

        mem.add_record(rec)
        return self.dumps(rec2d(rec))

    @requires_priv("rec_update")
    @cherrypy.expose
    def update(self, **kwds):
        """
        Update a record
        """

        recid = int(kwds["id"])
        if "memory_id" in kwds:
            memid = int(kwds["memory_id"])
            memory = model.Data.memories.get(memid)

            if not memory:
                cherrybase.log_warning(u"Memory %s not found" % memid)
                return self.dumps(None)

            record = model.rec_by_id(memory, recid)
        else:
            record = get_rec_by_id_global(recid)
            if not record:
                cherrybase.log_warning(u"Record with ID %s not found" % recid)
                return self.dumps(None)
            memid = record.memory_id
            memory = model.Data.memories.get(memid)
            if not memory:
                cherrybase.log_warning(u"Memory %s not found" % memid)
                return self.dumps(None)

        if not record:
            return self.add(str(memid), **kwds)

        oldkey = (record.source, record.trans)

        if not kwds.get("modified_by"):
            kwds["modified_by"] = self.getuser()

        record.update(kwds)
        newkey = (record.source, record.trans)

        del memory.mem["records"][oldkey]
        memory.mem["records"][newkey] = record

        drec = rec2d(record)
        return self.dumps(drec)

    @requires_priv("rec_read")
    @cherrypy.expose
    def concordance(self, memid, query, token=None):
        """Concordance (substring match in entries)"""
        memid = int(memid)
        mem = self.get_item(memid)
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        prefs = settings.get_prefs()
        self.ensure_synched(prefs, mem)

        query_cmp = make_query(query)

        records = mem.mem["records"].values()
        matches = [r for r in records if query_cmp in r.source_cmp][:self.MAX_NUM_RESULTS]

        return self.dumps([rec2d(m) for m in matches])

    @requires_priv("rec_read")
    @cherrypy.expose
    def rconcordance(self, memid, query, token=None):
        """Reverse concordance (on trans)"""

        memid = int(memid)
        mem = self.get_item(memid)
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        prefs = settings.get_prefs()
        self.ensure_synched(prefs, mem)

        query_cmp = make_query(query)

        records = mem.mem["records"].itervalues()
        matches = [r for r in records if query_cmp in r.trans_cmp][:self.MAX_NUM_RESULTS]
        return self.dumps([rec2d(m) for m in matches])


    @requires_priv("rec_read")
    @cherrypy.expose
    def memsearch(self, memid, queryfilters, token=None):
        """
        Generic method to get search results for given query terms
        """

        memory = self.get_item(int(memid)).mem
        if not memory:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        records = memory["records"].itervalues()

        for queryfilter in queryfilters:
            records = search.refine_query(records, ensure_u(queryfilter))

        return self.dumps([rec2d(r) for r in itertools.islice(records, 0, self.MAX_NUM_RESULTS)])

    @requires_priv("rec_read")
    @cherrypy.expose
    def search(self, memid, query, minscore, token=None):
        """TM search"""

        memid = int(memid)
        minscore = float(minscore)
        mem = self.get_item(memid)

        # base case -- memory not found
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        prefs = settings.get_prefs()
        self.ensure_synched(prefs, mem)

        query_cmp = make_query(query)
        records = mem.mem["records"].itervalues()

        edist.set_minscore(minscore)
        get_score = edist.get_score
        matches = [r for r in records if get_score(query_cmp, r.source_cmp) >= minscore]

        if len(matches) > self.MAX_NUM_RESULTS:
            get_score = edist.get_score
            matches = [r for (s, r) in reversed(sorted((get_score(r.source_cmp, query_cmp), r)
                                                       for r in matches))]

        return self.dumps([rec2d(r) for r in matches[:self.MAX_NUM_RESULTS]])

    @requires_priv("rec_read")
    @cherrypy.expose
    def rsearch(self, memid, query, minscore, token=None):
        """Reverse search (search on translation)"""

        minscore = float(minscore)
        memid = int(memid)
        mem = self.get_item(memid)
        if not mem:
            cherrybase.log_warning("Memory with id %s not found" % memid)
            return self.dumps(None)

        prefs = settings.get_prefs()
        self.ensure_synched(prefs, mem)

        query_cmp = make_query(query)
        records = mem.mem["records"].itervalues()

        edist.set_minscore(minscore)
        get_score = edist.get_score
        matches = [r for r in records if get_score(query_cmp, r.trans_cmp) >= minscore]

        if len(matches) > self.MAX_NUM_RESULTS:
            get_score = edist.get_score
            matches = [r for (s, r) in reversed(sorted((get_score(r.trans_cmp, query_cmp), r)
                                                       for r in matches))]

        return self.dumps([rec2d(r) for r in matches[:self.MAX_NUM_RESULTS]])
