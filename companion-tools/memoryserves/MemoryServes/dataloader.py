__author__ = 'Ryan'

import time
import threading
import os
import sys
import logging
import cPickle
import pickle
import sqlite3
import traceback
from datetime import datetime as datify

# legacy SQLAlchemy stuff
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, UniqueConstraint
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.types import DateTime, Boolean
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import clear_mappers

import model
from legacy import Record
from legacy import Memory
from model import MemoryRecord, TranslationMemory
from model import Data, get_maxid
from model import make_key_both, make_key_source
from model import Log, User, get_now
from model import normalize_rec
from model import mem2d
from model import SHOULD_QUIT


CHECK_INTERVAL = 60 * 10  # 10 minutes
SLEEP_INTERVAL = 3  # seconds
PICKLE_DATA_FILE = "data.pk"
ECHO_SQL = False


import settings

logger = logging.getLogger(__name__)


def massage_memories(memories):
    """
    Fix bad dates in memories
    """
    logger.info("Ensuring correct memory data")
    for memory in memories.itervalues():
        if not memory.mem.get('id'):
            memory.mem['id'] = model.get_next_memid()
        logger.debug(" ... Massaging %(name)s : id %(id)s" % memory.mem)
        try:
            records = massage_records(memory.mem["records"])
            memory.mem["records"] = dict((MAKE_KEY(r), r) for r in records)
        except Exception:
            logger.exception(" ... Failed to parse memory")


def massage_records(records):
    """
    Make sure that the data in our records is correct.
    - Correct date tuples to date objects
    - normalize source and translation
    """
    logger.debug("massage_records")

    for record in records.itervalues():
        if isinstance(record, dict):
            if "memory_id" in record and not isinstance(record["memory_id"], int):
                del(record["memory_id"])
            record = MemoryRecord(**record)

        yield transform_record(record)


def transform_record(record):
    """
    Perform fixes on record needed due to bad data migrations
    """
    massage_dates(record)
    normalize_rec(record)
    return record


def massage_dates(record):
    """
    Fix bad dates in the record
    """
    for attr in "date_created last_modified".split():
        val = getattr(record, attr)

        if isinstance(val, tuple):
            logger.warn("record attribute %s is a tuple (%s). Converting to datetime." % (attr, val))
            setattr(record, attr, datify(*val[:6]))

    return record


def load_pickle_data(data_file, data_filename=None):
    """
    Loads pickled TM data. If we fail to load it with cPickle, we load it with pickle.
    """

    logger.debug("Loading pickle data file")
    try:
        data = cPickle.load(data_file)
    except ImportError:
        if data_filename:
            data_file.close()
            data_file = open(data_filename)
        # it was expecting a legacy module structure...
        sys.modules["model"] = model
        # rewind the file
        data_file.seek(0)
        data = pickle.load(data_file)
        del sys.modules["model"]

    Data.memories = dict((k, TranslationMemory(mem))
        for k, mem in data["memories"].iteritems())
    massage_memories(Data.memories)
    Data.users = data["users"]
    Data.log = data["log"]
    Data.next_id = data["next_id"]


def load_memories(session):
    """
    Load memories (with their records) from the database
    """
    logger.debug("Loading memories")
    for memory in session.query(Memory).all():
        mem = mem2d(memory)
        logger.debug("Loading memory %s" % memory.id)
        Data.memories[memory.id] = TranslationMemory(mem)
    Data.next_id = get_maxid(session) + 1


def load_data(SessionClass, pickle_data_file=PICKLE_DATA_FILE):
    """
    If the user is upgrading, then they'll have the old SQLite
    database. Load that into our python-based in-memory
    data store
    """

    try:
        data_filename = settings.get_data_file(pickle_data_file)
        logger.info("loading data from %s" % repr(data_filename))
        if os.path.exists(data_filename):
            # preserve old module name so that we don't break the import...
            logger.debug("Loading data from python pickle file at %s" % get_now())
            load_pickle_data(open(data_filename, "rb"), data_filename)
            logger.debug(" ... done loading file at %s" % get_now())
            return
    except Exception:
        logger.exception("Failed to load pickled data file {0}".format(repr(data_filename)))

    try:
        session = SessionClass()
        load_memories(session)
    except TypeError:
        logger.exception("Failed to load from SQLite database")
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

    users_table = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(100)),
        Column('role', Unicode(100)),
        Column('password', Unicode(200)),
        Column('ip', Unicode(100)),
    )

    log_table = Table('log', metadata,
        Column('id', Integer, primary_key=True),
        Column('severity', Unicode(100), default=u"info"),
        Column('when', DateTime()),
        Column('message', UnicodeText()),
        Column('user', Unicode(100))
    )

    clear_mappers()
    mapper(Record, records_table)
    mapper(Memory, memories_table, properties={
        'records':relation(Record, backref='memory')
    })
    mapper(Log, log_table)
    mapper(User, users_table)

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


def get_data():
    """
    Get the database data as a dictionary suitable for pickling
    """

    data = {}
    data["memories"] = dict((k,v.mem) for (k,v) in Data.memories.iteritems())
    data["users"] = Data.users
    data["log"] = Data.log
    data["next_id"] = Data.next_id
    return data


def do_save():
    """
    Save the database to a pickle file.

    First saves the memories to a temp file, and then
    renames that to the actual file. This should save us from
    a crash/power failure during a save.
    """

    try:
        data = get_data()
        data_filename_tmp = settings.get_data_file("data.pk.tmp")
        logger.info("Writing data to %s" % repr(data_filename_tmp))

        with open(data_filename_tmp, "wb") as out:
            p = cPickle.Pickler(out, protocol=2)
            p.fast = True
            p.dump(data)

        data_filename = settings.get_data_file(PICKLE_DATA_FILE)
        if os.path.exists(data_filename):
            os.remove(data_filename)

        # rename the temp file to the database file
        os.rename(data_filename_tmp, data_filename)
    except Exception:
        logger.exception("Failed to save data:")


def do_quit():
    """
    Exit the program
    """
    os._exit(0)


def save_and_quit():
    """
    Perform a final save, and then send a quit signal.
    """
    logger.info("Quitting from Memory Serves - saving and shutting down")
    do_save()
    threading.Timer(1, do_quit).start()


def save_and_continue():
    """
    Save the db, and continue the endless loop.
    """
    logger.info("saving db to disc...")
    last_time = time.time()
    do_save()
    logger.info("   ... finished saving in %s seconds" % (time.time() - last_time))


def background_save():
    """
    Continually save data in the background
    """

    logger.info("background save")
    last_time = time.time()
    while True:
        if SHOULD_QUIT:
            save_and_quit()
            return

        time.sleep(SLEEP_INTERVAL)
        if time.time() - last_time > CHECK_INTERVAL:
            save_and_continue()
            last_time = time.time()


if settings.get_prefs()["one_trans_per_source"]:
    MAKE_KEY = make_key_source
else:
    MAKE_KEY = make_key_both


if __name__ == "__main__":  # pragma no cover
    load_data(None)