#coding: UTF8
__author__ = 'Ryan'

import unittest
import datetime
from MemoryServesExporter import exportdata
from cStringIO import StringIO

class TestWriteHeadNode(unittest.TestCase):
    def test_English(self):
        data = {'modified_by': u'Ryan',
                'name': u'test-mem',
                'creator': u'ryan',
                'notes': u'',
                'source_language': u'Japanese',
                'normalize_case': True,
                'normalize_hira': False,
                'created_on': datetime.datetime(2012, 4, 7, 21, 47, 1),
                'client': u'Felix',
                'version': '2.0.1',
                'normalize_width': True,
                'modified_on': datetime.datetime(2012, 4, 7, 21, 47, 1),
                'memtype': u'm',
                'target_language': u'English',
                'id': 1,
                'size': 6}

        out = StringIO()
        exportdata.write_head_node(data, out)
        actual = out.getvalue()
        expected = """<head>
  <creator>ryan</creator>
  <created_on>2012/04/07 21:47:01</created_on>
  <creation_tool>MemoryServesExporter</creation_tool>
  <creation_tool_version>1.0</creation_tool_version>
  <num_records>6</num_records>
  <locked>false</locked>
  <is_memory>true</is_memory>
</head>
"""
        assert actual == expected, actual

    def test_Japanese(self):
        data = {'modified_by': u'太郎',
                'name': u'test-mem',
                'creator': u'太郎',
                'notes': u'',
                'source_language': u'Japanese',
                'normalize_case': True,
                'normalize_hira': False,
                'created_on': datetime.datetime(2012, 4, 7, 21, 47, 1),
                'client': u'A社',
                'version': '2.0.1',
                'normalize_width': True,
                'modified_on': datetime.datetime(2012, 4, 7, 21, 47, 1),
                'memtype': u'm',
                'target_language': u'English',
                'id': 1,
                'size': 6}

        out = StringIO()
        exportdata.write_head_node(data, out)
        actual = out.getvalue()
        expected = """<head>
  <creator>太郎</creator>
  <created_on>2012/04/07 21:47:01</created_on>
  <creation_tool>MemoryServesExporter</creation_tool>
  <creation_tool_version>1.0</creation_tool_version>
  <num_records>6</num_records>
  <locked>false</locked>
  <is_memory>true</is_memory>
</head>
"""
        assert actual == expected, actual


class TestMakeHeadData(unittest.TestCase):
    def test_empty_data(self):
        today = datetime.datetime.today()
        start = today.strftime("%Y/%m/%d")
        head_data = exportdata.make_head_data({})
        assert head_data["count"] == '0', head_data
        assert head_data["locked"] == 'false', head_data
        assert head_data["creator"] == u'', head_data
        assert head_data["version"] == exportdata.VERSION, head_data
        assert head_data["creation_tool"] == 'MemoryServesExporter', head_data
        assert head_data["created_on"].startswith(start), head_data["created_on"]
        assert head_data["creation_tool"] == 'MemoryServesExporter', head_data

    def test_actual(self):
        data = {'modified_by': u'Ryan',
                'name': u'test-mem',
                'creator': u'ryan',
                'notes': u'',
                'source_language': u'Japanese',
                'normalize_case': True,
                'normalize_hira': False,
                'created_on': datetime.datetime(2012, 4, 7, 21, 47, 1),
                'client': u'Felix',
                'version': '2.0.1',
                'normalize_width': True,
                'modified_on': datetime.datetime(2012, 4, 7, 21, 47, 1),
                'memtype': u'm',
                'target_language': u'English',
                'id': 1,
                'size': 6}

        head_data = exportdata.make_head_data(data)
        assert head_data["count"] == '6', head_data
        assert head_data["locked"] == 'false', head_data
        assert head_data["creator"] == u'ryan', head_data
        assert head_data["version"] == exportdata.VERSION
        assert head_data["created_on"] == '2012/04/07 21:47:01', head_data

    def test_japanese(self):
        data = {'modified_by': u'日本語',
                'name': u'test-mem',
                'creator': u'太郎',
                }

        head_data = exportdata.make_head_data(data)
        assert head_data["creator"] == u'太郎', head_data
