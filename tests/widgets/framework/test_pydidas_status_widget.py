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


import sys
import unittest

from pydidas.widgets.framework import PydidasStatusWidget
from pydidas_qtcore import PydidasQApplication
from qtpy import QtCore, QtWidgets


class TestPydidasStatusWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q_app = QtWidgets.QApplication.instance()
        if cls.q_app is None:
            cls.q_app = PydidasQApplication(sys.argv)
        cls.widgets = []

    @classmethod
    def tearDownClass(cls):
        cls.q_app.quit()

    def test_init(self):
        obj = PydidasStatusWidget()
        self.assertIsInstance(obj, QtWidgets.QDockWidget)

    def test_sizeHint(self):
        obj = PydidasStatusWidget()
        self.assertEqual(obj.sizeHint(), QtCore.QSize(500, 50))

    def test_add_status(self):
        _test = "This is the test string"
        obj = PydidasStatusWidget()
        obj.add_status(_test)
        _text = obj.text()
        self.assertTrue(_text.strip().endswith(_test))


if __name__ == "__main__":
    unittest.main()
