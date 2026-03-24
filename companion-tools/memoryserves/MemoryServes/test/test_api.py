#coding: UTF8
"""
Enter module description here.

"""
import unittest
import cPickle

from nose.tools import raises

from .. import api
from .. import model
from .. import settings
from .. import model
from .. import main
from .. import search
from MemoryServes.test import fake_cherrypy

from apitest_base import ApiTester
from usertests import UserTestsDb


class TestRec2D(unittest.TestCase):

    def test_simple(self):
        rec = model.Record(u"spam", u"egg")
        rec.id = 1
        rec.memory_id = 1
        d = api.rec2d(rec)
        assert rec.source == d["source"], (rec, d)
        assert rec.trans == d["trans"], (rec, d)

    def test_simple_last_modified(self):
        rec = model.Record(u"spam", u"egg")
        rec.id = 1
        rec.memory_id = 1
        d = api.rec2d(rec)
        assert rec.last_modified == d["last_modified"], (rec, d)


class TestGetInfo(ApiTester):

    def test_no_mem(self):
        info = self.api.get_info("2")
        assert info is None, info

    def test_one_record(self):
        self.add_record(u"foo", u"bar")
        info = self.api.get_info("1")
        assert "records" not in info, info
        assert info["size"] == 1, info
        assert info["name"] == "ApiTester", info
        assert info["source_language"] == u"Default", info
        assert info["target_language"] == u"Default", info


class TestAddMem(ApiTester):
    def test_create(self):
        values = dict(name="TestAddMem.test_create", memtype="m", creator=u"Ryan")
        data = cPickle.loads(self.api.addmem(**values))
        assert data["name"] == u"TestAddMem.test_create", data
        assert data["id"] == 2, data
        assert data["creator"] == u"Ryan", data


class TestDelMem(ApiTester):
    def test_delete(self):
        assert len(model.Data.memories) == 1
        data = cPickle.loads(self.api.delmem("1"))
        assert data == 0, data
        assert len(model.Data.memories) == 0
    def test_doesnt_exist(self):
        assert len(model.Data.memories) == 1
        data = cPickle.loads(self.api.delmem("4"))
        assert data == 1, data
        assert len(model.Data.memories) == 1, model.Data.memories


