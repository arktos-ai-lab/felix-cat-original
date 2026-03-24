#coding: UTF8
"""
Enter module description here.
"""

import unittest
import md5
import time
import datetime

import mock

from .. import model
from .. import dataloader


class TestEnsureU(object):
    def test_unicode(self):
        term = u"日本語"
        uterm = model.ensure_u(term)
        assert term is uterm, repr(uterm)

    def test_utf8(self):
        term = "日本語"
        uterm = model.ensure_u(term)
        assert uterm == u"日本語", repr(uterm)

    def test_sjis(self):
        term = u"日本語".encode("sjis")
        uterm = model.ensure_u(term)
        assert uterm == repr(term), repr(uterm)


class TestMem2D(object):
    def test_memtype(self):
        mem = mock.MagicMock()
        mem.records = []
        mem.memtype = "mock"

        memd = model.mem2d(mem)

        assert memd["memtype"] == "mock", memd


class TestIsKeyValid(unittest.TestCase):
    def test_string_true(self):
        key = u"foo"
        assert model.is_key_valid(key)
    def test_string_false(self):
        key = u""
        assert not model.is_key_valid(key)
    def test_tuple_true(self):
        key = (u"foo", u"bar")
        assert model.is_key_valid(key)
    def test_tuple_false_one(self):
        key = (u"foo", None)
        assert not model.is_key_valid(key)
    def test_tuple_false_two(self):
        key = (None, None)

class TestMakeKeyBoth(unittest.TestCase):
    def test_empty(self):
        key = model.make_key_both({})
        assert key == (u'', u''), key
    def test_aaa_bbb(self):
        key = model.make_key_both(dict(source='aaa', trans='bbb'))
        assert key == (u'aaa', u'bbb'), key
    def test_record(self):
        rec = model.MemoryRecord("x", "y")
        key = model.make_key_both(rec)
        assert key == (u'x', u'y'), key

class TestMakeKeySource(unittest.TestCase):
    def test_empty(self):
        key = model.make_key_source({})
        assert key == u'', key
    def test_aaa_bbb(self):
        key = model.make_key_source(dict(source='aaa', trans='bbb'))
        assert key == u'aaa', key
    def test_record(self):
        rec = model.MemoryRecord("x", "y")
        key = model.make_key_source(rec)
        assert key == u'x', key

class TestModelFuncs(unittest.TestCase):
    def test_user_name(self):
        assert model.USER_NAME == u"Ryan", model.USER_NAME

    def test_bad_date(self):
        bad_date = "??:00:00 00:00:00"
        thedate = model.parse_time(bad_date)
        assert str(thedate).startswith("201"), thedate

    def test_make_unicode_u(self):
        obj = model.make_unicode(u"spam")
        assert isinstance(obj, unicode), obj
        assert obj == u"spam", obj

    def test_make_unicode_a(self):
        obj = model.make_unicode("spam")
        assert isinstance(obj, unicode), obj
        assert obj == u"spam", obj

class ModelTest(unittest.TestCase):
    pass

class TestUser(ModelTest):

    def test_create(self):
        user = model.User(u"ryan", u"admin", u"secret", u"1.1.1.1")
        assert user.name == u"ryan"
        assert user.password == md5.new(u"secret").hexdigest()
        assert user.ip == u"1.1.1.1"

    def test_create_id(self):
        user = model.User(u"ryan", u"admin", u"secret", u"1.1.1.1", id=3)
        assert user.id == 3, user

    def test_passwords_match(self):
        user = model.User(u"ryan", u"admin", u"secret", u"1.1.1.1")
        assert user.passwords_match(u"secret")

    def test_passwords_match_false(self):
        user = model.User(u"ryan", u"admin", u"secret", u"1.1.1.1")
        assert not user.passwords_match(u"public")

    # Ranks
    def test_rank_admin(self):
        user = model.User(u"ryan", u"admin", u"secret", u"1.1.1.1")
        assert user.get_rank() == 3, user.get_rank()
    def test_rank_user(self):
        user = model.User(u"ryan", u"user", u"secret", u"1.1.1.1")
        assert user.get_rank() == 2, user.get_rank()
    def test_rank_guest(self):
        user = model.User(u"ryan", u"guest", u"secret", u"1.1.1.1")
        assert user.get_rank() == 1, user.get_rank()
    def test_rank_anon(self):
        user = model.User(u"ryan", u"", u"secret", u"1.1.1.1")
        assert user.get_rank() == 0, user.get_rank()
    def test_rank_spam(self):
        user = model.User(u"ryan", u"spam", u"secret", u"1.1.1.1")
        assert user.get_rank() == 0, user.get_rank()


