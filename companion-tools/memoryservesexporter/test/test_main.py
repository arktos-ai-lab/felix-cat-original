"""
Unit tests for main module
"""
__author__ = 'Ryan'

import unittest
from MemoryServesExporter import main
import mock

class TestMainModule(unittest.TestCase):
    def test_module_loads(self):
        pass

class TestUnderscore(unittest.TestCase):
    def test_self_returned(self):
        msg = "foo"
        actual = main._(msg)
        assert isinstance(actual, unicode)
        assert actual == u"foo", actual

class TestMain(unittest.TestCase):
    def test_main(self):
        main.main(mock.Mock())

class TestApp(unittest.TestCase):
    def test_initialize_app(self):
        app = mock.Mock()
        frame_class = mock.Mock
        wx_provider = mock.Mock()
        sc_provider = mock.Mock()
        main.initialize_app(app, frame_class(), wx_provider, sc_provider)

class FakeProviders(object):
    def __init__(self):
        self.wx = mock.Mock()
        self.sc = mock.Mock()

class TestInitFrame(unittest.TestCase):
    def test_initialize_frame(self):
        controller = mock.Mock()
        pane = mock.Mock()
        providers = FakeProviders()
        main.initialize_frame(controller, pane, providers.wx, providers.sc)

    def test_create_connection_string_row(self):
        controller = mock.Mock()
        pane = mock.Mock()
        wx_provider = mock.Mock()
        main.create_connection_string_row(controller, pane, wx_provider)
        assert True

    def test_create_save_row(self):
        controller = mock.Mock()
        pane = mock.Mock()
        wx_provider = mock.Mock()
        main.create_save_row(controller, pane, wx_provider)
        assert True

    def test_create_export_button_row(self):
        controller = mock.Mock()
        pane = mock.Mock()
        wx_provider = mock.Mock()
        sc_provider = mock.Mock()
        main.create_export_button_row(controller, pane, wx_provider, sc_provider)
        assert True


