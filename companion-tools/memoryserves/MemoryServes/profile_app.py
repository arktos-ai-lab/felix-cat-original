#coding: UTF8
"""
Enter module description here.

"""
import cProfile
import pstats
import api
import cherrybase
import admin
from test import fake_cherrypy
import cPickle
import model
import random

def add_record(program_api, source, trans, id):  # pragma no cover
    """Add a record to the TM/gloss in question"""
    if source.strip():
        return cPickle.loads(program_api.add(id, source=source, trans=trans))

def add_mem_records(program_api, mem_info):  # pragma no cover
    """Add records to the TM"""
    for line in open("/python25/readme.txt"):
        words = line.split()
        if words:
            for c in range(10):
                text = " ".join([random.choice(words) for i in range(20)])
                add_record(program_api, text, text, mem_info["id"])

def add_gloss_records(program_api, mem_info):  # pragma no cover
    """Add records to the glossary"""
    for line in open("/python25/readme.txt").read().split():
        add_record(program_api, line, line, mem_info["id"])

def lookup_tm(program_api, mem_info):  # pragma no cover
    """Look up TM entries"""
    for line in open("/python25/readme.txt"):
        words = line.split()
        if words:
            text = " ".join([random.choice(words) for i in range(20)])
            results = cPickle.loads(program_api.search(mem_info["id"],
                                                       query=line,
                                                       minscore=".7"))

def lookup_gloss(program_api, gloss_info):  # pragma no cover
    """Look up glossary entries, with fuzzy matching"""
    for line in open("/python25/readme.txt"):
        results = cPickle.loads(program_api.gloss(gloss_info["id"], line, ".5"))

def lookup_gloss_100(program_api, gloss_info):  # pragma no cover
    """Look up gloss entries, without fuzzy matching"""
    for line in open("/python25/readme.txt"):
        results = cPickle.loads(program_api.gloss(gloss_info["id"], line, "1"))

def add_memory(program_api):  # pragma no cover
    """Add a memory"""
    return cPickle.loads(program_api.addmem(name="foo", memtype="m"))

def load_model():  # pragma no cover
    model.load_data(None, "data/data.pk")

def run_tests():  # pragma no cover
    """Run our test functions."""

    load_model()

    program_api = api.Api()

    mem_info = add_memory(program_api)
    add_mem_records(program_api, mem_info)
    mem_info = program_api.get_info(mem_info["id"])
    print "mem_info:", mem_info
    print "=" * 30

    lookup_tm(program_api, mem_info)

    gloss_info = add_memory(program_api)
    add_gloss_records(program_api, gloss_info)
    gloss_info = program_api.get_info(gloss_info["id"])
    print "gloss_info:", gloss_info
    lookup_gloss(program_api, gloss_info)
    lookup_gloss_100(program_api, gloss_info)

def profileTests():  # pragma no cover
    """Run test functions and profile them"""
    # use fake sessions...
    api.cherrypy = cherrybase.cherrypy = admin.cherrypy = fake_cherrypy.FakeCherryPy()
    # now profile our test functions
    cProfile.run('run_tests()', "profile.stats")
    statfile = pstats.Stats('profile.stats')
    statfile.sort_stats('cumulative').print_stats(20)

def main():  # pragma no cover
    """Called when run as main"""
    profileTests()

if __name__ == "__main__":  # pragma no cover
    main()
