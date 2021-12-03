# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest

from PyQt5 import QtCore, QtWidgets

from pydidas.widgets.base_frame import BaseFrame


class TestClass(QtCore.QObject):
    signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.reveived_signals = []

    def get_signal(self, obj):
        self.reveived_signals.append(obj)

    def send_signal(self, sig):
        self.signal.emit(sig)


class TestBaseFrame(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication([])
        self.tester = TestClass()

    def tearDown(self):
        self.q_app.deleteLater()
        self.q_app.quit()

    def get_base_frame(self, **kwargs):
        return BaseFrame(**kwargs)

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
        _test = 'This is the test status.'
        obj = self.get_base_frame()
        obj.status_msg.connect(self.tester.get_signal)
        obj.set_status(_test)
        self.assertEqual(self.tester.reveived_signals.pop(), _test)

    def test_next_row_empty(self):
        obj = self.get_base_frame()
        _row = obj.next_row()
        self.assertEqual(_row, 0)

    def test_next_row(self):
        obj = self.get_base_frame()
        w = QtWidgets.QLabel('test')
        w2 = QtWidgets.QLabel('test2')
        obj.layout().addWidget(w, 0, 0, 1, 1)
        obj.layout().addWidget(w2, 1, 0, 1, 1)
        _row = obj.next_row()
        self.assertEqual(_row, 2)


if __name__ == "__main__":
    unittest.main()
