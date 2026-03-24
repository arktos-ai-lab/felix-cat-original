#encoding: UTF8
#!/usr/bin/env python

import logging
import unittest
import datetime

from nose.tools import raises

import fake_cherrypy
from .. import main
from .. import model
from .. import settings
from .. import search
from .. import repository


search.logger.setLevel(logging.DEBUG)

class TestMakeXmlFilename(unittest.TestCase):
    def test_bare(self):
        name = "spam"
        asxml = search.make_xml_filename(name, True)
        assert asxml == "spam.ftm", asxml
    def test_text(self):
        name = "spam.txt"
        asxml = search.make_xml_filename(name, True)
        assert asxml == "spam.ftm", asxml
    def test_ftm(self):
        name = "spam.xml"
        asxml = search.make_xml_filename(name, True)
        assert asxml == "spam.ftm", asxml
    def test_fgloss(self):
        name = "spam.xml"
        asxml = search.make_xml_filename(name, False)
        assert asxml == "spam.fgloss", asxml
    def test_period(self):
        name = "spam."
        asxml = search.make_xml_filename(name, True)
        assert asxml == "spam.ftm", asxml
    def test_fullpath_xml(self):
        name = "c:\\path\\spam.ftm"
        asxml = search.make_xml_filename(name, True)
        assert asxml == "c:\\path\\spam.ftm", asxml
    def test_fullpath_bare(self):
        name = "c:\\path\\spam"
        asxml = search.make_xml_filename(name, True)
        assert asxml == "c:\\path\\spam.ftm", asxml
    def test_ftm(self):
        name = "c:\\path\\spam.ftm"
        asxml = search.make_xml_filename(name, True)
        assert asxml == "c:\\path\\spam.ftm", asxml

    def test_spaces(self):
        name = "spam gloss.txt"
        astmx = search.make_xml_filename(name, True)
        assert astmx == "spam_gloss.ftm", astmx

    def test_spaces_fgloss(self):
        name = "spam gloss.txt"
        astmx = search.make_xml_filename(name, False)
        assert astmx == "spam_gloss.fgloss", astmx

    def test_spaces_xml(self):
        name = "spam gloss.xml"
        astmx = search.make_xml_filename(name, True)
        assert astmx == "spam_gloss.ftm", astmx


class TestMakeTmxFilename(unittest.TestCase):
    def test_bare(self):
        name = "spam"
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam.tmx", astmx
    def test_text(self):
        name = "spam.txt"
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam.tmx", astmx
    def test_xml(self):
        name = "spam.xml"
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam.tmx", astmx
    def test_tmx(self):
        name = "spam.tmx"
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam.tmx", astmx
    def test_period(self):
        name = "spam."
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam.tmx", astmx
    def test_fullpath_tmx(self):
        name = "c:\\path\\spam.tmx"
        astmx = search.make_tmx_filename(name)
        assert astmx == "c:\\path\\spam.tmx", astmx
    def test_fullpath_bare(self):
        name = "c:\\path\\spam"
        astmx = search.make_tmx_filename(name)
        assert astmx == "c:\\path\\spam.tmx", astmx
    def test_ftm(self):
        name = "c:\\path\\spam.ftm"
        astmx = search.make_tmx_filename(name)
        assert astmx == "c:\\path\\spam.tmx", astmx
    def test_xml(self):
        name = "c:\\path\\spam.xml"
        astmx = search.make_tmx_filename(name)
        assert astmx == "c:\\path\\spam.tmx", astmx

    def test_spaces(self):
        name = "spam gloss.xml"
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam_gloss.tmx", astmx

    def test_spaces_xml(self):
        name = "spam gloss.xml"
        astmx = search.make_tmx_filename(name)
        assert astmx == "spam_gloss.tmx", astmx


class TestSetPagination(unittest.TestCase):
    def test_set_pagination(self):
        """
        def set_pagination(context, page, count, start):
        Set the pagination information for search and browse pages

        page = int(page)
        context["num"] = format_num(count)
        context["page"] = page
        end = start + PAGE_SIZE

        context["has_next"] = count > end
        context["next_page"] = page+1
        context["has_prev"] = page > 1
        context["prev_page"] = page-1
        context["page_size"] = PAGE_SIZE

        extra = min(1, count % PAGE_SIZE)
        context["num_pages"] = format_num((count / PAGE_SIZE) + extra)
        return context
        """

        page = "1"
        count = 1001
        old_page_size = search.PAGE_SIZE
        try:
            search.PAGE_SIZE = 10
            context = search.set_pagination({}, page, count)

            assert context["num"] == "1,001", context
            assert context["has_next"] == True, context
            assert context["has_prev"] == False, context
            assert context["page_size"] == 10, context
            assert context["prev_page"] == 0, context
            assert context["next_page"] == 2, context
            assert context["num_pages"] == "101", context

            assert context["page_start"] == 0, context
            assert context["page_end"] == 10, context
            assert context["pages"] == range(1,11), context


        finally:
            search.PAGE_SIZE = old_page_size


