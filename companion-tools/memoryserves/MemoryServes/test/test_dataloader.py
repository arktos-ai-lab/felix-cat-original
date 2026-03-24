"""
Unit tests for dataloader module
"""

import unittest
import datetime

import mock

from .. import dataloader


class TestMassageDates(unittest.TestCase):
    """
    Unit tests for massage_dates function
    """

    def test_created_tuple(self):
        """
        If the date_created is a tuple, it is converted to a datetime.
        """
        record = mock.Mock()
        record.date_created = (2010, 10, 9, 8, 7, 6)
        expected = datetime.datetime(2010, 10, 9, 8, 7, 6)
        actual = dataloader.massage_dates(record).date_created

        assert actual == expected, actual

    def test_modified_tuple(self):
        """
        If the last_modified is a tuple, it is converted to a datetime.
        """
        record = mock.Mock()
        record.last_modified = (2010, 10, 9, 8, 7, 6)
        expected = datetime.datetime(2010, 10, 9, 8, 7, 6)
        actual = dataloader.massage_dates(record).last_modified

        assert actual == expected, actual

class TestMassageMemories(unittest.TestCase):
    """
    Unit tests for `massage_memories` class.
    """
    def test_exception(self):
        """
        The function handles exceptions correctly.
        """
        with mock.patch("MemoryServes.dataloader.massage_records") as mock_mr:
            with mock.patch("MemoryServes.dataloader.logger") as mock_log:
                mock_mr.side_effect = Exception("boom")
                memory = mock.Mock()
                memory.mem = {'records': [], 'name': "foo", "id": 1}
                dataloader.massage_memories({1: memory})
                mock_log.exception.assert_called_once_with(" ... Failed to parse memory")


class TestMassageRecords(unittest.TestCase):
    """
    Unit tests for `massage_records` function
    """

    def test_str_id(self):
        """
        If a record has a non-int id value, it is deleted.
        """

        actual = {"memory_id": "foo", "source": "s", "trans": "t"}
        records = {1: actual}
        expected = {"source": "s", "trans": "t"}
        list(dataloader.massage_records(records))
        assert actual == expected, actual


class TestSave(unittest.TestCase):
    """
    Unit tests for save thread.
    """
    def test_save_and_continue(self):
        """
        The save_and_quit function does a save and then sends a quit message.
        """
        with mock.patch("MemoryServes.dataloader.do_save") as msave:
            with mock.patch("MemoryServes.dataloader.time") as mtime:
                dataloader.save_and_continue()
                msave.assert_called_once_with()
                mtime.time.assert_called_with()

    def test_save_and_quit(self):
        """
        The save_and_quit function does a save and then sends a quit message.
        """
        with mock.patch("MemoryServes.dataloader.do_save") as msave:
            with mock.patch("MemoryServes.dataloader.threading") as mthread:
                dataloader.save_and_quit()
                msave.assert_called_once_with()
                mthread.Timer.assert_called_once_with(1, dataloader.do_quit)

    def test_background_save_should_quit(self):
        with mock.patch("MemoryServes.dataloader.save_and_quit") as msave:
            dataloader.SHOULD_QUIT = True
            dataloader.background_save()
            msave.assert_called_once_with()

