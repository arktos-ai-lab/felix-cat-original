#encoding: UTF-8

from MemoryServesExporter import exportdata
import unittest
import cStringIO
import cPickle
import datetime
import mock

class TestMassageRecData(unittest.TestCase):
    def test_reliability_1(self):
        data = dict(reliability=1)
        actual = exportdata.massage_rec_data(data)["reliability"]
        expected = u"1"
        assert actual == expected, actual

class TestGetUrlContent(unittest.TestCase):
    def test_calls(self):
        url_module=mock.Mock()
        url = "http://example.com/"
        exportdata.get_url_content(url, url_module)
        assert len(url_module.mock_calls) == 2, url_module.mock_calls
        first, second = url_module.mock_calls
        assert str(first) == "call.urlopen('http://example.com/')", first
        assert str(second) == "call.urlopen().read()", second

class TestDataSource(unittest.TestCase):
    def test_parse_url(self):
        conn_url = "http://felix-cat.com/1"
        source = exportdata.DataSource(conn_url)
        url = source.parse_url()
        assert url.scheme == "http:", url.scheme
        assert url.netloc == "felix-cat.com", url.netloc
        assert url.mem_num == "1", url.mem_num

class FakeDataSource(object):
    def __init__(self, scheme="", netloc="", mem_num="", data=None):
        self.scheme = scheme
        self.netloc = netloc
        self.mem_num = mem_num
        self.data = data or {}

    def get_data(self):
        return self.data

    def parse_url(self):
        return exportdata.ParsedUrl(self.scheme, self.netloc, self.mem_num)

class TestWriteMemory(unittest.TestCase):

    def setUp(self):
        self.url_getter = exportdata.get_url_content
        self.content = {}
        exportdata.get_url_content = lambda x : self.content[x]

    def tearDown(self):
        exportdata.get_url_content =  self.url_getter

    def set_content(self, key, data):
        self.content[key] = cPickle.dumps(data)

    def test_write_memory(self):
        self.set_content("info", dict(created_on=datetime.datetime(2010, 1, 2, 3, 4, 5), size=5))
        self.set_content("scheme//netloc/memories/browse/1/1", "")

        source = FakeDataSource("scheme", "netloc", "1")
        source.data = dict(info="info",
                           rec_by_id="foo"
                           )

        out = cStringIO.StringIO()
        exportdata.write_memory(source, out, mock.Mock())
        actual = out.getvalue()
        expected = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Created by MemoryServesExporter v 1.0 -->
<memory>
<head>
  <creator></creator>
  <created_on>2010/01/02 03:04:05</created_on>
  <creation_tool>MemoryServesExporter</creation_tool>
  <creation_tool_version>1.0</creation_tool_version>
  <num_records>5</num_records>
  <locked>false</locked>
  <is_memory>false</is_memory>
</head>
<records>
</records>
</memory>
"""
        assert actual == expected, actual
    
class TestBool2String(unittest.TestCase):
    def test_True(self):
        assert exportdata.bool2str(True) == "true",  exportdata.bool2str(True)
    def test_False(self):
        assert exportdata.bool2str(False) == "false",  exportdata.bool2str(True)

class TestDownloadPageSubroutines(unittest.TestCase):
    def test_build_download_url(self):
        source = exportdata.DataSource("http://192.168.56.1:8765/api/mems/3/")
        parsed = source.parse_url()
        page_num = "1"
        url = exportdata.build_download_url(page_num, parsed)
        assert url == "http://192.168.56.1:8765/memories/browse/3/1", url

    def test_find_record_links(self):
        browse_page = """<tr id="row_b4">
            <td colspan="2">
                <a href="/records/edit/3/198" id="edit_4">Edit</a>
                | <a href="/records/delete/3/198/?next=/memories/browse/3/1">Delete</a>
                | <a href="/records/view/3/198" id="view_4">Details &gt;&gt;</a>
                <div id="item_4" style="display:none;">
		    <table class="props">
			<tr>
			    <th>Source</th>
			    <td id="source_4">ボデー</td>
            <td colspan="2">
                <a href="/records/edit/3/201" id="edit_4">Edit</a>
                | <a href="/records/delete/3/198/?next=/memories/browse/3/1">Delete</a>
                | <a href="/records/view/3/198" id="view_4">Details &gt;&gt;</a>
                <div id="item_4" style="display:none;">
"""
        record_links = exportdata.find_record_links(browse_page)
        assert record_links == ['href="/records/edit/3/198"', 'href="/records/edit/3/201"'], record_links

    def test_find_page_links(self):
        browse_page = """<p class="paginator">

        <span class="this-page" title="Current page">1</span>
        <a href="2" title="Go to page 2">2</a>
        <a href="3" title="Go to page 3">3</a>
</p>
"""
        record_links = exportdata.find_page_links(browse_page)
        assert record_links == ['<a href="2" title="Go to page 2">2</a>', '<a href="3" title="Go to page 3">3</a>'], record_links