class TestMemTruther(object):
    def test_true(self):
        assert search.mem_truther("true") == "true"

    def test_foo(self):
        assert search.mem_truther("foo") == "false"

class TestTermToDate(unittest.TestCase):
    @raises(ValueError)
    def test_empty(self):
        search.term_to_date("")

    def test_hyphens(self):
        when = search.term_to_date("2000-10-1")
        assert when.year == 2000, when
        assert when.month == 10, when
        assert when.day == 1, when

    def test_slashes(self):
        when = search.term_to_date("2000/10/1")
        assert when.year == 2000, when
        assert when.month == 10, when
        assert when.day == 1, when

class TestEnsureU(unittest.TestCase):
    def test_unicode(self):
        term = u"spam"
        term = search.ensure_u(term)
        assert isinstance(term, unicode)
        assert term == u"spam", term

    def test_utf8(self):
        term = "spam"
        term = search.ensure_u(term)
        assert isinstance(term, unicode)
        assert term == u"spam", term

class TestSearchQuery(unittest.TestCase):
    def test_init(self):
        sq = search.SearchQuery(u"foo")
        assert sq.querytype == "general", sq
        assert sq.isregex == False, sq
        assert sq.query == "foo", sq

    def test_source(self):
        sq = search.SearchQuery(u"source:test_term")
        assert sq.querytype == "source", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_trans(self):
        sq = search.SearchQuery(u"trans:test_term")
        assert sq.querytype == "trans", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_context(self):
        sq = search.SearchQuery(u"context:test_term")
        assert sq.querytype == "context", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

        # created
    def test_created_by(self):
        sq = search.SearchQuery(u"created-by:test_term")
        assert sq.querytype == "created-by", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_created_before(self):
        sq = search.SearchQuery(u"created-before:test_term")
        assert sq.querytype == "created-before", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_created_after(self):
        sq = search.SearchQuery(u"created-after:test_term")
        assert sq.querytype == "created-after", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

        # modified
    def test_modified_by(self):
        sq = search.SearchQuery(u"modified-by:test_term")
        assert sq.querytype == "modified-by", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_modified_before(self):
        sq = search.SearchQuery(u"modified-before:test_term")
        assert sq.querytype == "modified-before", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_modified_after(self):
        sq = search.SearchQuery(u"modified-after:test_term")
        assert sq.querytype == "modified-after", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

        # reliability
    def test_reliability_gt(self):
        sq = search.SearchQuery(u"reliability-gt:test_term")
        assert sq.querytype == "reliability-gt", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_reliability_gte(self):
        sq = search.SearchQuery(u"reliability-gte:test_term")
        assert sq.querytype == "reliability-gte", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_reliability_lt(self):
        sq = search.SearchQuery(u"reliability-lt:test_term")
        assert sq.querytype == "reliability-lt", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_reliability_lte(self):
        sq = search.SearchQuery(u"reliability-lte:test_term")
        assert sq.querytype == "reliability-lte", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_reliability(self):
        sq = search.SearchQuery(u"reliability:test_term")
        assert sq.querytype == "reliability", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

        # validated
    def test_validated(self):
        sq = search.SearchQuery(u"validated:test_term")
        assert sq.querytype == "validated", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

        # ref_count
    def test_refcount(self):
        sq = search.SearchQuery(u"refcount:test_term")
        assert sq.querytype == "refcount", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_refcount_gt(self):
        sq = search.SearchQuery(u"refcount-gt:test_term")
        assert sq.querytype == "refcount-gt", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_refcount_gte(self):
        sq = search.SearchQuery(u"refcount-gte:test_term")
        assert sq.querytype == "refcount-gte", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_refcount_lt(self):
        sq = search.SearchQuery(u"refcount-lt:test_term")
        assert sq.querytype == "refcount-lt", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

    def test_refcount_lte(self):
        sq = search.SearchQuery(u"refcount-lte:test_term")
        assert sq.querytype == "refcount-lte", sq
        assert sq.isregex == False, sq
        assert sq.query == "test_term", sq

