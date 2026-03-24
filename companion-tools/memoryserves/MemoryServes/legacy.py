"""
Legacy database module.
"""

import md5
import datetime
import time
import logging

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Unicode, UnicodeText, UniqueConstraint
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.types import DateTime, Boolean
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker
import settings
from data import USER_NAME

logger = logging.getLogger(__name__)
ECHO_SQL = False


def get_now():
    """
    Get the current datetime
    """

    return datetime.datetime(*time.localtime()[:6])


def parse_time(expr):
    """
    Parse the time into a time object if it's a string.
    If it's already a date, return that.
    Otherwise, return the current datetime.

    >>> parse_time("2010/10/10 10:11:12")
    datetime.datetime(2010, 10, 10, 10, 11, 12)
    >>> parse_time(datetime.datetime(2010, 10, 10, 10, 11, 12))
    datetime.datetime(2010, 10, 10, 10, 11, 12)
    """

    if isinstance(expr, basestring):
        try:
            return datetime.datetime(*time.strptime(expr, "%Y/%m/%d %H:%M:%S")[:6])
        except ValueError:
            return get_now()
    return expr if expr else get_now()


def make_unicode(obj):
    """
    Make the string unicode if it isn't already.

    Multibyte strings are assumed to be utf-8
    """

    if isinstance(obj, unicode):
        return obj
    return unicode(obj, "utf-8")


def parse_validated(validated):
    """
    Parse the validated field, handling various variations of true/false we may
    have put in there. Always gives you some sort of bool value.
    """
    try:
        return {"true": True,
                "True": True,
                "false": False,
                "False": False,
                True: True,
                False: False}[validated]
    except KeyError:
        logging.warn("%s is not a valid bool value. Returning True." % validated)
        return bool(validated)


def make_hash(password):
    """
    Create a hash of the password
    """
    return unicode(md5.new(password).hexdigest())


class Record(object):
    """
    Represents a record object in the database
    """

    def __init__(self,
                 source,
                 trans,
                 context=u"",
                 date_created=None,
                 last_modified=None,
                 reliability=0,
                 validated=False,
                 ref_count=0,
                 created_by=USER_NAME,
                 modified_by=USER_NAME,
                 id=0,
                 memory_id=0,
                 **kwds):
        """
        Initialize the record. source and trans are required
        """

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

        self.created_by = make_unicode(created_by)
        self.modified_by = make_unicode(modified_by)

        self.context = make_unicode(context)


class Memory(object):
    """
    Represents a memory object in the database
    """

    def __init__(self,
                 name,
                 memtype,
                 creator=USER_NAME,
                 created_on=None,
                 client=u"",
                 source_language=u"Default",
                 target_language=u"Default",
                 notes=u"",
                 modified_by=USER_NAME,
                 modified_on=None,
                 normalize_case=False,
                 normalize_width=False,
                 normalize_hira=False,
                 records=None,
                 **kwds):
        """
        Initialize the memory with various values
        """

        self.name = make_unicode(name)
        self.memtype = make_unicode(memtype)
        self.creator = make_unicode(creator)
        self.created_on = parse_time(created_on)

        self.client = make_unicode(client)
        self.source_language = make_unicode(source_language)
        self.target_language = make_unicode(target_language)
        self.notes = make_unicode(notes)

        self.modified_by = make_unicode(modified_by)
        self.modified_on = parse_time(modified_on)

        self.normalize_case = normalize_case
        self.normalize_width = normalize_width
        self.normalize_hira = normalize_hira

        self.records = records or []


def load():
    """
    Load from legacy database.
    """
    try:
        session = SessionClass()
        load_memories(session)
    except TypeError:
        logger.exception("Failed to load data from SQLite database")
    else:
        SessionClass.remove()


def get_engine(connection_string):
    """
    Get the database engine (SQLAlchemy stuff)
    """

    def connect():
        """
        Custom connection function to set the isolation level
        """

        conn = sqlite3.connect(connection_string)
        conn.isolation_level = "IMMEDIATE"
        return conn

    engine = create_engine("sqlite:///%s" % connection_string,
                           echo=ECHO_SQL,
                           creator=connect)

    metadata = MetaData()
    memories_table = Table('memories', metadata,
         Column('id', Integer, primary_key=True),
         Column('name', Unicode(100)),
         Column('size', Integer),
         Column('creator', Unicode(100)),
         Column('created_on', DateTime()),
         Column('memtype', Unicode(1)),
         Column('modified_by', Unicode(100)),
         Column('modified_on', DateTime()),
         Column('client', Unicode(100)),
         Column('source_language', Unicode(100)),
         Column('target_language', Unicode(100)),
         Column('notes', UnicodeText()),
         Column('normalize_case', Boolean(), default=False),
         Column('normalize_width', Boolean(), default=False),
         Column('normalize_hira', Boolean(), default=False),
    )
    records_table = Table('records', metadata,
         Column('id', Integer, primary_key=True),
         Column('source', UnicodeText(), index=True),
         Column('trans', UnicodeText(), index=True),
         Column('source_cmp', UnicodeText()),
         Column('trans_cmp', UnicodeText()),
         Column('context', UnicodeText()),
         Column('created_by', Unicode(100)),
         Column('modified_by', Unicode(100)),
         Column('date_created', DateTime()),
         Column('last_modified', DateTime()),
         Column('reliability', Integer()),
         Column('validated', Boolean()),
         Column('ref_count', Integer()),
         Column('memory_id', Integer, ForeignKey('memories.id'), index=True),
         UniqueConstraint('source', 'trans', 'memory_id')
    )

    mapper(Record, records_table)
    mapper(Memory, memories_table, properties={
         'records':relation(Record, backref='memory')
     })
    metadata.create_all(engine)

    return engine


def make_session_class(engine):
    """
    Create the session class for accessing the database
    via SQLAlchemy
    """

    SessionClass = scoped_session(sessionmaker(bind=engine,
                                       autoflush=True,
                                       autocommit=True))
    return SessionClass


def set_up_database(connection_string=':memory:'):
    """
    Create the database engine, and define our tables
    """

    engine = get_engine(connection_string)
    return make_session_class(engine)