class TestController(unittest.TestCase):
    def setUp(self):
        frame = mock.Mock()
        providers = FakeProviders()
        self.controller = main.MemoryExporterFrameController(frame, providers)

    def test_create(self):
        assert self.controller.test_btn
        assert self.controller.browse_btn
        assert self.controller.cancel_btn
        assert self.controller.export_btn

    def test_on_cancel(self):
        """
        Ensure that correct stuff happens when Cancel button is pressed.
        """
        self.controller.frame = frame = mock.Mock()
        self.controller.OnCancel(None)

        assert len(frame.mock_calls) == 1, frame.mock_calls
        frame.Close.assert_called_once_with()

    def test_on_test_connection_true(self):
        with mock.patch.object(main, 'is_valid_connection', return_value=True):
            with mock.patch.multiple(main, warning_msg=mock.DEFAULT, info_msg=mock.DEFAULT):
                self.controller.OnTestConnection(None)

                assert main.warning_msg.called == False
                main.info_msg.assert_called_once_with(self.controller.frame,
                                                  main._("Test Connection String"),
                                                  main._("The connection string is valid."),
                                                  self.controller.providers.wx)

    def test_on_test_connection_false(self):
        with mock.patch.object(main, 'is_valid_connection', return_value=False):
            with mock.patch.multiple(main, warning_msg=mock.DEFAULT, info_msg=mock.DEFAULT):
                self.controller.OnTestConnection(None)

                assert main.info_msg.called == False
                main.warning_msg.assert_called_once_with(self.controller.frame,
                                                  main._("Test Connection String"),
                                                  main._("The connection string is not valid."),
                                                  self.controller.providers.wx)

    def test_get_wildcard(self):
        expected = main._("Felix Memory Files (*.ftm)|*.ftm|Felix Glossary Files (*.fgloss)|*.fgloss|XML Files (*.xml)|*.xml|All Files (*.*)|*.*")
        actual = self.controller.get_wildcard()
        assert actual == expected, actual

    def test_on_browse_cancel(self):
        box = self.controller.filename_textbox
        box.Value = ""
        wx = self.controller.providers.wx
        wx.ID_OK = "user clicked open"
        wx.SAVE = 2
        wx.CHANGE_DIR = 4
        dlg = wx.FileDialog()
        dlg.ShowModal.return_value = "user clicked cancel"
        dlg.GetPaths.return_value = ["there is now a filename in the textbox"]

        self.controller.OnBrowse(None)
        assert box.Value == "", box.Value

    def test_on_browse_ok(self):
        box = self.controller.filename_textbox
        box.Value = ""
        wx = self.controller.providers.wx
        wx.ID_OK = "user clicked open"
        wx.SAVE = 2
        wx.CHANGE_DIR = 4
        dlg = wx.FileDialog()
        dlg.ShowModal.return_value = "user clicked open"
        dlg.GetPaths.return_value = ["there is now a filename in the textbox"]
        self.controller.OnBrowse(None)
        assert box.Value == "there is now a filename in the textbox", box.Value

    def test_on_export_bad_file(self):
        default = mock.DEFAULT
        with mock.patch('__builtin__.open', side_effect=IOError("Cannot open file.")) as mock_open:
            with mock.patch.multiple(main, warning_msg=default):
                self.controller.OnExport(None)

                val = self.controller.filename_textbox.Value
                expected_msg = main._("Failed to open file %s:\nCannot open file.") % val
                main.warning_msg.assert_called_once_with(self.controller.frame,
                                                         main._("Export Failed"),
                                                         expected_msg,
                                                         self.controller.providers.wx)

    def test_on_export_bad_connection(self):
        default = mock.DEFAULT
        with mock.patch('__builtin__.open') as mock_open:
            with mock.patch.multiple(main, warning_msg=default, is_valid_connection=default):
                main.is_valid_connection.return_value = False
                self.controller.OnExport(None)

                val = self.controller.filename_textbox.Value
                mock_open.assert_called_once_with(val, "w")

                conn = self.controller.connect_textbox.Value
                expected_msg = main._("Invalid connection string: %s") % conn
                main.warning_msg.assert_called_once_with(self.controller.frame,
                                                         main._("Export Failed"),
                                                         expected_msg,
                                                         self.controller.providers.wx)

    def test_on_export_success(self):
        default = mock.DEFAULT
        with mock.patch('__builtin__.open') as mock_open:
            with mock.patch.multiple(main, warning_msg=default,
                                     is_valid_connection=default, exportdata=default, info_msg=default):
                main.is_valid_connection.return_value = True
                mock_open.return_value = "file handle"

                prov = self.controller.providers.wx
                prov.PD_CAN_ABORT = 2
                prov.PD_APP_MODAL = 4
                prov.PD_ELAPSED_TIME = 8
                prov.PD_REMAINING_TIME = 16
                prov.PD_AUTO_HIDE = 32

                export_func = main.exportdata.export
                export_func.side_effect = lambda a, b, c : c.initialize(10)

                self.controller.OnExport(None)

                val = self.controller.filename_textbox.Value
                mock_open.assert_called_once_with(val, "w")

                conn = self.controller.connect_textbox.Value

                export_func.assert_called_once_with(conn, "file handle", self.controller.callback)

                self.controller.providers.wx.ProgressDialog.assert_called_once()
                dlg = self.controller.providers.wx.ProgressDialog()

                dlg.Destroy.assert_called()

                assert main.info_msg.call_count == 1, main.info_msg.call_count

    def test_on_export_fails(self):
        default = mock.DEFAULT
        with mock.patch('__builtin__.open') as mock_open:
            with mock.patch.multiple(main, warning_msg=default,
                                     is_valid_connection=default, exportdata=default, info_msg=default):
                main.is_valid_connection.return_value = True
                mock_open.return_value = "file handle"

                prov = self.controller.providers.wx
                prov.PD_CAN_ABORT = 2
                prov.PD_APP_MODAL = 4
                prov.PD_ELAPSED_TIME = 8
                prov.PD_REMAINING_TIME = 16
                prov.PD_AUTO_HIDE = 32

                export_func = main.exportdata.export
                export_func.side_effect = Exception("boom")

                self.controller.OnExport(None)

                val = self.controller.filename_textbox.Value
                mock_open.assert_called_once_with(val, "w")

                conn = self.controller.connect_textbox.Value

                export_func.assert_called_once_with(conn, "file handle", self.controller.callback)

                expected_msg = main._("Failed to export TM\nboom")
                main.warning_msg.assert_called_once_with(self.controller.frame,
                                                         main._("Export Failed"),
                                                         expected_msg,
                                                         self.controller.providers.wx)


class TestMemoryExporterAbortException(unittest.TestCase):
    def test_create(self):
        try:
            raise main.MemoryExporterAbortException("An abort.")
            assert False, "Should have thrown here."
        except main.MemoryExporterAbortException, e:
            assert str(e) == "An abort.", e