class TestSearchQueryRegex(unittest.TestCase):
    def test_init(self):
        sq = search.SearchQuery(u"regex:foo")
        assert sq.querytype == "general", sq
        assert sq.isregex == True, sq
        assert sq.query == "foo", sq

    def test_source(self):
        sq = search.SearchQuery(u"source:regex:test_term")
        assert sq.querytype == "source", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_trans(self):
        sq = search.SearchQuery(u"trans:regex:test_term")
        assert sq.querytype == "trans", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_context(self):
        sq = search.SearchQuery(u"context:regex:test_term")
        assert sq.querytype == "context", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

        # created
    def test_created_by(self):
        sq = search.SearchQuery(u"created-by:regex:test_term")
        assert sq.querytype == "created-by", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_created_before(self):
        sq = search.SearchQuery(u"created-before:regex:test_term")
        assert sq.querytype == "created-before", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_created_after(self):
        sq = search.SearchQuery(u"created-after:regex:test_term")
        assert sq.querytype == "created-after", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

        # modified
    def test_modified_by(self):
        sq = search.SearchQuery(u"modified-by:regex:test_term")
        assert sq.querytype == "modified-by", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_modified_before(self):
        sq = search.SearchQuery(u"modified-before:regex:test_term")
        assert sq.querytype == "modified-before", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_modified_after(self):
        sq = search.SearchQuery(u"modified-after:regex:test_term")
        assert sq.querytype == "modified-after", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

        # reliability
    def test_reliability_gt(self):
        sq = search.SearchQuery(u"reliability-gt:regex:test_term")
        assert sq.querytype == "reliability-gt", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_reliability_gte(self):
        sq = search.SearchQuery(u"reliability-gte:regex:test_term")
        assert sq.querytype == "reliability-gte", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_reliability_lt(self):
        sq = search.SearchQuery(u"reliability-lt:regex:test_term")
        assert sq.querytype == "reliability-lt", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_reliability_lte(self):
        sq = search.SearchQuery(u"reliability-lte:regex:test_term")
        assert sq.querytype == "reliability-lte", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_reliability(self):
        sq = search.SearchQuery(u"reliability:regex:test_term")
        assert sq.querytype == "reliability", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

        # validated
    def test_validated(self):
        sq = search.SearchQuery(u"validated:regex:test_term")
        assert sq.querytype == "validated", sq
        assert sq.isregex is True, sq
        assert sq.query == "test_term", sq

    def test_validated_regex_order_reversed(self):
        sq = search.SearchQuery(u"regex:validated:test_term")
        assert sq.querytype == "validated", sq
        assert sq.isregex is True, sq
        assert sq.query == "test_term", sq

        # ref_count
    def test_refcount(self):
        sq = search.SearchQuery(u"refcount:regex:test_term")
        assert sq.querytype == "refcount", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_refcount_gt(self):
        sq = search.SearchQuery(u"refcount-gt:regex:test_term")
        assert sq.querytype == "refcount-gt", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_refcount_gte(self):
        sq = search.SearchQuery(u"refcount-gte:regex:test_term")
        assert sq.querytype == "refcount-gte", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_refcount_lt(self):
        sq = search.SearchQuery(u"refcount-lt:regex:test_term")
        assert sq.querytype == "refcount-lt", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

    def test_refcount_lte(self):
        sq = search.SearchQuery(u"refcount-lte:regex:test_term")
        assert sq.querytype == "refcount-lte", sq
        assert sq.isregex == True, sq
        assert sq.query == "test_term", sq