class TestMemoryRecord(unittest.TestCase):

    def test_cmp(self):
        rec = model.MemoryRecord(u"<strong>spam</strong>", u"""<font style="color: red">egg</font>""")

        assert rec.source_cmp == "spam", rec.source_cmp
        assert rec.trans_cmp == "egg", rec.trans_cmp

    def test_cmp_complex(self):
        rec = model.MemoryRecord(u"""I <b>love <i>spam</i></b> in the morning!""", u"""<font style="color: red">egg</font>""")

        assert rec.source_cmp.lower() == u"i love spam in the morning!", rec.source_cmp

    def test_id(self):
        rec = model.MemoryRecord(u"source", u"trans", id="3")
        assert rec.id == 3, rec

    def test_created(self):
        rec = model.MemoryRecord(u"source", u"trans", date_created="2007/11/12 12:12:12")
        print rec.date_created
        assert rec.date_created.strftime("%Y") == "2007", rec.date_created.strftime("%Y")

    def test_id_none(self):
        rec = model.MemoryRecord(u"source", u"trans")
        assert rec.id == 0, rec

    def test_memory_id(self):
        rec = model.MemoryRecord(u"source", u"trans", memory_id="3")
        assert rec.memory_id == 3, rec

    def test_memory_id_none(self):
        rec = model.MemoryRecord(u"source", u"trans")
        assert rec.memory_id == 0, rec

    def test_validated_False(self):
        rec = model.MemoryRecord(u"x", u"y", validated=False)
        assert rec.validated == False, rec

    def test_validated_True(self):
        rec = model.MemoryRecord(u"x", u"y", validated=True)
        assert rec.validated == True, rec

    def test_validated_str_False(self):
        rec = model.MemoryRecord(u"x", u"y", validated="False")
        assert rec.validated == False, rec

    def test_validated_str_True(self):
        rec = model.MemoryRecord(u"x", u"y", validated="True")
        assert rec.validated == True, rec

    def test_key(self):
        rec = model.MemoryRecord(u"x", u"y", validated="True")
        assert rec.key == (u"x", u"y"), rec

class TestRecordModel(ModelTest):

    def test_cmp(self):
        rec = model.Record(u"<strong>spam</strong>", u"""<font style="color: red">egg</font>""")

        assert rec.source_cmp == "spam", rec.source_cmp
        assert rec.trans_cmp == "egg", rec.trans_cmp

    def test_cmp_complex(self):
        rec = model.Record(u"""I <b>love <i>spam</i></b> in the morning!""", u"""<font style="color: red">egg</font>""")

        assert rec.source_cmp.lower() == u"i love spam in the morning!", rec.source_cmp

    def test_id(self):
        rec = model.Record(u"source", u"trans", id="3")
        assert rec.id == 3, rec

    def test_id_none(self):
        rec = model.Record(u"source", u"trans")
        assert rec.id == 0, rec

    def test_memory_id(self):
        rec = model.Record(u"source", u"trans", memory_id="3")
        assert rec.memory_id == 3, rec

    def test_memory_id_none(self):
        rec = model.Record(u"source", u"trans")
        assert rec.memory_id == 0, rec

    def test_validated_False(self):
        rec = model.Record(u"x", u"y", validated=False)
        assert rec.validated == False, rec

    def test_validated_True(self):
        rec = model.Record(u"x", u"y", validated=True)
        assert rec.validated == True, rec

    def test_validated_str_False(self):
        rec = model.Record(u"x", u"y", validated="False")
        assert rec.validated == False, rec

    def test_validated_str_True(self):
        rec = model.Record(u"x", u"y", validated="True")
        assert rec.validated == True, rec

