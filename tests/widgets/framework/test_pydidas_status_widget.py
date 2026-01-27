# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

from qtpy import QtCore, QtWidgets

from pydidas.widgets.framework import PydidasStatusWidget


class TestPydidasStatusWidget(unittest.TestCase):
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
