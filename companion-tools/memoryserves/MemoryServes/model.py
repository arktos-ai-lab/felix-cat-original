# coding: UTF8
"""
Enter module description here.

"""

import datetime
import threading
import time
import itertools
import logging

import settings
from settings import normalize

# legacy SQLAlchemy stuff
from legacy import make_hash
from legacy import Memory
from legacy import Record

from data import USER_NAME

DEBUG_MODE = True
VERSION = "2.1.3"

# These are for our save thread.
# The app sets SHOULD_QUIT to True to signal the thread
# to quit; the thread then performs a final save, and quits.
SHOULD_QUIT = False


def ensure_u(term):
    """
    Make a term unicode if it isn't now
    """
    if isinstance(term, unicode):
        return term
    try:
        return unicode(term, "utf-8")
    except UnicodeDecodeError:
        return repr(term)
    except TypeError:
        return u''


def is_key_valid(key):
    '''
    Is the key valid?
    '''
    if not key:
        return False
    return all(x for x in key)


def make_key_both(record):
    """
    key = (source, trans)
    """
    try:
        return (record.source, record.trans)
    except AttributeError:
        source = ensure_u(record.get("source"))
        trans = ensure_u(record.get("trans"))

        return (source, trans)


def make_key_source(record):
    '''
    key = source
    This is for the one translation per source option.
    '''
    try:
        return record.source
    except AttributeError:
        return ensure_u(record.get("source"))


MAKE_KEY = make_key_both


def log2d(entry):
    """
    Convert a log entry object into a dictionary
    """

    return dict(severity=entry.severity,
                when=entry.when,
                message=entry.message,
                user=entry.user)


def user2d(user):
    """
    Convert a user object into a dictionary
    """

    return dict(id=user.id,
                name=user.name,
                role=user.role,
                password=user.password,
                ip=user.ip)


def rec2d(rec):
    """
    Convert a record into a dictionary for sending over the wire
    """
    return dict(source=rec.source,
                trans=rec.trans,
                source_cmp=rec.source_cmp,
                trans_cmp=rec.trans_cmp,
                context=rec.context,
                created_by=rec.created_by,
                modified_by=rec.modified_by,
                date_created=rec.date_created,
                last_modified=rec.last_modified,
                reliability=rec.reliability,
                validated=rec.validated,
                ref_count=rec.ref_count,
                memory_id=rec.memory_id,
                id=rec.id,
    )


def mem2d(mem):
    """
    Convert a memory object into a dictionary
    """
    logging.debug("mem2d")
    records = dict([(MAKE_KEY(r), MemoryRecord(**rec2d(r)))
                    for r in mem.records])
    memd = dict(name=mem.name,
                memtype=mem.memtype,
                creator=mem.creator,
                created_on=mem.created_on,
                client=mem.client,
                source_language=mem.source_language,
                target_language=mem.target_language,
                notes=mem.notes,
                modified_by=mem.modified_by,
                modified_on=mem.modified_on,
                normalize_case=mem.normalize_case,
                normalize_width=mem.normalize_width,
                normalize_hira=mem.normalize_hira,
                records=records,
    )
    memd["id"] = mem.id
    logging.debug(str(mem))
    return memd


class Data:
    """
    Global class for holding our data
    """

    memories = {}
    users = {}
    logins = {}
    log = []
    lock = threading.Lock()
    next_id = 1


def get_next_id(ids):
    """
    Get the next id from the list of integers
    """

    if not ids:
        return 1
    return max(ids) + 1


def get_next_memid():
    """
    Get the next memory id. Lock for thread safety goodness
    """

    with Data.lock:
        return get_next_id(Data.memories.keys())


def get_next_userid():
    """
    Get the next user id. Lock for thread safety goodness
    """

    with Data.lock:
        return get_next_id(Data.users.keys())


def get_next_recid():
    """
    Get the next record id. Lock for thread safety goodness
    """

    with Data.lock:
        nextid = Data.next_id
        Data.next_id += 1
        return nextid