class TestProgressCallback(unittest.TestCase):
    def setUp(self):
        self.callback = main.ProgressCallback(mock.Mock(), mock.Mock())

        prov = self.callback.provider
        prov.PD_CAN_ABORT = 2
        prov.PD_APP_MODAL = 4
        prov.PD_ELAPSED_TIME = 8
        prov.PD_REMAINING_TIME = 16
        prov.PD_AUTO_HIDE = 16

    def test_init(self):
        callback = self.callback
        assert callback.parent
        assert callback.provider
        assert not callback.dlg, callback.dlg
        assert callback.max_value == 0, callback.max_value

    def test_initialize(self):
        callback = self.callback

        callback.initialize(10)

        assert callback.max_value == 10, callback.max_value
        assert callback.provider.ProgressDialog.called_once_with(main._("Exporting Memory Serves Repo"),
                                                   main._("Initializing data..."),
                                                   10,
                                                   callback.parent,
                                                   2 | 4 | 8 | 16)
    def test_update_keep_going(self):
        callback = self.callback
        callback.initialize(10)
        assert callback.current == 0, callback.current
        callback.dlg.Update.return_value = (True, True)
        callback.update()
        callback.dlg.Update.assert_called_once_with(1, u"Exported 1 of 10 records")
        assert callback.current == 1, callback.current

    def test_update_keep_going_over_max(self):
        callback = self.callback
        callback.initialize(10)
        callback.current = 15
        callback.dlg.Update.return_value = (True, True)
        callback.update()
        callback.dlg.Update.assert_called_once_with(10, "Exported 10 of 10 records")

    def test_update_abort(self):
        callback = self.callback
        callback.initialize(10)
        callback.dlg.Update.return_value = (False, True)
        try:
            callback.update()
            assert False, "Should have aborted"
        except main.MemoryExporterAbortException, e:
            assert unicode(e) == main._("User aborted export")

    def test_with_statement(self):
        provider = self.callback.provider

        with main.ProgressCallback(mock.Mock(), provider) as callback:
            callback.initialize(10)

        callback.dlg.Destroy.assert_called_once_with()

class TestIsValidConnection(unittest.TestCase):
    def test_bad_url(self):
        with mock.patch.multiple(main, exportdata=mock.DEFAULT):
            main.exportdata.DataSource().get_data.side_effect = Exception("Bad URL")
            assert not main.is_valid_connection("foo")
    def test_not_dict(self):
        with mock.patch.multiple(main, exportdata=mock.DEFAULT):
            main.exportdata.DataSource().get_data.return_value = "foo"
            assert not main.is_valid_connection("foo")
    def test_info_not_in_dict(self):
        with mock.patch.multiple(main, exportdata=mock.DEFAULT):
            main.exportdata.DataSource().get_data.return_value = dict(foo=3)
            assert not main.is_valid_connection("foo")
    def test_info_not_url(self):
        with mock.patch.multiple(main, exportdata=mock.DEFAULT):
            main.exportdata.DataSource().get_data.return_value = dict(info="foo")
            assert not main.is_valid_connection("foo")
    def test_valid(self):
        with mock.patch.multiple(main, exportdata=mock.DEFAULT):
            main.exportdata.DataSource().get_data.return_value = dict(info="http://example.com/")
            assert main.is_valid_connection("foo")

class TestMessageBoxes(unittest.TestCase):
    def test_msg_box(self):
        wx_provider = mock.Mock()
        wx_provider.OK = 3
        main.msg_box("parent", "message", "title", 8, wx_provider)
        assert len(wx_provider.mock_calls) == 3, wx_provider.mock_calls
        wx_provider.MessageDialog.assert_called_once_with("parent", "message", "title", 3 | 8)
        wx_provider.MessageDialog().ShowModal.assert_called_once_with()
        wx_provider.MessageDialog().Destroy.assert_called_once_with()

    def test_warning_msg(self):
        wx_provider = mock.Mock()
        with mock.patch.object(main, 'msg_box') as msg_func:
            wx_provider.OK = 3
            wx_provider.ICON_EXCLAMATION = 8
            main.warning_msg("parent", "message", "title", wx_provider)

        msg_func.assert_called_once_with("parent", "title", "message", 8, wx_provider)

    def test_info_msg(self):
        wx_provider = mock.Mock()
        with mock.patch.object(main, 'msg_box') as msg_func:
            wx_provider.OK = 3
            wx_provider.ICON_INFORMATION = 22
            main.info_msg("parent", "message", "title", wx_provider)

        msg_func.assert_called_once_with("parent", "title", "message", 22, wx_provider)
