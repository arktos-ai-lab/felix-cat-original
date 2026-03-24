#!/usr/bin/env python

from .. import model

def init_db(dbname, memtype):
    mem = model.Memory(dbname, memtype)
    mem.id = 1
    mem.records = []
    model.Data.memories = {}
    model.Data.memories[1] = model.TranslationMemory(model.mem2d(mem))
    return mem
