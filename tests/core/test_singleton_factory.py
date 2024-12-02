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


import time
import unittest

from pydidas.core import SingletonFactory
from pydidas.core.utils import get_random_string
from qtpy import QtCore, QtWidgets


class TestClass:
    def __init__(self):
        self.attr1 = hash(time.time())
        self.attr2 = get_random_string(64)


class TestQObject(QtCore.QObject):
    def deleteLater(self):
        pass


class TestSingletonFactory(unittest.TestCase):
    def setUp(self):
        self.factory = SingletonFactory(TestClass)

    def tearDown(self):
        app = QtWidgets.QApplication.instance()
        if app is None:
            app.deleteLater()

    def test_setup(self):
        # test setUp method
        self.assertIsInstance(self.factory, SingletonFactory)

    def test_creation(self):
        obj = self.factory()
        self.assertIsInstance(obj, TestClass)

    def test_repeated_call(self):
        obj = self.factory()
        obj2 = self.factory()
        self.assertEqual(obj, obj2)

    def test_instance(self):
        obj = self.factory.instance
        self.assertIsInstance(obj, TestClass)

    def test_reset(self):
        obj = self.factory()
        self.factory._reset_instance()
        obj2 = self.factory()
        self.assertNotEqual(obj, obj2)

    def test_with_qobject(self):
        _factory = SingletonFactory(QtCore.QObject)
        obj = _factory()
        obj_id = id(obj)
        self.assertIsInstance(obj, QtCore.QObject)
        obj.deleteLater()
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        _timer = QtCore.QTimer(app)
        _timer.timeout.connect(app.exit)
        _timer.start(100)
        app.exec_()
        obj2 = _factory()
        self.assertNotEqual(id(obj2), obj_id)
        self.assertIsInstance(obj2, QtCore.QObject)


if __name__ == "__main__":
    unittest.main()
