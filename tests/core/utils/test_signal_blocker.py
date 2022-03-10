# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

from qtpy import QtCore, QtTest

from pydidas.core.utils import SignalBlocker


class Tester(QtCore.QObject):
    sig = QtCore.Signal(object)

    def __init__(self):
        super().__init__()

    def send(self, obj):
        self.sig.emit(obj)


class TestSignalBlocker(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test__base_object(self):
        _tester = Tester()
        _spy = QtTest.QSignalSpy(_tester.sig)
        _tester.send(1)
        self.assertEqual(len(_spy), 1)

    def test_signal_blocker__w_qobject(self):
        _tester = Tester()
        _spy = QtTest.QSignalSpy(_tester.sig)
        with SignalBlocker(_tester):
            _tester.send(1)
        self.assertEqual(len(_spy), 0)

    def test_signal_blocker__w_wrong_object(self):
        with self.assertRaises(TypeError):
            SignalBlocker(12)


if __name__ == "__main__":
    unittest.main()