class TestDoReplacement(unittest.TestCase):
    def setUp(self):

        self.record = model.MemoryRecord(source=u"The source string",
                                   trans=u"The translation string",
                                   context=u"This is the context",
                                   date_created=datetime.datetime(2009, 1, 1),
                                   created_by=u"Ryan Ginstrom",
                                   last_modified=datetime.datetime(2009, 2, 1),
                                   modified_by=u"Ryan Ginstrom",
                                   reliability=5,
                                   validated=True)

    def test_no_tag(self):
        context = dict(found=self.record,
                       replacefrom=u"The",
                       replaceto=u"That")
        result = search.do_replacement(context)
        assert result.source == u"That source string", result
        assert result.trans == u"That translation string", result
        assert result.source_cmp == u"that source string", result
        assert result.trans_cmp == u"that translation string", result.trans_cmp


    def test_source(self):
        context = dict(found=self.record,
                       replacefrom=u"source:source",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.source == u"The xxx string", result
        assert result.source_cmp == u"the xxx string", result.source_cmp

    def test_source_bold(self):
        self.record.source = u"<b>I love source</b>"
        self.record.source_cmp = settings.normalize(self.record.source)
        context = dict(found=self.record,
                       replacefrom=u"source:source",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.source == u"<b>I love xxx</b>", result
        assert result.source_cmp == u"i love xxx", result

    def test_source_not_changed(self):
        context = dict(found=self.record,
                       replacefrom=u"source:source",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert self.record.source == u"The source string", self.record
        assert self.record.source_cmp == u"the source string", self.record

    def test_source_japanese(self):
        self.record.source = u"本日は晴天なり"
        context = dict(found=self.record,
                       replacefrom=u"source:本日",
                       replaceto=u"昨夜")
        result = search.do_replacement(context)
        assert result.source == u"昨夜は晴天なり", result
        assert result.source_cmp == u"昨夜ハ晴天ナリ", result.source_cmp.encode("utf-8")

    def test_source_asterisk(self):
        context = dict(found=self.record,
                       replacefrom=u"source:*",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.source == u"xxx", result
        assert result.source_cmp == u"xxx", result

    def test_trans(self):
        context = dict(found=self.record,
                       replacefrom=u"trans:translation",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.trans == u"The xxx string", result
        assert result.trans_cmp == u"the xxx string", result

    def test_trans_asterisk(self):
        context = dict(found=self.record,
                       replacefrom=u"trans:*",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.trans == u"xxx", result
        assert result.trans_cmp == u"xxx", result

    def test_context(self):
        context = dict(found=self.record,
                       replacefrom=u"context:context",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.context == u"This is the xxx", result
        assert self.record.context == u"This is the context", self.record

    def test_context_asterisk(self):
        context = dict(found=self.record,
                       replacefrom=u"context:*",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.context == u"xxx", result

    def test_created_by(self):
        context = dict(found=self.record,
                       replacefrom=u"created-by:Ginstrom",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.created_by == u"Ryan xxx", result

    def test_created_by_asterisk(self):
        context = dict(found=self.record,
                       replacefrom=u"created-by:*",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.created_by == u"xxx", result

    def test_modified_by(self):
        context = dict(found=self.record,
                       replacefrom=u"modified-by:Ginstrom",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.modified_by == u"Ryan xxx", result

    def test_modified_by_asterisk(self):
        main_key = "modified_by"
        context = dict(found=self.record,
                       replacefrom=u"modified-by:*",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.modified_by == u"xxx", result

    def test_reliability(self):
        context = dict(found=self.record,
                       replacefrom=u"reliability:",
                       replaceto=u"8")
        result = search.do_replacement(context)
        assert result.reliability == 8, result

    def test_validated(self):
        context = dict(found=self.record,
                       replacefrom=u"validated:",
                       replaceto=u"false")
        result = search.do_replacement(context)
        assert result.validated == False, result

    def test_refcount(self):
        context = dict(found=self.record,
                       replacefrom=u"refcount:",
                       replaceto=u"101")
        result = search.do_replacement(context)

        assert result.ref_count == 101, result

    def test_created(self):
        context = dict(found=self.record,
                       replacefrom=u"created:",
                       replaceto=u"2000-05-15")
        result = search.do_replacement(context)

        assert result.date_created.year == 2000, result
        assert result.date_created.month == 5, result
        assert result.date_created.day == 15, result

    def test_modified(self):
        context = dict(found=self.record,
                       replacefrom=u"modified:",
                       replaceto=u"1999-8-30")
        result = search.do_replacement(context)

        assert result.last_modified.year == 1999, result
        assert result.last_modified.month == 8, result
        assert result.last_modified.day == 30, result



class TestDoReplacementRegex(unittest.TestCase):
    def setUp(self):

        self.record = model.MemoryRecord(source=u"The source string",
                                   trans=u"The translation string",
                                   context=u"This is the context",
                                   date_created=datetime.datetime(2009, 1, 1),
                                   created_by=u"Ryan Ginstrom",
                                   last_modified=datetime.datetime(2009, 2, 1),
                                   modified_by=u"Ryan Ginstrom",
                                   reliability=5,
                                   validated=True)


    def test_no_tag(self):
        context = dict(found=self.record,
                       replacefrom=u"regex:The\\s",
                       replaceto=u"That-")
        result = search.do_replacement(context)
        assert result.source == u"That-source string", result
        assert result.trans == u"That-translation string", result
        assert result.source_cmp == u"that-source string", result
        assert result.trans_cmp == u"that-translation string", result.trans_cmp

    def test_source(self):
        context = dict(found=self.record,
                       replacefrom=u"source:regex:s\\wurce",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.source == u"The xxx string", result
        assert result.source_cmp == u"the xxx string", result.source_cmp

    def test_source_bold(self):
        self.record.source = u"<b>I love source</b>"
        self.record.source_cmp = settings.normalize(self.record.source)
        context = dict(found=self.record,
                       replacefrom=u"source:regex:so\\wrce",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.source == u"<b>I love xxx</b>", result
        assert result.source_cmp == u"i love xxx", result

    def test_source_not_changed(self):
        context = dict(found=self.record,
                       replacefrom=u"source:regex:source",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert self.record.source == u"The source string", self.record
        assert self.record.source_cmp == u"the source string", self.record

    def test_source_japanese(self):
        search.normalize = settings.make_normalizer(dict(normalize_width=True,
                                                           normalize_case=True,
                                                           normalize_hira=True))
        self.record.source = u"本日は晴天なり"
        context = dict(found=self.record,
                       replacefrom=u"source:regex:晴天なり",
                       replaceto=u"昨夜")
        result = search.do_replacement(context)
        assert result.source == u"本日は昨夜", result
        assert result.source_cmp.endswith(u"昨夜"), result.source_cmp.encode("utf-8")

    def test_trans(self):
        context = dict(found=self.record,
                       replacefrom=u"trans:regex:(translation)\\s(string)",
                       replaceto=u"\\2 \\1")
        result = search.do_replacement(context)
        assert result.trans == u"The string translation", result
        assert result.trans_cmp == u"the string translation", result

    def test_context(self):
        context = dict(found=self.record,
                       replacefrom=u"context:regex:context",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.context == u"This is the xxx", result
        assert self.record.context == u"This is the context", self.record.context

    def test_created_by(self):
        context = dict(found=self.record,
                       replacefrom=u"created-by:regex:G[io]nstrom",
                       replaceto=u"xxx")
        result = search.do_replacement(context)
        assert result.created_by == u"Ryan xxx", result.created_by

    def test_modified_by(self):
        context = dict(found=self.record,
                       replacefrom=u"modified-by:regex:(\\w+)\\s(\\w+)",
                       replaceto=u"\\2 \\1")
        result = search.do_replacement(context)
        assert result.modified_by == u"Ginstrom Ryan", result.modified_by


class SearchTester(unittest.TestCase):
    def setUp(self):
        model.Data.memories = {}
        model.Data.users = {}
        model.Data.log = []

        self.repo = self.repotype()

        self.renderer = fake_cherrypy.FakeRenderer()
        repository.render = self.renderer.render

        mem = model.Memory(u"SearchTester", u"m")
        mem.id = 1
        model.Data.memories[1] = model.TranslationMemory(model.mem2d(mem))

    def add_record(self, source, trans, **kwds):
        rec = model.MemoryRecord(source, trans)
        records = model.Data.memories.values()[0].mem["records"]
        key = (rec.source, rec.trans)
        records[key] = rec
        records[key].update(kwds)
        return records[key]

class TestSearchGlossaries(SearchTester):
    repotype = repository.Glossaries

    def test_dirname(self):
        self.repo.search("1", "1", "spam", ["egg"])

        dirname = self.renderer.context["dirname"]
        assert dirname == "glossaries", self.renderer.context

class TestSearchTags(SearchTester):
    repotype = repository.Memories

    # source
    def test_source_yes(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.search("1", "1", "source:spam")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_source_yes_3_words(self):
        record = self.add_record(u"spam and eggs", u"egg")
        self.repo.search("1", "1", "source:spam and eggs")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_source_no(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.search("1", "1", "source:egg")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_source_japanese(self):
        record = self.add_record(u"日本語はよし", u"英語")
        self.repo.search("1", "1", "source:日本語はよし")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)


    # trans
    def test_trans_yes(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.search("1", "1", "trans:egg")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_trans_no(self):
        record = self.add_record(u"spam", u"egg")
        self.repo.search("1", "1", "trans:spam")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_trans_japanese(self):
        record = self.add_record(u"日本語はよし", u"はよし")
        self.repo.search("1", "1", "trans:はよし")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    # context
    def test_context_yes(self):
        record = self.add_record(u"spam", u"egg", context=u"I heart foo baby!")
        self.repo.search("1", "1", "context:foo")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.context == record.context, (actual, record)

    def test_context_no(self):
        record = self.add_record(u"spam", u"egg", context=u"I heart bar baby!")
        self.repo.search("1", "1", "context:spam")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_context_japanese(self):
        record = self.add_record(u"日本語はよし", u"foo", context=u"はよし")
        self.repo.search("1", "1", "context:はよし")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    # created-by
    def test_created_by_yes(self):
        record = self.add_record(u"spam", u"egg", created_by=u"I heart foo baby!")
        self.repo.search("1", "1", "created-by:foo")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.created_by == record.created_by, (actual, record)

    def test_created_by_no(self):
        record = self.add_record(u"spam", u"egg", created_by=u"I heart bar baby!")
        self.repo.search("1", "1", "created-by:spam")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.created-by

    # created-before
    def test_created_before_yes(self):
        record1 = self.add_record(u"spam", u"egg", date_created=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", date_created=datetime.datetime(2009, 1, 1))
        self.repo.search("1", "1", "created-before:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.date_created == record1.date_created, (actual, record1)

    def test_created_before_yes_slashes(self):
        record1 = self.add_record(u"spam", u"egg", date_created=datetime.datetime(2007, 1, 1))
        self.repo.search("1", "1", "created-before:2008/10/1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.date_created == record1.date_created, (actual, record1)

    def test_created_before_no(self):
        self.add_record(u"foo", u"bar", date_created=datetime.datetime(2009, 1, 1))
        self.repo.search("1", "1", "created-before:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # created-after
    def test_created_after_yes(self):
        record1 = self.add_record(u"spam", u"egg", date_created=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", date_created=datetime.datetime(2009, 1, 1))
        self.repo.search("1", "1", "created-after:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record2.source, (actual, record2)
        assert actual.trans == record2.trans, (actual, record2)
        assert actual.date_created == record2.date_created, (actual, record2)

    def test_created_after_no(self):
        self.add_record(u"foo", u"bar", date_created=datetime.datetime(2007, 1, 1))
        self.repo.search("1", "1", "created-after:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # modified-by
    def test_modified_by_yes(self):
        record = self.add_record(u"spam", u"egg", modified_by=u"I heart foo baby!")
        self.repo.search("1", "1", "modified-by:foo")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.modified_by == record.modified_by, (actual, record)

    def test_modified_by_no(self):
        record = self.add_record(u"spam", u"egg", modified_by=u"I heart bar baby!")
        self.repo.search("1", "1", "modified-by:spam")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.modified-by

    # modified-before
    def test_modified_before_yes(self):
        record1 = self.add_record(u"spam", u"egg", last_modified=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2009, 1, 1))
        self.repo.search("1", "1", "modified-before:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.last_modified == record1.last_modified, (actual, record1)

    def test_modified_before_yes_slashes(self):
        record1 = self.add_record(u"spam", u"egg", last_modified=datetime.datetime(2007, 1, 1))
        self.repo.search("1", "1", "modified-before:2008/10/1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record1.source, (actual, record1)
        assert actual.trans == record1.trans, (actual, record1)
        assert actual.last_modified == record1.last_modified, (actual, record1)

    def test_modified_before_no(self):
        self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2009, 1, 1))
        self.repo.search("1", "1", "modified-before:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # modified-after
    def test_modified_after_yes(self):
        record1 = self.add_record(u"spam", u"egg", last_modified=datetime.datetime(2007, 1, 1))
        record2 = self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2009, 1, 1))
        self.repo.search("1", "1", "modified-after:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record2.source, (actual, record2)
        assert actual.trans == record2.trans, (actual, record2)
        assert actual.last_modified == record2.last_modified, (actual, record2)

    def test_modified_after_no(self):
        self.add_record(u"foo", u"bar", last_modified=datetime.datetime(2007, 1, 1))
        self.repo.search("1", "1", "modified-after:2008-10-1")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability
    def test_reliability_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.search("1", "1", "reliability:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_no(self):
        record = self.add_record(u"spam", u"egg", reliability=1)
        self.repo.search("1", "1", "reliability:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-gt
    def test_reliability_gt_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=5)
        self.repo.search("1", "1", "reliability-gt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_gt_no(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.search("1", "1", "reliability-gt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-gte
    def test_reliability_gte_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=5)
        self.repo.search("1", "1", "reliability-gte:5")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_gte_no(self):
        record = self.add_record(u"spam", u"egg", reliability=3)
        self.repo.search("1", "1", "reliability-gte:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-lt
    def test_reliability_lt_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=3)
        self.repo.search("1", "1", "reliability-lt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_lt_no(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.search("1", "1", "reliability-lt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # reliability-lte
    def test_reliability_lte_yes(self):
        record = self.add_record(u"spam", u"egg", reliability=4)
        self.repo.search("1", "1", "reliability-lte:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.reliability == record.reliability, (actual, record)

    def test_reliability_lte_no(self):
        record = self.add_record(u"spam", u"egg", reliability=5)
        self.repo.search("1", "1", "reliability-lte:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # validated
    def test_validated_true_yes(self):
        record = self.add_record(u"spam", u"egg", validated=True)
        self.repo.search("1", "1", "validated:true")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.validated == record.validated, (actual, record)

    def test_validated_true_no(self):
        self.add_record(u"spam", u"egg", validated=False)
        self.repo.search("1", "1", "validated:true")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_validated_false_yes(self):
        record = self.add_record(u"spam", u"egg", validated=False)
        self.repo.search("1", "1", "validated:false")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.validated == record.validated, (actual, record)

    def test_validated_false_no(self):
        record = self.add_record(u"spam", u"egg", validated=True)
        self.repo.search("1", "1", "validated:false")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context["records"]

    # refcount
    def test_refcount_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.search("1", "1", "refcount:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=1)
        self.repo.search("1", "1", "refcount:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-gt
    def test_refcount_gt_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=5)
        self.repo.search("1", "1", "refcount-gt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_gt_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.search("1", "1", "refcount-gt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-gte
    def test_refcount_gte_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=5)
        self.repo.search("1", "1", "refcount-gte:5")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_gte_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=3)
        self.repo.search("1", "1", "refcount-gte:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-lt
    def test_refcount_lt_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=3)
        self.repo.search("1", "1", "refcount-lt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_lt_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.search("1", "1", "refcount-lt:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    # refcount-lte
    def test_refcount_lte_yes(self):
        record = self.add_record(u"spam", u"egg", ref_count=4)
        self.repo.search("1", "1", "refcount-lte:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)
        assert actual.ref_count == record.ref_count, (actual, record)

    def test_refcount_lte_no(self):
        record = self.add_record(u"spam", u"egg", ref_count=5)
        self.repo.search("1", "1", "refcount-lte:4")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_source_and_trans(self):
        record = self.add_record(u"spam", u"egg")
        fake1 = self.add_record(u"foo", u"egg")
        fake2 = self.add_record(u"spam", u"bar")
        self.repo.search("1", "1", "source:spam", queryfilters=["trans:egg"])

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]

        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)



class TestSearchMemories(SearchTester):
    repotype = repository.Memories

    def test_no_matches(self):

        self.repo.search("1", "1", "spam", ["egg"])

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

    def test_dirname(self):

        self.repo.search("1", "1", "spam", ["egg"])

        dirname = self.renderer.context["dirname"]
        assert dirname == "memories", self.renderer.context

    def test_string_qf_to_list(self):
        self.repo.search("1", "1", "spam", "egg")

        queryfilters = self.renderer.context["queryfilters"]
        expected = [{'removelink': u'?queryfilters=spam', 'term': u'egg'}, {'removelink': u'?queryfilters=egg', 'term': u'spam'}]
        assert queryfilters == expected, queryfilters
        assert isinstance(queryfilters[0], dict), queryfilters

    def test_1_match_string_qf(self):
        record = self.add_record(u"spam", u"egg")

        self.repo.search("1", "1", "spam", ["egg"])

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_one_match_list_queryfilter(self):
        record = self.add_record(u"spam foo", u"egg")

        self.repo.search("1", "1", "spam", "foo egg".split())

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_both(self):
        record = self.add_record(u"spam", u"egg")

        self.repo.search("1", "1", "spam", ["egg"])

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_no_queryfilter(self):
        record = self.add_record(u"spam", u"egg")

        self.repo.search("1", "1", "spam")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_japanese_no_queryfilter(self):
        record = self.add_record(u"日本語", u"英語")

        self.repo.search("1", "1", "日本語")

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_japanese(self):
        record = self.add_record(u"日本語", u"英語")

        self.repo.search("1", "1", "日本語", ["英語"])

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_match_japanese_with_hiragana(self):
        record = self.add_record(u"日本語はよし", u"英語")

        self.repo.search("1", "1", "日本語はよし", ["英語"])

        assert self.renderer.page == "search/search.html", self.renderer.page
        records = self.renderer.context["records"]
        assert len(records) == 1, records
        actual = records[0]
        assert actual.source == record.source, (actual, record)
        assert actual.trans == record.trans, (actual, record)

    def test_empty_string(self):
        self.add_record(u"spam", u"egg")
        self.repo.search("1", "1", "")

        assert self.renderer.page == "search/search.html", self.renderer.page
        assert self.renderer.context["records"] == [], self.renderer.context

class TestSmoothQueryfilters(unittest.TestCase):
    def test_string(self):
        queryfilters = "English"
        qf = search.smooth_queryfilters(queryfilters)
        assert qf == [u"English"], qf

    def test_list(self):
        queryfilters = "English 日本語".split()
        qf = search.smooth_queryfilters(queryfilters)
        assert qf == [u"English", u"日本語"], qf

class TestRefineQuery(unittest.TestCase):
    def setUp(self):
        self.records = [model.MemoryRecord(source=u"spam",
                        trans=u"foo",
                        source_cmp=u"spam",
                        trans_cmp=u"foo",
                        context=u"xxx",
                        reliability=0,
                        validated=True,
                        created_by="Ryan Ginstrom",
                        modified_by="Santa Klaus",
                        ref_count=0),

                        model.MemoryRecord(source=u"egg",
                        trans=u"bar",
                        source_cmp=u"egg",
                        trans_cmp=u"bar",
                        context=u"yyy",
                        reliability=5,
                        validated=False,
                        created_by="Ted Bundy",
                        modified_by="Easter Bunny",
                        ref_count=5)]

    def test_source_spam(self):
        records = list(repository.refine_query(self.records, "source:spam"))
        assert len(records) == 1, records
        assert records[0].source == u"spam", records

    def test_source_asterisk(self):
        records = list(repository.refine_query(self.records, "source:*"))
        assert len(records) == 2, records
        assert records[0].source == u"spam", records
        assert records[1].source == u"egg", records

    def test_reliability_5(self):
        records = list(repository.refine_query(self.records, "reliability:5"))
        assert len(records) == 1, records
        assert records[0].source == u"egg", records

    def test_trans_spam(self):
        records = list(repository.refine_query(self.records, "trans:foo"))
        assert len(records) == 1, records
        assert records[0].trans == u"foo", records

    def test_trans_asterisk(self):
        records = list(repository.refine_query(self.records, "trans:*"))
        assert len(records) == 2, records
        assert records[0].trans == u"foo", records
        assert records[1].trans == u"bar", records

    def test_context_spam(self):
        records = list(repository.refine_query(self.records, "context:xxx"))
        assert len(records) == 1, records
        assert records[0].context == u"xxx", records

    def test_context_asterisk(self):
        records = list(repository.refine_query(self.records, "context:*"))
        assert len(records) == 2, records
        assert records[0].context == u"xxx", records
        assert records[1].context == u"yyy", records

    def test_created_by_spam(self):
        records = list(repository.refine_query(self.records, "created-by:Ryan"))
        assert len(records) == 1, records
        assert records[0].created_by == u"Ryan Ginstrom", records

    def test_created_by_asterisk(self):
        records = list(repository.refine_query(self.records, "created-by:*"))
        assert len(records) == 2, records
        assert records[0].created_by == u"Ryan Ginstrom", records
        assert records[1].created_by == u"Ted Bundy", records

    def test_modified_by_spam(self):
        records = list(repository.refine_query(self.records, "modified-by:Santa"))
        assert len(records) == 1, records
        assert records[0].modified_by == u"Santa Klaus", records

    def test_modified_by_asterisk(self):
        records = list(repository.refine_query(self.records, "modified-by:*"))
        assert len(records) == 2, records
        assert records[0].modified_by == u"Santa Klaus", records
        assert records[1].modified_by == u"Easter Bunny", records


class TestRefineQueryRegex(unittest.TestCase):
    def setUp(self):
        self.records = [model.MemoryRecord(source=u"spam is cool",
                        trans=u"<b>Food <i>gets</i> eaten</b>",
                        source_cmp=u"spam is cool",
                        trans_cmp=u"food gets eaten",
                        context=u"xxx",
                        reliability=0,
                        validated=True,
                        created_by="Ryan Ginstrom",
                        modified_by="Santa Klaus",
                        ref_count=0),

                        model.MemoryRecord(source=u"egg follows bacon",
                        trans=u"bars precede spam",
                        source_cmp=u"egg follows bacon",
                        trans_cmp=u"bars precede cars",
                        context=u"yyy",
                        reliability=5,
                        validated=False,
                        created_by="Ted Bundy",
                        modified_by="Easter Bunny",
                        ref_count=5)]

    def test_general_spam(self):
        records = list(repository.refine_query(self.records, "regex:sp\\wm"))
        assert records == self.records, (records, self.records)

    def test_source_spam(self):
        records = list(repository.refine_query(self.records, "source:regex:sp\\wm"))
        assert len(records) == 1, records
        assert records[0].source == u"spam is cool", records

    def test_trans_food(self):
        records = list(repository.refine_query(self.records, "trans:regex:Foo\\w gets"))
        assert len(records) == 1, records
        assert records[0].trans == u"<b>Food <i>gets</i> eaten</b>", records

    def test_context_spam(self):
        records = list(repository.refine_query(self.records, "context:regex:xxx"))
        assert len(records) == 1, records
        assert records[0].context == u"xxx", records


    def test_created_by_spam(self):
        records = list(repository.refine_query(self.records, "created-by:regex:Ryan"))
        assert len(records) == 1, records
        assert records[0].created_by == u"Ryan Ginstrom", records


    def test_modified_by_spam(self):
        records = list(repository.refine_query(self.records, "modified-by:regex:Santa"))
        assert len(records) == 1, records
        assert records[0].modified_by == u"Santa Klaus", records



class TestRefineReplaceFrom(unittest.TestCase):
    def setUp(self):
        self.records = [model.MemoryRecord(source=source,
                        trans=trans,
                        source_cmp=source,
                        trans_cmp=trans)
                   for source, trans in zip(u"spam egg".split(), u"foo bar".split())]

    def test_xxx(self):
        self.records = [model.MemoryRecord(source=source,
                        trans=trans,
                        source_cmp=source,
                        trans_cmp=trans)
                   for source, trans in zip(u"xxx xxx".split(), u"yyy zzz".split())]

        records = list(repository.refine_replacefrom(self.records, "xxx"))
        assert len(records) == 2, records

    def test_created(self):
        records = list(repository.refine_replacefrom(self.records, "created:foo"))
        assert records == self.records, (records, self.records)

    def test_reliability(self):
        records = list(repository.refine_replacefrom(self.records, "reliability:foo"))
        assert records == self.records, (records, self.records)

    def test_validated(self):
        records = list(repository.refine_replacefrom(self.records, "validated:foo"))
        assert records == self.records, (records, self.records)

    def test_refcount(self):
        records = list(repository.refine_replacefrom(self.records, "refcount:foo"))
        assert records == self.records, (records, self.records)

    def test_modified(self):
        records = list(repository.refine_replacefrom(self.records, "modified:foo"))
        assert records == self.records, (records, self.records)

    def test_source(self):
        records = list(repository.refine_replacefrom(self.records, "source:spam"))
        len(records) == 1, records
        record = records[0]
        assert record.source == u"spam", record

    def test_source_asterisk(self):
        records = list(repository.refine_replacefrom(self.records, "source:*"))
        assert len(records) == 2, records
        rec1, rec2 = records
        assert rec1.source == u"spam", rec1
        assert rec2.source == u"egg", rec2

    def test_trans(self):
        records = list(repository.refine_replacefrom(self.records, "trans:bar"))
        len(records) == 1, records
        record = records[0]
        assert record.trans == u"bar", record

    def test_trans(self):
        records = list(repository.refine_replacefrom(self.records, "trans:*"))
        assert len(records) == 2, records
        rec1, rec2 = records
        assert rec1.source == u"spam", rec1
        assert rec2.source == u"egg", rec2


class TestMakeQueryLink(unittest.TestCase):

    def test_empty(self):
        link = search.make_querylink([])
        assert link == "", link

    def test_one(self):
        link = search.make_querylink(["foo"])
        assert link == "?queryfilters=foo", link

    def test_two(self):
        link = search.make_querylink("foo bar".split())
        assert link == "?queryfilters=foo&amp;queryfilters=bar", link

    def test_one_amp(self):
        link = search.make_querylink("&".split())
        assert link == "?queryfilters=%26", link

    def test_two_amp(self):
        link = search.make_querylink("& foo".split())
        assert link == "?queryfilters=%26&amp;queryfilters=foo", link

    def test_Japaenese(self):
        link = search.make_querylink(["日本語"])
        assert link == u"?queryfilters=%E6%97%A5%E6%9C%AC%E8%AA%9E", link
