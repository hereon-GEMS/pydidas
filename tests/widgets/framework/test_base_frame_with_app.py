# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest
from pathlib import Path

from qtpy import QtCore, QtWidgets

from pydidas.core import BaseApp, get_generic_parameter
from pydidas.widgets.framework import BaseFrameWithApp
from pydidas_qtcore import PydidasQApplication


class DummyRunner:
    def exit(self):
        pass


class TestClass(QtCore.QObject):
    signal = QtCore.Signal(float)
    simple_signal = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.reveived_signals = []

    def get_progress(self, obj):
        self.reveived_signals.append(obj)

    def send_progress(self, progress):
        self.signal.emit(progress)


class TestBaseFrameWithApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._qtapp = QtWidgets.QApplication.instance()
        if cls._qtapp is None:
            cls._qtapp = PydidasQApplication([])

    @classmethod
    def tearDownClass(cls):
        cls._qtapp.quit()
        app = QtWidgets.QApplication.instance()
        if app is None:
            app.deleteLater()

    def setUp(self):
        self.tester = TestClass()

    def tearDown(self):
        ...

    def get_base_frame_with_app(self):
        _obj = BaseFrameWithApp()
        # self.widgets.append(_obj)
        return _obj

    def test_init(self):
        obj = self.get_base_frame_with_app()
        self.assertIsInstance(obj, BaseFrameWithApp)
        self.assertEqual(obj.frame_index, -1)
        self.assertIsNone(obj._app)

    def test_set_app_wrong_class(self):
        obj = self.get_base_frame_with_app()
        with self.assertRaises(TypeError):
            obj._set_app("test")

    def test_set_app_no_existing_app(self):
        obj = self.get_base_frame_with_app()
        app = BaseApp()
        obj._set_app(app)
        self.assertIsInstance(obj._app, BaseApp)

    def test_set_app_existing_app(self):
        _bin = 5
        _fname = Path("test/file/name.txt")
        obj = self.get_base_frame_with_app()
        obj._app = BaseApp(
            get_generic_parameter("first_file"), get_generic_parameter("binning")
        )
        obj._app_attributes_to_update.append("test_attr")
        app = BaseApp(
            get_generic_parameter("first_file"), get_generic_parameter("binning")
        )
        app.set_param_value("binning", _bin)
        app.set_param_value("first_file", _fname)
        app._config["test_key"] = True
        app.test_attr = [True, False]
        obj._set_app(app)
        self.assertTrue(obj._app._config["test_key"])
        self.assertEqual(obj._app.get_param_value("binning"), _bin)
        self.assertEqual(obj._app.get_param_value("first_file"), _fname)
        self.assertEqual(obj._app.test_attr, app.test_attr)

    def test_apprunner_update_progress(self):
        _progress = 0.425
        obj = self.get_base_frame_with_app()
        obj._app = BaseApp()
        obj._widgets["progress"] = QtWidgets.QSpinBox()
        self.tester.signal.connect(obj._apprunner_update_progress)
        self.tester.send_progress(_progress)
        self.assertEqual(obj._widgets["progress"].value(), round(_progress * 100))

    def test_apprunner_finished(self):
        obj = self.get_base_frame_with_app()
        obj._runner = DummyRunner()
        self.tester.simple_signal.connect(obj._apprunner_finished)
        self.tester.simple_signal.emit()
        self.assertIsNone(obj._runner)


if __name__ == "__main__":
    unittest.main()
