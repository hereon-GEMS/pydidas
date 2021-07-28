# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import sys

from PyQt5 import QtWidgets, QtCore

from pydidas.widgets.info_widget import GetInfoWidget


class TestCentralWidgetStack(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication(sys.argv)
        self.widgets = []

    def tearDown(self):
        self.q_app.quit()

    def test_init(self):
        obj = GetInfoWidget()
        self.assertIsInstance(obj, QtWidgets.QPlainTextEdit)

    def test_sizeHint(self):
        obj = GetInfoWidget()
        self.assertEqual(obj.sizeHint(), QtCore.QSize(500, 50))

    def test_add_status(self):
        _test = 'This is the test string'
        obj = GetInfoWidget()
        obj.add_status(_test)
        _text = obj.toPlainText()
        self.assertTrue(_text.strip().endswith(_test))


if __name__ == "__main__":
    unittest.main()