def get_now():
    """
    Get the current datetime
    """

    return datetime.datetime(*time.localtime()[:6])


def get_maxid(session):
    """
    Get the highest id for records in the database
    """

    conn = session.bind.connect()
    maxid = conn.execute("select max(id) from records").fetchone()[0]
    return maxid or 0


def parse_time(expr):
    """
    Parse the time into a time object if it's a string.
    If it's already a date, return that.
    Otherwise, return the current datetime.
    """

    if isinstance(expr, basestring):
        try:
            return datetime.datetime(*time.strptime(expr, "%Y/%m/%d %H:%M:%S")[:6])
        except ValueError:
            return get_now()
    if expr:
        return expr
    return get_now()


def make_unicode(obj):
    """
    Make the string unicode if it isn't already
    """

    if isinstance(obj, unicode):
        return obj
    return unicode(obj, "utf-8")


def global_rec_by_id(memories, recid):
    """
    Get the record for the given id, from the supplied memory
    """

    for memory in memories:
        records = memory.mem["records"]
        for record in records.itervalues():
            if record.id == recid:
                return record
    return None


def get_all_records():
    """
    Get all records from all memories
    """

    memories = Data.memories.itervalues()
    return itertools.chain(*[m.mem["records"].itervalues() for m in memories])


def rec_by_id(memory, recid):
    """
    Get the record for the given id, from the supplied memory
    """

    records = memory.mem["records"]
    for record in records.itervalues():
        if record.id == recid:
            return record
    return None


def parse_validated(validated):
    try:
        return {"true": True,
                "True": True,
                "false": False,
                "False": False,
                True: True,
                False: False}[validated]
    except KeyError:
        return bool(validated)


class TranslationMemory:
    """
    Represents a translation memory/glossary
    in the database
    """

    def __init__(self, mem):
        self.mem = mem

    def synch_prefs(self, prefs):
        self.mem["normalize_case"] = prefs["normalize_case"]
        self.mem["normalize_hira"] = prefs["normalize_hira"]
        self.mem["normalize_width"] = prefs["normalize_width"]

        settings.normalize = settings.make_normalizer(prefs)
        for record in self.mem["records"].itervalues():
            normalize_rec(record)

    def add_record(self, record):
        records = self.mem["records"]
        records[MAKE_KEY(record)] = record

    def remove_record(self, record):
        oldkey = MAKE_KEY(record)
        if oldkey in self.mem["records"]:
            del self.mem["records"][oldkey]
            return True
        else:
            return False