class TestVariousModelStuff(unittest.TestCase):
    def test_parse_validated_keyerr(self):
        value = model.parse_validated("foo")
        assert value == True, value

    def test_percent_validated(self):
        records = { 1 : model.MemoryRecord(source=u"foo", trans=u"bar", validated="true"),
                    2 : model.MemoryRecord(source=u"spam", trans=u"eggs", validated="false")}
        memory = dict(records=records)
        percent = model.percent_validated(memory)
        assert percent == .5, percent

    def test_reliability_stats(self):
        records = { 1 : model.MemoryRecord(source=u"foo", trans=u"bar", reliability=4),
                    2 : model.MemoryRecord(source=u"spam", trans=u"eggs", reliability=8)}
        memory = dict(records=records)
        low, high, ave = model.reliability_stats(memory)

        assert low == 4, low
        assert high == 8, high
        assert ave == 6.0, ave


class TestMassageRecords(unittest.TestCase):
    def test_empty(self):
        records = {}

        mrecords = dict((model.MAKE_KEY(r), r) for r in dataloader.massage_records(records))

        assert mrecords == {}, mrecords

    def test_dicts(self):
        records = { 1 : dict(source=u"foo", trans=u"bar"),
                    2 : dict(source=u"spam", trans=u"eggs")}

        mrecords = dict((model.MAKE_KEY(r), r) for r in dataloader.massage_records(records))

        key1 = model.MAKE_KEY(records[1])
        assert mrecords[key1].source == u"foo", mrecords[key1].source
        key2 = model.MAKE_KEY(records[2])
        assert mrecords[key2].trans == u"eggs", mrecords[key2].trans

    def test_records(self):
        records = { 1 : model.MemoryRecord(source=u"foo", trans=u"bar"),
                    2 : model.MemoryRecord(source=u"spam", trans=u"eggs")}

        mrecords = dict((model.MAKE_KEY(r), r) for r in dataloader.massage_records(records))

        key1 = model.MAKE_KEY(records[1])
        assert mrecords[key1].source == u"foo", mrecords[key1].source
        key2 = model.MAKE_KEY(records[2])
        assert mrecords[key2].trans == u"eggs", mrecords[key2].trans

class TestMassageMemories(unittest.TestCase):

    def test_records(self):
        records = { 1 : model.MemoryRecord(source=u"foo", trans=u"bar"),
                    2 : model.MemoryRecord(source=u"spam", trans=u"eggs")}
        memories = { 1 : model.TranslationMemory(dict(records=records,
                                                      name="test_dicts",
                                                      id=1))}

        dataloader.massage_memories(memories)

        key1 = model.MAKE_KEY(records[1])
        key2 = model.MAKE_KEY(records[2])
        assert memories[1].mem["records"][key1].source == u"foo", records
        assert memories[1].mem["records"][key2].trans == u"eggs", records

class TestMemory(ModelTest):
    def test_created(self):
        mem = model.Memory(u"TestMemory", u"m", created_on="2008/03/13 09:41:45")
        t = mem.created_on

        assert t.year == 2008, t
        assert t.month == 3, t
        assert t.day == 13, t
        assert t.hour == 9, t
        assert t.minute == 41, t
        assert t.second == 45, t

    def test_records_empty(self):
        mem = model.Memory(u"TestMemory", u"m", created_on="2008/03/13 09:41:45")
        assert mem.records == [], mem.records

def test_get_data():
    mem = model.TranslationMemory(dict(records={}))
    model.Data.memories = dict(m=mem)
    model.Data.users = dict(u=1)
    model.Data.log = [1]
    model.Data.next_id = 3

    data = dataloader.get_data()
    assert data["memories"] == dict(m=mem.mem), data
    assert data["users"] == dict(u=1), data
    assert data["log"] == [1], data
    assert data["next_id"] == 3, data