class TestMemSearch(ApiTester):

    def test_generic(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", ["spam"]))
        assert len(records) == 1, records
        assert records[0]["source"] == u"spam", records

    def test_generic_false(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", ["foo"]))
        assert not records, records

    def test_source(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", ["source:spam"]))
        assert len(records) == 1, records
        assert records[0]["source"] == u"spam", records

    def test_source_false(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", ["source:egg"]))
        assert not records, records

    def test_trans(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", ["trans:egg"]))
        assert len(records) == 1, records
        assert records[0]["source"] == u"spam", records

    def test_trans_false(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", ["trans:spam"]))
        assert not records, records


    def test_two(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", "source:spam trans:egg".split()))
        assert len(records) == 1, records
        assert records[0]["source"] == u"spam", records

    def test_two_false(self):
        self.add_record(u"spam", u"egg")

        records = cPickle.loads(self.api.memsearch("1", "source:spam trans:foo".split()))
        assert not records, records


class TestRSearch(ApiTester):

    def test_egg(self):

        self.add_record(u"spam", u"egg")

        text = self.api.rsearch("1", "egg", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"spam", item
        assert item["trans"] == u"egg", item

    def test_bad_memory(self):
        data = cPickle.loads(self.api.rsearch("2", "spam", ".5"))
        assert data is None, data

    def test_eggs(self):

        self.add_record(u"spam", u"egg")

        text = self.api.rsearch("1", "eggs", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"spam", item
        assert item["trans"] == u"egg", item

    def test_zzzz(self):

        self.add_record(u"spam", u"egg")

        text = self.api.rsearch("1", "zzzz", ".5")
        items = cPickle.loads(text)
        assert len(items) == 0, items

    def test_japanese(self):

        self.add_record(u"本日は晴天なり", u"日本語")

        text = self.api.rsearch("1", "日本語", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"本日は晴天なり", item
        assert item["trans"] == u"日本語", item

    def test_3_records_2_hits(self):

        self.add_record(u"spam", u"aa bb cc")
        self.add_record(u"ham", u"aa bb c")
        self.add_record(u"crapola", u"zzzz zzzz")

        text = self.api.rsearch("1", "aa bb cc", ".5")
        items = cPickle.loads(text)
        assert len(items) == 2, items
        item1, item2 = items
        assert item2["trans"] == u"aa bb cc" or item2["trans"] == u"aa bb c", item1
        assert item1["source"] == u"spam" or item1["source"] == u"ham", item1

    def test_3_hits_2_max(self):

        self.add_record(u"spam", u"aa bb cc")
        self.add_record(u"ham", u"aa bb cca")
        self.add_record(u"crapola", u"aa bb ccaa")

        self.api.MAX_NUM_RESULTS = 2
        text = self.api.rsearch("1", "aa bb cc", ".5")
        items = cPickle.loads(text)
        assert len(items) == 2, items
        item1, item2 = items
        assert item1["trans"] == u"aa bb cc"
        assert item2["trans"] == u"aa bb cca"


def getmem(memid):
    return model.Data.memories[memid]


class TestDelete(ApiTester):

    def test_existing(self):
        data = cPickle.loads(self.api.add("1", source="added spam", trans="added egg"))

        result = cPickle.loads(self.api.delete(**data))

        assert result == 0, result
        assert len(getmem(1).mem["records"]) == 0, getmem(1).mem["records"]

    def test_non_existing(self):
        data = cPickle.loads(self.api.add("1", source="added spam", trans="added egg"))

        result = cPickle.loads(self.api.delete(**dict(id=1 + int(data["id"]))))

        assert result == 1, result
        assert len(getmem(1).mem["records"]) == 1, getmem(1).mem["records"]

    def test_mem_non_existing(self):
        data = cPickle.loads(self.api.add("1", source="spam", trans="egg"))
        records = getmem(1).mem["records"]
        key = model.MAKE_KEY(dict(source=u"spam", trans=u"egg"))
        records[key].memory_id = 2

        result = cPickle.loads(self.api.delete(**data))

        print model.Data.log
        assert result == 0, result
        assert len(getmem(1).mem["records"]) == 1, getmem(1).mem["records"]


class TestSearch(ApiTester):
    def test_search_spam(self):

        self.add_record(u"spam", u"egg")

        text = self.api.search("1", "spam", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"spam", item
        assert item["trans"] == u"egg", item

    def test_bad_memory(self):
        data = cPickle.loads(self.api.search("2", "spam", ".5"))
        assert data is None, data

    def test_search_added_records(self):

        self.add_record(u"spam", u"egg")

        text = self.api.search("1", "spam", ".5")
        items = cPickle.loads(text)

        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"spam", item
        assert item["trans"] == u"egg", item
        assert item["memory_id"] == 1, item
        assert item["id"] == 1, item

    def test_search_spam_empty(self):

        text = self.api.search("1", "spam", ".5")
        items = cPickle.loads(text)
        assert items == [], items

    def test_search_spam_wrong_memory(self):

        self.add_record(u"spam", u"egg")

        text = self.api.search("2", "spam", ".5")
        items = cPickle.loads(text)
        assert items is None

    def test_search_twice(self):

        self.add_record(u"spam", u"egg")

        text = self.api.search("1", "spam", ".5")
        items1 = cPickle.loads(text)

        text = self.api.search("1", "spam", ".5")
        items2 = cPickle.loads(text)

        assert items1 == items2, (items1, items2)

    def test_search_ham(self):

        self.add_record(u"spam", u"egg")

        text = self.api.search("1", "ham", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"spam", item
        assert item["trans"] == u"egg", item

    def test_search_dashes(self):

        self.add_record(u"----------------------------", u"----------------------------")

        text = self.api.search("1", "----------------------------", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"----------------------------", item
        assert item["trans"] == u"----------------------------", item

    def test_search_3_records_2_hits(self):

        self.add_record(u"spam", u"egg")
        self.add_record(u"ham", u"egg")
        self.add_record(u"crapola", u"egg")

        text = self.api.search("1", "ham", ".5")
        items = cPickle.loads(text)
        assert len(items) == 2, items
        item1, item2 = items
        assert item1["source"] == u"spam" or item1["source"] == u"ham", item1
        assert item2["trans"] == u"egg", item2

    def test_search_zzzz(self):

        self.add_record(u"spam", u"egg")

        text = self.api.search("1", "zzzz", ".5")
        items = cPickle.loads(text)
        assert len(items) == 0, items

    def test_search_japanese(self):

        self.add_record(u"本日は晴天なり", u"日本語")

        text = self.api.search("1", "本日晴天なり", ".5")
        items = cPickle.loads(text)
        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"本日は晴天なり", item
        assert item["trans"] == u"日本語", item

    def test_search_75_to_0_hits(self):

        self.add_record(u"aaa bbb ccc", u"egg")
        self.add_record(u"aaa zzz ccc", u"egg")
        self.add_record(u"fugga fugga", u"egg")

        text = self.api.search("1", "aaa ccc", ".75")
        items = cPickle.loads(text)
        assert len(items) == 0, items

    def test_search_50_to_2_hits(self):

        self.add_record(u"aaa bbb ccc", u"egg")
        self.add_record(u"aaa zzz ccc", u"egg")
        self.add_record(u"fugga fugga", u"egg")

        text = self.api.search("1", "aaa ccc", ".50")
        items = cPickle.loads(text)
        assert len(items) == 2, items


class TestConcordance(ApiTester):
    def test_empty(self):
        data = cPickle.loads(self.api.concordance("1", "spam"))
        assert data == [], data

    def test_bad_memory(self):
        data = cPickle.loads(self.api.concordance("2", "spam"))
        assert data is None, data

    def test_spam(self):
        self.add_record(u"I love spam in the morning!", u"aa bb cc")

        data = cPickle.loads(self.api.concordance("1", "spam"))
        assert len(data) == 1, data
        assert data[0]["source"] == u"I love spam in the morning!", data

    def test_spam_in(self):
        self.add_record(u"I love spam in the morning!", u"aa bb cc")

        data = cPickle.loads(self.api.concordance("1", "spam in"))
        assert len(data) == 1, data
        assert data[0]["source"] == u"I love spam in the morning!", data

    def test_spam_formatting(self):
        self.add_record(u"""I <b>love <i>spam</i></b> in the morning!""", u"aa bb cc")

        data = cPickle.loads(self.api.concordance("1", """<strong>spam</strong> in"""))
        assert len(data) == 1, data
        assert data[0]["source"] == u"I <b>love <i>spam</i></b> in the morning!", data

    def test_0_hits(self):
        self.add_record(u"I love spam in the morning!", u"aa bb cc")

        data = cPickle.loads(self.api.concordance("1", "ham"))
        assert data == [], data

class TestRConcordance(ApiTester):
    def test_empty(self):
        data = cPickle.loads(self.api.rconcordance("1", "spam"))
        assert data == [], data

    def test_bad_memory(self):
        data = cPickle.loads(self.api.rconcordance("2", "spam"))
        assert data is None, data

    def test_spam(self):
        self.add_record(u"I love spam in the morning!", u"The parrot is deceased")

        data = cPickle.loads(self.api.rconcordance("1", "parrot"))
        assert len(data) == 1, data
        assert data[0]["source"] == u"I love spam in the morning!", data


class TestRecordById(ApiTester):

    # by id
    def test_simple(self):
        data = cPickle.loads(self.api.add("1",
                                          source="added spam",
                                          trans="added egg"))

        result = cPickle.loads(self.api.rec_by_id(data["memory_id"],
                                                  data["id"]))
        assert result["source"] == "added spam", result
        assert result["memory_id"] == 1, result
        assert len(getmem(1).mem["records"]) == 1, getmem(1).mem["records"]

    def test_add_no_source(self):
        data = cPickle.loads(self.api.add("1",
                                          source="",
                                          trans="added egg"))

        assert data is None, data

    def test_add_no_trans(self):
        data = cPickle.loads(self.api.add("1",
                                          source="xxx",
                                          trans=""))

        assert data is None, data

    def test_wrong_memory(self):

        data = cPickle.loads(self.api.add("1",
                                          source="added spam",
                                          trans="added egg"))

        result = cPickle.loads(self.api.rec_by_id(str(data["memory_id"]+1),
                                                  str(data["id"])))

        assert result is None, result
        assert len(getmem(1).mem["records"]) == 1, getmem(1).mem["records"]

    def test_wrong_recid(self):

        data = cPickle.loads(self.api.add("1",
                                          source="added spam",
                                          trans="added egg"))

        result = cPickle.loads(self.api.rec_by_id(str(data["memory_id"]),
                                                  str(data["id"]+1)))

        assert result is None, result

        log = model.Data.log
        assert len(log) == 1, log


class TestUpdate(ApiTester):

    def test_simple_record(self):
        rec = self.add_record("xxx", "yyy")
        assert rec.reliability == 0, rec

        data = cPickle.loads(self.api.update(id="1",
                                             source="updated spam",
                                             trans="updated egg"))
        assert data["source"] == u"updated spam", data
        assert data["trans"] == u"updated egg", data
        assert data["reliability"] == 0, data
        assert data["validated"] == False, data
        assert data["ref_count"] == 0, data

    def test_nonexistent(self):
        data = cPickle.loads(self.api.update(id="1",
                                             source="updated spam",
                                             trans="updated egg",
                                             memory_id="1"))

        assert data["source"] == u"updated spam", data
        assert data["trans"] == u"updated egg", data

    def test_no_mem(self):
        self.add_record("xxx", "yyy")
        getmem(1).mem["records"][(u"xxx", u"yyy")].memory_id = 2

        data = cPickle.loads(self.api.update(id="1",
                                             source="updated spam",
                                             trans="updated egg"))

        assert data is None, data

    def test_bad_memid(self):
        self.add_record("xxx", "yyy")

        data = cPickle.loads(self.api.update(id="1",
                                             source="updated spam",
                                             trans="updated egg",
                                             memory_id="2"))

        assert data is None, data

    def test_j(self):
        rec = self.add_record("xxx", "yyy")
        assert rec.reliability == 0, rec

        data = cPickle.loads(self.api.update(id="1",
                                             source="日本語",
                                             trans="カタカナ"))
        assert data["source"] == u"日本語", data
        assert data["trans"] == u"カタカナ", data
        assert data["reliability"] == 0, data
        assert data["validated"] == False, data
        assert data["ref_count"] == 0, data

    def test_j_unicode(self):
        rec = self.add_record("xxx", "yyy")
        assert rec.reliability == 0, rec

        data = cPickle.loads(self.api.update(id="1",
                                             source=u"日本語",
                                             trans=u"カタカナ"))
        assert data["source"] == u"日本語", data
        assert data["trans"] == u"カタカナ", data
        assert data["reliability"] == 0, data
        assert data["validated"] == False, data
        assert data["ref_count"] == 0, data

    def test_other_values(self):
        self.add_record("xxx", "yyy")

        record = dict(source="updated spam",
                      trans="updated egg",
                      reliability=4,
                      ref_count=3,
                      validated=True,
                      created_by="Thunder",
                      modified_by="Mountain")

        data = cPickle.loads(self.api.update(id="1", **record))

        print data
        # make sure values are changed
        assert data["source"] == u"updated spam", data
        assert data["trans"] == u"updated egg", data
        assert data["reliability"] == 4, data
        assert data["validated"] == True, data
        assert data["ref_count"] == 3, data
        assert data["created_by"] == u"Thunder", data
        assert data["modified_by"] == u"Mountain", data

    def test_to_dup(self):
        rec1 = self.add_record("xxx", "yyy")
        rec2 = self.add_record("spam", "eggs")

        data = cPickle.loads(self.api.update(id="1",
                                             source="spam",
                                             trans="eggs",
                                             memory_id="1"))
        assert data["source"] == u"spam", data
        assert data["trans"] == u"eggs", data
        assert data["id"] == 1, data

        info = cPickle.loads(self.api.info("1"))
        assert info["size"] == 1, info

    def test_created_not_changed(self):
        rec1 = self.add_record("xxx", "yyy")
        rec1.date_created = model.parse_time("2000/10/10 10:10:10")

        data = cPickle.loads(self.api.update(id="1",
                                             source="spam",
                                             trans="eggs",
                                             date_created="2010/10/10 10:10:10",
                                             memory_id="1"))
        assert data["date_created"].year == 2010, data["date_created"]

    def test_reliability_then_find(self):
        rec = self.add_record("xxx", "yyy")

        assert rec.reliability == 0, rec

        getmem(1).mem["records"][(u"xxx", u"yyy")].reliability = 4

        hits = cPickle.loads(self.api.search("1", "xxx", ".5"))

        assert len(hits) == 1, hits

        hit = hits[0]

        assert hit["id"] == 1, hit
        assert hit["reliability"] == 4, hit


class TestAdd(ApiTester):

    def test_mem_doesnt_exist(self):
        data = dict(source="added spam", trans="added ham")
        rec = cPickle.loads(self.api.add("3", **data))
        assert rec is None, rec

    def test_one(self):
        data = dict(source="added spam", trans="added ham")
        rec = model.MemoryRecord(**cPickle.loads(self.api.add("1", **data)))
        assert rec.source == u"added spam", rec
        assert rec.trans == u"added ham", rec

    def test_two(self):
        data = dict(source="added spam", trans="added ham")
        rec1 = cPickle.loads(self.api.add("1", **data))

        data = dict(source="added spam2", trans="added ham2")
        rec2 = cPickle.loads(self.api.add("1", **data))

        assert rec1["id"] == 1, rec1
        assert rec2["id"] == 2, rec2

    def test_dup(self):
        data = dict(source="added spam", trans="added ham")
        rec1 = cPickle.loads(self.api.add("1", **data))
        rec2 = cPickle.loads(self.api.add("1", **data))

        print "record 1", rec1
        print "record 2", rec2
        assert rec1["source"] == rec2["source"]
        assert rec1["trans"] == rec2["trans"]
        assert rec1["id"] == rec2["id"]

    def test_add_simple_record(self):
        data = cPickle.loads(self.api.add("1", source="added spam", trans="added egg"))
        assert data["source"] == u"added spam", data
        assert data["trans"] == u"added egg", data
        assert data["memory_id"] == 1, data

    def test_simple_mem(self):
        self.api.add("1", source="added spam", trans="added egg")
        mem = getmem(1).mem
        rec = mem["records"][(u"added spam", u"added egg")]
        assert rec.source == u"added spam", rec
        assert rec.trans == u"added egg", rec

    def test_added_records(self):
        rec = self.add_record(u"spam", u"egg")
        rec.id = 3

        item = cPickle.loads(self.api.add("1", source="spam", trans="egg"))

        assert item["source"] == u"spam", item
        assert item["trans"] == u"egg", item
        assert item["memory_id"] == 1, item
        assert item["id"] == 3, item

    def test_simple_twice(self):
        data = cPickle.loads(self.api.add("1", source="added spam twice", trans="added egg twice"))
        assert data["source"] == u"added spam twice", data
        assert data["trans"] == u"added egg twice", data
        assert data["id"] == 1, data

        data = cPickle.loads(self.api.add("1", source="added spam twice", trans="added egg twice"))
        assert data["source"] == u"added spam twice", data
        assert data["trans"] == u"added egg twice", data
        assert data["id"] == 1, data

    def test_get_range_one_0_1(self):
        self.add_record(u"aaa", u"xxx")

        items = cPickle.loads(self.api.getrange("1", "0", "1"))

        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"aaa", item
        assert item["trans"] == u"xxx", item

    def test_get_range_three_0_1(self):
        model.MAKE_KEY = model.make_key_both
        self.add_record(u"aaa", u"xxx")
        self.add_record(u"bbb", u"yyy")
        self.add_record(u"ccc", u"zzz")

        items = cPickle.loads(self.api.getrange("1", "0", "1"))

        assert len(items) == 1, items
        item = items[0]
        assert item["source"] == u"bbb", item
        assert item["trans"] == u"yyy", item

    def test_get_range_three_0_10(self):
        model.MAKE_KEY = model.make_key_both
        self.add_record(u"aaa", u"xxx")
        self.add_record(u"bbb", u"yyy")
        self.add_record(u"ccc", u"zzz")

        items = cPickle.loads(self.api.getrange("1", "0", "10"))

        assert len(items) == 3, items
        item = items[0]
        assert item["source"] == u"bbb", item
        assert item["trans"] == u"yyy", item

        item = items[1]
        assert item["source"] == u"ccc", item
        assert item["trans"] == u"zzz", item

    def test_get_page_one_of_one(self):
        """
        We can get all records if they fit on one page
        """
        search.PAGE_SIZE = 3
        model.MAKE_KEY = model.make_key_both
        self.add_record(u"aaa", u"xxx")
        self.add_record(u"bbb", u"yyy")
        self.add_record(u"ccc", u"zzz")

        items = cPickle.loads(self.api.get_page("1", "1"))

        assert len(items) == 3, items
        sources = [r["source"] for r in items]

        assert "aaa" in sources, sources
        assert "bbb" in sources, sources
        assert "ccc" in sources, sources

    def test_get_page_one_of_two(self):
        """
        We get can the first of two pages.
        """
        search.PAGE_SIZE = 2
        model.MAKE_KEY = model.make_key_both
        self.add_record(u"aaa", u"xxx")
        self.add_record(u"bbb", u"yyy")
        self.add_record(u"ccc", u"zzz")

        items = cPickle.loads(self.api.get_page("1", "1"))

        assert len(items) == 2, items
        sources = [r["source"] for r in items]

        assert "aaa" in sources or "bbb" in sources, sources

    def test_get_page_two_of_two(self):
        """
        We get can the first of two pages.
        """
        search.PAGE_SIZE = 2
        model.MAKE_KEY = model.make_key_both
        self.add_record(u"aaa", u"xxx")
        self.add_record(u"bbb", u"yyy")
        self.add_record(u"ccc", u"zzz")

        items = cPickle.loads(self.api.get_page("1", "2"))

        [record] = items
        assert record["source"] in "aaa bbb ccc".split(), record

    def test_num_pages_two(self):
        """
        We get can the first of two pages.
        """
        search.PAGE_SIZE = 2
        model.MAKE_KEY = model.make_key_both
        self.add_record(u"aaa", u"xxx")
        self.add_record(u"bbb", u"yyy")
        self.add_record(u"ccc", u"zzz")

        num = cPickle.loads(self.api.num_pages("1"))

        assert num == 2, num

class TestAddOneSource(ApiTester):

    def setUp(self):
        ApiTester.setUp(self)
        model.MAKE_KEY = model.make_key_source

    def tearDown(self):
        ApiTester.tearDown(self)
        model.MAKE_KEY = model.make_key_both

    def test_mem_doesnt_exist(self):
        data = dict(source="added spam", trans="added ham")
        rec = cPickle.loads(self.api.add("3", **data))
        assert rec is None, rec

    def test_one(self):
        data = dict(source="added spam", trans="added ham")
        rec = model.MemoryRecord(**cPickle.loads(self.api.add("1", **data)))
        assert rec.source == u"added spam", rec
        assert rec.trans == u"added ham", rec

    def test_two_same_source(self):
        data = dict(source="added spam", trans="added ham")
        rec1 = cPickle.loads(self.api.add("1", **data))

        data = dict(source="added spam", trans="added ham2")
        rec2 = cPickle.loads(self.api.add("1", **data))

        assert rec1["id"] == 1, rec1
        assert rec2["id"] == 1, rec2

    def test_dup(self):
        data = dict(source="added spam", trans="added ham")
        rec1 = cPickle.loads(self.api.add("1", **data))
        rec2 = cPickle.loads(self.api.add("1", **data))

        assert rec1["source"] == rec2["source"]
        assert rec1["trans"] == rec2["trans"]
        assert rec1["id"] == rec2["id"]


class TestGetUser(ApiTester):
    def test_nomatch(self):
        name = self.api.getuser()
        assert name == u"Ryan-PC", name

    def test_noip(self):
        user = model.User(u"Sam", u"admin", u"secret", u"1.1.1.1")
        user.id = 1
        model.Data.users[1] = model.user2d(user)

        name = self.api.getuser()
        assert name == u"Ryan-PC", name

    def test_ip_nomatch(self):
        user = model.User(u"Sam", u"admin", u"secret", u"1.1.1.1")
        user.id = 1
        model.Data.users[1] = model.user2d(user)

        api.cherrypy.request.remote.ip = u"2.2.2.2"

        name = self.api.getuser()
        assert name == u"Ryan-PC", name

    def test_ip_match(self):
        user = model.User(u"Sam", u"admin", u"secret", u"1.1.1.1")
        user.id = 1
        model.Data.users[1] = model.user2d(user)

        api.cherrypy.request.remote.ip = u"1.1.1.1"

        name = self.api.getuser()
        assert name == u"Sam", name


class TestApi(ApiTester):

    def test_mems(self):
        text = self.api.mems("1")
        d = cPickle.loads(text)
        assert "add" in d, d
        assert "search" in d, d
        assert "rsearch" in d, d
        assert "gloss" in d, d
        assert "update" in d, d
        assert "delete" in d, d
        assert "concordance" in d, d
        assert "info" in d, d
        assert d["mem_info"]["name"] == u"ApiTester", d
        assert d["mem_info"]["size"] == 0, d

    def test_mems_none(self):
        text = self.api.mems("2")
        d = cPickle.loads(text)
        assert d is None, d

    def test_info(self):
        info = cPickle.loads(self.api.info("1"))
        assert info["size"] == 0, info
        assert info["name"] == u"ApiTester", info
        assert info["version"] == model.VERSION, info
        assert info["source_language"] == u"Default", info

    def test_synch_prefs_and_mem_true(self):
        prefs = {}
        prefs["normalize_case"] = True
        prefs["normalize_hira"] = True
        prefs["normalize_width"] = True

        mem = getmem(1)
        self.api.synch_prefs_and_mem(prefs, mem)

        mem = getmem(1)

        assert mem.mem["normalize_case"], mem
        assert mem.mem["normalize_hira"], mem
        assert mem.mem["normalize_width"], mem

    def test_synch_prefs_and_mem_false(self):
        prefs = {}
        prefs["normalize_case"] = False
        prefs["normalize_hira"] = False
        prefs["normalize_width"] = False

        mem = getmem(1)
        self.api.synch_prefs_and_mem(prefs, mem)

        mem = getmem(1)

        assert not mem.mem["normalize_case"], mem
        assert not mem.mem["normalize_hira"], mem
        assert not mem.mem["normalize_width"], mem

    def test_commands_rec_by_id(self):
        info = cPickle.loads(self.api.mems(1))

        expected = "http://%s:%s/api/rec_by_id/1/" % (settings.get_host(), settings.get_port())
        assert info["rec_by_id"] == expected, (expected, info["get_page"])

    def test_commands_get_page(self):
        info = cPickle.loads(self.api.mems(1))

        expected = "http://%s:%s/api/get_page/1/" % (settings.get_host(), settings.get_port())
        assert info["get_page"] == expected, (expected, info["get_page"])


class TestLogin(UserTestsDb):

    def setUp(self):
        self.api = api.Api()
        UserTestsDb.setUp(self)

    def test_success(self):
        self.add_user(u"spam", u"foo", "0.0.0.0")
        hashid = cPickle.loads(self.api.login("spam", "foo"))
        assert model.Data.logins[hashid]["name"] == "spam", model.Data.logins

    @raises(Exception)
    def test_user_does_not_exist(self):
        self.api.login("spam", "foo")


class TestGlossStuff(unittest.TestCase):
    def test_gloss_sort_key(self):
        record = model.MemoryRecord(u"1234", u"abc")
        assert api.gloss_sort_key(record) == 4, api.gloss_sort_key(record)

    def test_gloss_sort_key_richtext(self):
        record = model.MemoryRecord(u"<foo>1234</foo>", u"abc")
        assert api.gloss_sort_key(record) == 4, api.gloss_sort_key(record)

    def test_gloss_matches_sorted(self):
        rec1 = model.MemoryRecord(u"1234", u"abc")
        rec2 = model.MemoryRecord(u"123", u"abc")
        rec3 = model.MemoryRecord(u"12", u"abc")
        records = [rec3, rec1, rec2]

        matches = api.gloss_matches_sorted(records)
        m1, m2, m3 = matches
        print "m1:", m1.source
        print "m2:", m2.source
        print "m3:", m3.source
        assert matches == [rec1, rec2, rec3], matches
