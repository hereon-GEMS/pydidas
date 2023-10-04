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


import random
import string
import unittest

import numpy as np
from qtpy import QtWidgets

from pydidas.widgets.framework import BaseFrame, PydidasFrameStack


class TestWidget(BaseFrame):
    ref_name = ""
    title = ""
    menu_icon = None
    menu_entry = "Test/Entry"
    menu_title = "Test"

    def __init__(self, **kwargs):
        BaseFrame.__init__(self, **kwargs)
        self.hash = hash(self)
        self.menu_entry = "".join(
            random.choice(string.ascii_letters) for i in range(20)
        )

    def frame_activated(self, index):
        ...


class TestPydidasFrameStack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._qtapp = QtWidgets.QApplication.instance()
        if cls._qtapp is None:
            cls._qtapp = QtWidgets.QApplication([])
        cls.frames = []

    @classmethod
    def tearDownClass(cls):
        while cls.frames:
            w = cls.frames.pop()
            w.deleteLater()
        cls._qtapp.quit()
        app = QtWidgets.QApplication.instance()
        if app is None:
            app.deleteLater()

    def setUp(self):
        self.frames = []

    def create_stack(self):
        stack = PydidasFrameStack()
        stack.reset()
        for i in range(4):
            w = TestWidget()
            stack.register_frame(w)
            self.frames.append(w)
        return stack

    def test_init(self):
        obj = PydidasFrameStack()
        self.assertIsInstance(obj, QtWidgets.QStackedWidget)
        self.assertTrue(hasattr(obj, "frame_indices"))
        self.assertTrue(hasattr(obj, "frames"))

    def test_register_frame(self):
        stack = PydidasFrameStack()
        w = TestWidget()
        stack.register_frame(w)

    def test_register_frame_duplicate(self):
        stack = PydidasFrameStack()
        w = TestWidget()
        stack.register_frame(w)
        with self.assertRaises(KeyError):
            stack.register_frame(w)

    def test_get_name_from_index(self):
        stack = self.create_stack()
        _name = stack.get_name_from_index(0)
        self.assertEqual(_name, self.frames[0].menu_entry)

    def test_get_widget_by_name__known_name(self):
        stack = self.create_stack()
        _w = stack.get_widget_by_name(self.frames[0].menu_entry)
        self.assertEqual(_w, self.frames[0])

    def test_get_widget_by_name__not_registered(self):
        stack = self.create_stack()
        with self.assertRaises(KeyError):
            stack.get_widget_by_name("no such widget")

    def test_get_all_widget_names(self):
        stack = self.create_stack()
        _names = stack.get_all_widget_names()
        self.assertEqual(len(self.frames), len(_names))
        for w in self.frames:
            self.assertTrue(w.menu_entry in _names)

    def test_activate_widget_by_name(self):
        stack = self.create_stack()
        stack.activate_widget_by_name(self.frames[-1].menu_entry)
        self.assertEqual(stack.currentIndex(), len(self.frames) - 1)

    def test_activate_widget_by_name_wrong_name(self):
        stack = self.create_stack()
        with self.assertRaises(KeyError):
            stack.activate_widget_by_name("no such name")

    def test_remove_widget_by_name(self):
        stack = self.create_stack()
        stack.remove_widget_by_name(self.frames[-1].menu_entry)

    def test_remove_widget_by_name_wrong_name(self):
        stack = self.create_stack()
        with self.assertRaises(KeyError):
            stack.remove_widget_by_name("no such name")

    def test_removeWidget_widget_not_registered(self):
        stack = self.create_stack()
        w = TestWidget()
        with self.assertRaises(KeyError):
            stack.removeWidget(w)

    def test_removeWidget(self):
        stack = self.create_stack()
        w = self.frames[1]
        stack.removeWidget(w)
        _indices = set(stack.frame_indices.values())
        self.assertNotIn(w.menu_entry, stack.frame_indices.keys())
        self.assertNotIn(w, stack.frames)
        self.assertEqual(_indices, set(np.arange(stack.count())))

    def test_addWidget(self):
        stack = self.create_stack()
        w = TestWidget()
        with self.assertRaises(NotImplementedError):
            stack.addWidget(w)

    def test_reset(self):
        stack = self.create_stack()
        stack.reset()
        self.assertEqual(stack.count(), 0)
        self.assertEqual(stack.frames, [])
        self.assertEqual(stack.frame_indices, {})

    def test_is_registered(self):
        stack = self.create_stack()
        self.assertTrue(stack.is_registered(self.frames[0]))

    def test_is_registered_wrong_widget(self):
        stack = self.create_stack()
        self.assertFalse(stack.is_registered(TestWidget()))

    def test_change_reference_name__with_registered_widget(self):
        _new = "The new widget name"
        stack = self.create_stack()
        w = self.frames[0]
        stack.change_reference_name(_new, w)
        self.assertIn(_new, stack.frame_indices)
        self.assertEqual(w.menu_entry, _new)

    def test_change_reference_name__with_unregistered_widget(self):
        _new = "The new widget name"
        stack = self.create_stack()
        w = TestWidget()
        with self.assertRaises(KeyError):
            stack.change_reference_name(_new, w)


if __name__ == "__main__":
    unittest.main()