class TestModelParsing(unittest.TestCase):
    def test_parse_time_none(self):
        t = model.parse_time(None)
        year = str(time.localtime()[0])
        assert str(t).startswith(year), t

    def test_parse_time_str(self):
        t = model.parse_time("2008/01/01 12:12:12")
        print dir(t)
        assert t.year == 2008, t
        assert t.month == 1, t
        assert t.day == 1, t
        assert t.hour == 12, t
        assert t.minute == 12, t
        assert t.second == 12, t


class TestUpdateRecValues(unittest.TestCase):
    def test_source(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(source="<b>spam</b>")
        rec.update(values)
        assert rec.source == u"<b>spam</b>", rec
        assert rec.source_cmp == u"spam", rec

    def test_source_j(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(source="<b>本日は晴天なり</b>")
        rec.update(values)
        assert rec.source == u"<b>本日は晴天なり</b>", rec
        assert rec.source_cmp == u"本日ハ晴天ナリ", rec

    def test_trans(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(trans="<b>spam</b>")
        rec.update(values)
        assert rec.trans == u"<b>spam</b>", rec
        assert rec.trans_cmp == u"spam", rec

    def test_date_created(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(date_created="2008/01/01 10:10:10")
        rec.update(values)
        assert rec.date_created == datetime.datetime(2008, 1, 1, 10, 10, 10), rec

    def test_last_modified(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(last_modified="2008/01/01 10:10:10")
        rec.update(values)
        assert rec.last_modified == datetime.datetime(2008, 1, 1, 10, 10, 10), rec

    def test_reliability(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(reliability="5")
        rec.update(values)
        assert rec.reliability == 5, rec

    def test_validated_true(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(validated="true")
        rec.update(values)
        assert rec.validated == True, rec

    def test_validated_true(self):
        rec = model.MemoryRecord(u"foo", u"bar", validated="True")
        values = dict(validated="false")
        rec.update(values)
        assert rec.validated == False, rec

    def test_ref_count(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(ref_count="5")
        rec.update(values)
        assert rec.ref_count == 5, rec

    def test_context(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(context="hello")
        rec.update(values)
        assert rec.context == u"hello", rec

    def test_context_j(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(context="日本語")
        rec.update(values)
        assert rec.context == u"日本語", rec

    def test_created_by(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(created_by="hello")
        rec.update(values)
        assert rec.created_by == u"hello", rec

    def test_created_by_j(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(created_by="日本語")
        rec.update(values)
        assert rec.created_by == u"日本語", rec

    def test_modified_by(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(modified_by="hello")
        rec.update(values)
        assert rec.modified_by == u"hello", rec

    def test_source_and_reliability(self):
        rec = model.MemoryRecord(u"foo", u"bar")
        values = dict(source="<b>spam</b>", reliability="9")
        rec.update(values)
        assert rec.source == u"<b>spam</b>", rec
        assert rec.source_cmp == u"spam", rec
        assert rec.reliability == 9, rec

class TestRecord(unittest.TestCase):
    def test_created(self):
        rec = model.Record(u"spam", u"egg", date_created="2008/03/13 09:41:45")

        t = rec.date_created

        assert t.year == 2008, t
        assert t.month == 3, t
        assert t.day == 13, t
        assert t.hour == 9, t
        assert t.minute == 41, t
        assert t.second == 45, t

    def test_validated_true(self):
        rec = model.Record(u"spam", u"egg", validated="true")
        assert rec.validated == True, rec.validated

    def test_validated_false(self):
        rec = model.Record(u"spam", u"egg", validated="false")
        assert rec.validated == False, rec.validated

    def test_validated_zero(self):
        rec = model.Record(u"spam", u"egg", validated=0)
        assert rec.validated == False, rec.validated

    def test_extra_key(self):
        rec = model.Record(u"spam", u"egg", foo="bar")
        assert rec.source == u"spam"
        assert rec.trans == u"egg"
