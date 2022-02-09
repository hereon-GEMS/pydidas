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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import string
import random
import sys

import numpy as np
from PyQt5 import  QtWidgets

from pydidas.widgets.central_widget_stack import CentralWidgetStack


class TestWidget(QtWidgets.QWidget):
    ref_name = ''
    title = ''
    menuicon = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hash = hash(self)
        self.name =''.join(random.choice(string.ascii_letters)
                           for i in range(20))

    def frame_activated(self, index):
        ...


class TestCentralWidgetStack(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication(sys.argv)
        self.widgets = []

    def tearDown(self):
        self.q_app.deleteLater()
        self.q_app.quit()
        CentralWidgetStack._reset_instance()

    def create_stack(self):
        stack = CentralWidgetStack()
        for i in range(4):
            w = TestWidget()
            stack.register_widget(w.name, w)
            self.widgets.append(w)
        return stack

    def test_init(self):
        obj = CentralWidgetStack()
        self.assertIsInstance(obj, QtWidgets.QStackedWidget)
        self.assertTrue(hasattr(obj, 'widget_indices'))
        self.assertTrue(hasattr(obj, 'widgets'))

    def test_register_widget(self):
        stack = CentralWidgetStack()
        w = TestWidget()
        stack.register_widget(w.name, w)

    def test_register_widget_duplicate(self):
        stack = CentralWidgetStack()
        w = TestWidget()
        stack.register_widget(w.name, w)
        with self.assertRaises(KeyError):
            stack.register_widget(w.name, w)

    def test_get_name_from_index(self):
        stack = self.create_stack()
        _name = stack.get_name_from_index(0)
        self.assertEqual(_name, self.widgets[0].name)

    def test_get_widget_by_name__known_name(self):
        stack = self.create_stack()
        _w = stack.get_widget_by_name(self.widgets[0].name)
        self.assertEqual(_w, self.widgets[0])

    def test_get_widget_by_name__not_registered(self):
        stack = self.create_stack()
        with self.assertRaises(KeyError):
            stack.get_widget_by_name('no such widget')

    def test_get_all_widget_names(self):
        stack = self.create_stack()
        _names = stack.get_all_widget_names()
        self.assertEqual(len(self.widgets), len(_names))
        for w in self.widgets:
            self.assertTrue(w.ref_name in _names)

    def test_activate_widget_by_name(self):
        stack = self.create_stack()
        stack.activate_widget_by_name(self.widgets[-1].name)
        self.assertEqual(stack.currentIndex(), len(self.widgets) - 1)

    def test_activate_widget_by_name_wrong_name(self):
        stack = self.create_stack()
        with self.assertRaises(KeyError):
            stack.activate_widget_by_name('no such name')

    def test_remove_widget_by_name(self):
        stack = self.create_stack()
        stack.remove_widget_by_name(self.widgets[-1].name)

    def test_remove_widget_by_name_wrong_name(self):
        stack = self.create_stack()
        with self.assertRaises(KeyError):
            stack.remove_widget_by_name('no such name')

    def test_removeWidget_widget_not_registered(self):
        stack = self.create_stack()
        w = TestWidget()
        with self.assertRaises(KeyError):
            stack.removeWidget(w)

    def test_removeWidget(self):
        stack = self.create_stack()
        w = self.widgets[1]
        stack.removeWidget(w)
        _indices = set(stack.widget_indices.values())
        self.assertNotIn(w.name, stack.widget_indices.keys())
        self.assertNotIn(w, stack.widgets)
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
        self.assertEqual(stack.widgets, [])
        self.assertEqual(stack.widget_indices, {})

    def test_is_registered(self):
        stack = self.create_stack()
        self.assertTrue(stack.is_registered(self.widgets[0]))

    def test_is_registered_wrong_widget(self):
        stack = self.create_stack()
        self.assertFalse(stack.is_registered(TestWidget()))

    def test_change_reference_name__with_registered_widget(self):
        _new = 'The new widget name'
        stack = self.create_stack()
        w = self.widgets[0]
        stack.change_reference_name(_new, w)
        self.assertIn(_new, stack.widget_indices)
        self.assertEqual(w.ref_name, _new)

    def test_change_reference_name__with_unregistered_widget(self):
        _new = 'The new widget name'
        stack = self.create_stack()
        w = TestWidget()
        with self.assertRaises(KeyError):
            stack.change_reference_name(_new, w)


if __name__ == "__main__":
    unittest.main()
