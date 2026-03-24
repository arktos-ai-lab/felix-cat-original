# coding=utf-8
__author__ = 'Ryan'

import unittest
import datetime
from MemoryServesExporter import exportdata
from cStringIO import StringIO

class TestExportRecord(unittest.TestCase):
    def test_min(self):
        today = datetime.datetime.today()
        data = dict(source="foo",
                    trans="bar",
                    date_created=today,
                    last_modified=today)
        datestr = exportdata.date2str(today)

        out = StringIO()
        exportdata.export_record(out, data)
        actual = out.getvalue()
        expected = """  <record>
    <source><![CDATA[foo]]></source>
    <trans><![CDATA[bar]]></trans>
    <date_created>%s</date_created>
    <last_modified>%s</last_modified>
  </record>
""" % (datestr, datestr)
        print expected
        assert actual == expected, actual

    def test_japanese(self):
        mod = datetime.datetime(2013, 2, 5, 15, 31, 1)
        created = datetime.datetime(2013, 2, 5, 14, 37, 26)
        data = {'trans_cmp': u'上述の置換ルールにより、訳文は下記のように置き換えられます。',
                'trans': u'上述の置換ルールにより、訳文は下記のように置き換えられます。',
                'modified_by': u'Midori Horii',
                'memory_id': 1,
                'ref_count': 1,
                'source_cmp': u'the rule above would yield the following substitution:',
                'source': u'The rule above would yield the following substitution:',
                'last_modified': mod,
                'created_by': u'Midori Horii',
                'context': u'',
                'date_created': created,
                'validated': False,
                'reliability': 0,
                'id': 242}

        out = StringIO()
        exportdata.export_record(out, data)
        actual = out.getvalue()
        expected = """  <record>
    <id>242</id>
    <ref_count>1</ref_count>
    <source><![CDATA[The rule above would yield the following substitution:]]></source>
    <trans><![CDATA[上述の置換ルールにより、訳文は下記のように置き換えられます。]]></trans>
    <creator>Midori Horii</creator>
    <modified_by>Midori Horii</modified_by>
    <date_created>%s</date_created>
    <last_modified>%s</last_modified>
    <validated>false</validated>
  </record>
""" % (exportdata.date2str(created), exportdata.date2str(mod))

        for e, a in zip(expected.splitlines(), actual.splitlines()):
            assert e == a, (e, a)
        assert actual == expected, actual

    def test_reliability_and_context(self):
        mod = datetime.datetime(2013, 2, 5, 15, 31, 1)
        created = datetime.datetime(2013, 2, 5, 14, 37, 26)
        data = {'trans_cmp': u'trans',
                'trans': u'trans',
                'modified_by': u'Midori Horii',
                'context': "context",
                'memory_id': 1,
                'ref_count': 1,
                'source_cmp': u'source',
                'source': u'source',
                'last_modified': mod,
                'created_by': u'Midori Horii',
                'date_created': created,
                'validated': False,
                'reliability': 4,
                'id': 242}

        out = StringIO()
        exportdata.export_record(out, data)
        actual = out.getvalue()
        expected = """  <record>
    <id>242</id>
    <ref_count>1</ref_count>
    <source><![CDATA[source]]></source>
    <trans><![CDATA[trans]]></trans>
    <context><![CDATA[context]]></context>
    <creator>Midori Horii</creator>
    <modified_by>Midori Horii</modified_by>
    <date_created>%s</date_created>
    <last_modified>%s</last_modified>
    <validated>false</validated>
    <reliability>4</reliability>
  </record>
""" % (exportdata.date2str(created), exportdata.date2str(mod))

        for e, a in zip(expected.splitlines(), actual.splitlines()):
            assert e == a, (e, a)
        assert actual == expected, actual

    def test_formatting(self):
        mod = datetime.datetime(2013, 2, 5, 15, 31, 1)
        created = datetime.datetime(2013, 2, 5, 14, 37, 26)
        data = {'trans_cmp': u'foo & bar',
                'trans': u'<FONT FACE="Arial">foo &amp; bar</FONT>',
                'modified_by': u'Midori Horii',
                'memory_id': 1,
                'ref_count': 1,
                'source_cmp': u'fizz & buzz',
                'source': u'<FONT FACE="Century">fizz &amp; buzz</FONT>',
                'last_modified': mod,
                'created_by': u'Midori Horii',
                'context': u'',
                'date_created': created,
                'validated': False,
                'reliability': 0,
                'id': 242}

        out = StringIO()
        exportdata.export_record(out, data)
        actual = out.getvalue()
        expected = """  <record>
    <id>242</id>
    <ref_count>1</ref_count>
    <source><![CDATA[<FONT FACE="Century">fizz &amp; buzz</FONT>]]></source>
    <trans><![CDATA[<FONT FACE="Arial">foo &amp; bar</FONT>]]></trans>
    <creator>Midori Horii</creator>
    <modified_by>Midori Horii</modified_by>
    <date_created>%s</date_created>
    <last_modified>%s</last_modified>
    <validated>false</validated>
  </record>
""" % (exportdata.date2str(created), exportdata.date2str(mod))

        for e, a in zip(expected.splitlines(), actual.splitlines()):
            assert e == a, (e, a)
        assert actual == expected, actual

class TestMassageRecData(unittest.TestCase):
    def test_empty(self):
        data = {}
        today = datetime.datetime.today()
        actual = exportdata.massage_rec_data(data)
        start = today.strftime("%Y/%m/%d")

        assert len(actual) == 2, actual

        assert actual["date_created"].startswith(start), actual
        assert actual["last_modified"].startswith(start), actual

    def test_japanese(self):
        data = {'trans_cmp': u'上述の置換ルールにより、訳文は下記のように置き換えられます。',
                'trans': u'<FONT FACE="ＭＳ 明朝">上述の置換ルールにより、訳文は下記のように置き換えられます。</FONT>',
                'modified_by': u'Midori Horii',
                'memory_id': 1,
                'ref_count': 1,
                'source_cmp': u'the rule above would yield the following substitution:',
                'source': u'<FONT FACE="Century">The rule above would yield the following substitution:</FONT>',
                'last_modified': datetime.datetime(2013, 2, 5, 15, 31, 1),
                'created_by': u'Midori Horii',
                'context': u'',
                'date_created': datetime.datetime(2013, 2, 5, 14, 37, 26),
                'validated': False,
                'reliability': 0,
                'id': 242}

        actual = exportdata.massage_rec_data(data)

        assert "reliability" not in actual

        EXPECTATIONS = [("last_modified", "2013/02/05 15:31:01"),
                        ("date_created", "2013/02/05 14:37:26"),
                        ("creator", u'Midori Horii'),
                        ('id', u"242"),
                        ("source", u"""<FONT FACE="Century">The rule above would yield the following substitution:</FONT>"""),
                        ("trans", u"""<FONT FACE="ＭＳ 明朝">上述の置換ルールにより、訳文は下記のように置き換えられます。</FONT>"""),
                        ("ref_count", 1),
                        ("validated", "false")
        ]

        for key, expected in EXPECTATIONS:
            assert actual[key] == expected, actual[key]
