# coding: UTF8
"""
Calculates segment matches against TransAssist memories

"""
import logging

import edist
from edist import get_score
from pywintypes import com_error
from win32com.client import Dispatch
import normalizer
from MemoryServes import mem_parser
from TMX import reader

MINSCORE = 0.1
LOGGER = logging.getLogger(__name__)


class SegmenterException(Exception):
    pass


class RemoteMemory(object):
    def __init__(self, connection):
        self.remote_mem = Dispatch("Felix.RemoteMemory")
        self.remote_mem.Connect(connection)

    def get_best(self, query):
        stripper = normalizer.strip
        candidates = [stripper(rec.Source)
                      for rec in self.remote_mem.Search(query, MINSCORE)]
        scores = [get_score(query, candidate) for candidate in candidates]
        if not scores:
            return 0
        return max(scores)


def load_memory_ta(filename):
    """
    Load a Felix memory
    """

    try:
        with open(filename) as fp:
            records = mem_parser.get_records(mem_parser.get_root(fp))
            return [normalizer.strip(rec["source"]) for rec in records]
    except com_error:
        LOGGER.exception(u"Failed to load memory (%s)" % filename)
        raise


def load_memory_tmx(filename):
    """
    Load a TMX memory and get the source segments
    """

    try:
        mem = reader.parse_tmx(open(filename))
        srclang = mem.header.srclang
        return [r.get_segment(srclang) for r in mem.records]
    except Exception:
        LOGGER.exception(u"Failed to load memory ({0})".format(filename))
        raise


def load_memory(filename):
    """
    Loads the memory in filename.
    Selects a tmx or TransAssist loader depending on the file extension.

    @param filename: The name of the file. "tmx" -> TMX loader; others -> TransAssist loader
    """

    if filename.lower().endswith("tmx"):
        return load_memory_tmx(filename)
    return load_memory_ta(filename)


class SegMatcher(object):
    """
    Matches segments against the memories provided
    """

    def __init__(self, memory_names):
        """
        @param memory_names: The names of the memories to load
        """
        LOGGER.debug("Creating SegMatcher")
        LOGGER.debug("Minimum match score is %s" % MINSCORE)
        edist.set_minscore(MINSCORE)

        self.memory_names = memory_names

        self.repetitions = set()
        self.memories = set()
        self.remote_mems = set()
        for memory_name in memory_names:
            if memory_name.startswith("http"):
                self.remote_mems.add(RemoteMemory(memory_name))
            else:
                self.memories.update(load_memory(memory_name))

    def best_match(self, seg):
        """Get the best match in our memories for seg

        0 = No match
        100 = Perfect match
        101 = Repetition

        >>> matcher = SegMatcher([])
        >>> matcher.best_match(u"spam")
        0
        >>> matcher.best_match(u"spam")
        101
        >>> matcher.memories.add(u"egg")
        >>> matcher.best_match(u"egg")
        100
        """

        if seg in self.repetitions:
            return 101

        score = self.get_best(seg)

        if score < 100:
            self.repetitions.add(seg)

        return score

    def get_best(self, seg):
        """Returns the best score in the memories
        >>> matcher = SegMatcher([])
        >>> matcher.get_best(u"spam")
        0
        >>> matcher.memories.add(u"spam")
        >>> matcher.get_best(u"spam")
        100
        """
        if not self.memories:
            local_best = 0
        else:
            local_best = max(get_score(seg, record) for record in self.memories)

        if not self.remote_mems:
            remote_best = 0
        else:
            scores = list(mem.get_best(seg) for mem in self.remote_mems)
            if not scores:
                remote_best = 0
            remote_best = max(scores)

        return int(max(remote_best, local_best) * 100)


def get_seg_matcher(memory_names):
    """
    Retrieves a SegMatcher with the specified memory names
    """

    return SegMatcher(memory_names)