class MemoryRecord(object):
    """Represents a record object in the database"""
    __slots__ = """key source trans context
                source_cmp trans_cmp
                 date_created last_modified
                 reliability validated ref_count
                 created_by modified_by
                 id memory_id""".split()

    def __init__(self,
                 source,
                 trans,
                 context=u"",
                 date_created=None,
                 last_modified=None,
                 reliability=0,
                 validated=False,
                 ref_count=0,
                 created_by=u"",
                 modified_by=u"",
                 id=0,
                 memory_id=0,
                 **kwds):
        """Initialize the record. source and trans are required"""

        self.source = make_unicode(source)
        self.source_cmp = settings.normalize(self.source)
        self.trans = make_unicode(trans)
        self.trans_cmp = settings.normalize(self.trans)

        self.date_created = parse_time(date_created)
        self.last_modified = parse_time(last_modified)
        self.reliability = int(reliability)

        self.id = int(id)
        self.memory_id = int(memory_id)

        self.validated = parse_validated(validated)
        self.ref_count = int(ref_count)

        self.created_by = make_unicode(created_by or USER_NAME)
        self.modified_by = make_unicode(modified_by or USER_NAME)

        self.context = make_unicode(context)

    @property
    def key(self):
        return (self.source_cmp, self.trans_cmp)

    def __str__(self):
        return "<MemoryRecord: [s] %s | [t] %s>" % (self.source.encode("utf-8"),
                                                    self.trans.encode("utf-8"))

    def update(self, values):
        """Initialize the record. source and trans are required"""

        actions = dict(source=self.update_source,
                       trans=self.update_trans,
                       date_created=self.update_date_created,
                       last_modified=self.update_last_modified,
                       reliability=self.update_reliability,
                       validated=self.update_validated,
                       ref_count=self.update_ref_count,
                       created_by=self.update_created_by,
                       modified_by=self.update_modified_by,
                       context=self.update_context, )

        for key, val in values.iteritems():
            action = actions.get(key)
            if action:
                action(val)

    def update_source(self, source):
        self.source = make_unicode(source)
        self.source_cmp = settings.normalize(self.source)

    def update_trans(self, trans):
        self.trans = make_unicode(trans)
        self.trans_cmp = settings.normalize(self.trans)

    def update_date_created(self, date_created):
        self.date_created = parse_time(date_created)

    def update_last_modified(self, last_modified):
        self.last_modified = parse_time(last_modified)

    def update_reliability(self, reliability):
        self.reliability = int(reliability)

    def update_validated(self, validated):
        self.validated = parse_validated(validated)

    def update_ref_count(self, ref_count):
        self.ref_count = int(ref_count)

    def update_created_by(self, created_by):
        self.created_by = make_unicode(created_by)

    def update_modified_by(self, modified_by):
        self.modified_by = make_unicode(modified_by)

    def update_context(self, context):
        self.context = make_unicode(context)

    def __getstate__(self):
        """
        State is: (__dict__, __slots__)
        Since we don't have a __dict__, it will be None, with the slots
        dict next
        """

        state = dict(source=self.source,
                     trans=self.trans,
                     source_cmp=self.source_cmp,
                     trans_cmp=self.trans_cmp,
                     context=self.context,
                     date_created=self.date_created,
                     last_modified=self.last_modified,
                     reliability=self.reliability,
                     validated=self.validated,
                     ref_count=self.ref_count,
                     created_by=self.created_by,
                     modified_by=self.modified_by,
                     id=self.id,
                     memory_id=self.memory_id)
        # __dict__, __slots__
        return (None, state)

    def __setstate__(self, state):
        """
        State is: (__dict__, __slots__)
        Since we don't have a __dict__, it will be None, with the slots
        dict next
        """

        d, s = state
        MemoryRecord.__init__(self, **s)


class User(object):
    """
    Represents a user
    """

    def __init__(self, name, role, password, ip=u"", id=None):
        self.name = name
        self.role = role
        self.password = make_hash(password)
        self.ip = ip
        if id:
            self.id = id

    def passwords_match(self, password):
        """
        See if the hash of this password matches our stored hash
        of the user's password
        """
        return self.password == make_hash(password)

    def get_rank(self):
        """
        Numerical value for role
        """
        ranks = dict(admin=3, user=2, guest=1, anon=0)
        return ranks.get(self.role, 0)


class Log(object):
    """
    Represents a log entry
    """

    def __init__(self, message, user=None, severity=u"info", when=None):
        self.severity = severity
        self.message = message
        self.when = parse_time(when)
        self.user = user or u""


def normalize_rec(record):
    """
    Normalize the source and trans strings in the record
    """
    record.source_cmp = normalize(record.source)
    record.trans_cmp = normalize(record.trans)


def percent_validated(memory):
    """
    Get the percent of records in the memory that have been validated
    """
    num_validated = sum(1 for x in memory["records"].itervalues() if x.validated)
    if len(memory["records"]) == 0:
        return 0
    return float(num_validated) / float(len(memory["records"]))


def reliability_stats(memory):
    """
    Get reliability stats for the memory
    high, low, and average reliability
    """

    high, low, total = 0, 9, 0

    for record in memory["records"].itervalues():
        high = max(high, record.reliability)
        total += record.reliability
        low = min(low, record.reliability)

    low = min(high, low)
    high = max(high, low)
    if len(memory["records"]) == 0:
        ave = 0.0
    else:
        ave = float(total) / float(len(memory["records"]))

    return low, high, ave


