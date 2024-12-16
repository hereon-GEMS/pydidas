# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

from qtpy import QtCore, QtWidgets

from pydidas.core import Parameter
from pydidas.core.utils import get_random_string
from pydidas.widgets.framework import BaseFrame
from pydidas_qtcore import PydidasQApplication


class SignalTestClass(QtCore.QObject):
    signal = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        self.reveived_signals = []

    def get_signal(self, obj):
        self.reveived_signals.append(obj)

    def send_signal(self, sig):
        self.signal.emit(sig)


class TestBaseFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._qtapp = QtWidgets.QApplication.instance()
        if cls._qtapp is None:
            cls._qtapp = PydidasQApplication([])

        cls.tester = SignalTestClass()
        # cls.widgets = []

    @classmethod
    def tearDownClass(cls):
        # while cls.widgets:
        #     w = cls.widgets.pop()
        #     w.deleteLater()
        cls._qtapp.quit()
        app = QtWidgets.QApplication.instance()
        if app is None:
            app.deleteLater()

    def get_base_frame(self, **kwargs):
        _frame = BaseFrame(**kwargs)
        # self.widgets.append(_frame)
        _frame.add_param(Parameter("test_int", int, 24))
        _frame.add_param(Parameter("test_str", str, get_random_string(30)))
        _frame.create_param_widget(_frame.get_param("test_int"))
        return _frame

    def create_widgets_in_frame(self, frame, n=6):
        for _index in range(n):
            frame.create_label(f"label_{_index}", get_random_string(120))

    def test_init(self):
        obj = self.get_base_frame()
        self.assertIsInstance(obj, BaseFrame)
        self.assertEqual(obj.frame_index, -1)
        self.assertIsInstance(obj.layout(), QtWidgets.QGridLayout)

    def test_frame_activated(self):
        obj = self.get_base_frame()
        self.tester.signal.connect(obj.frame_activated)
        self.tester.send_signal(1)

    def test_set_status(self):
        _test = "This is the test status."
        obj = self.get_base_frame()
        obj.status_msg.connect(self.tester.get_signal)
        obj.set_status(_test)
        self.assertEqual(self.tester.reveived_signals.pop(), _test)

    def test_export_state(self):
        _n = 10
        obj = self.get_base_frame()
        self.create_widgets_in_frame(obj, _n)
        QtCore.QTimer.singleShot(100, self._qtapp.quit)
        obj.show()
        _, _state = obj.export_state()
        self.assertEqual(obj.get_param_values_as_dict(), _state["params"])

    def test_restore_state__hidden_frame(self):
        _n = 10
        obj = self.get_base_frame()
        obj._config["built"] = False
        self.create_widgets_in_frame(obj, _n)
        _params = {"test_int": 42, "test_str": get_random_string(10)}
        _state = {"params": _params}
        QtCore.QTimer.singleShot(100, self._qtapp.quit)
        obj.show()
        obj.restore_state(_state)
        self.assertEqual(obj._config["state"], _state)

    def test_restore_state__frame_visible(self):
        _n = 10
        obj = self.get_base_frame()
        self.create_widgets_in_frame(obj, _n)
        obj.frame_activated(obj.frame_index)
        _params = {"test_int": 42, "test_str": get_random_string(10)}
        _state = {"params": _params}
        QtCore.QTimer.singleShot(100, self._qtapp.quit)
        obj.show()
        obj.restore_state(_state)
        _, _state = obj.export_state()
        self.assertEqual(_params, _state["params"])


if __name__ == "__main__":
    unittest.main()
