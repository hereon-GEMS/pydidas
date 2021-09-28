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

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import string
import random

from PyQt5 import  QtWidgets

from pydidas._exceptions import WidgetLayoutError
from pydidas.widgets.create_widgets_mixin import (
    CreateWidgetsMixIn, _get_widget_layout_args, _get_grid_pos)


class TestWidget(QtWidgets.QWidget, CreateWidgetsMixIn):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent)
        self.hash = hash(self)
        self.name =''.join(random.choice(string.ascii_letters)
                           for i in range(20))


def get_test_widget(*args, **kwargs):
    return TestWidget()


class TestCreateWidgetsMixin(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication([])
        self.widgets = []

    def tearDown(self):
        self.q_app.deleteLater()
        self.q_app.quit()

    def get_widget(self):
        _w = TestWidget()
        _w.setLayout(QtWidgets.QGridLayout())
        return _w

    def test_get_grid_pos_default(self):
        obj = self.get_widget()
        _grid_pos = _get_grid_pos(obj)
        self.assertEqual(_grid_pos, (0, 0, 1, 2))

    def test_get_grid_pos_gridPos(self):
        _gridPos = (2, 7, 5, 3)
        obj = self.get_widget()
        _grid_pos = _get_grid_pos(obj, gridPos=_gridPos)
        self.assertEqual(_grid_pos, _gridPos)

    def test_get_grid_pos_kwargs(self):
        _gridPos = (2, 7, 5, 3)
        obj = self.get_widget()
        _grid_pos = _get_grid_pos(obj, row=_gridPos[0], column=_gridPos[1],
                                   n_rows=_gridPos[2], n_columns=_gridPos[3])
        self.assertEqual(_grid_pos, _gridPos)

    def test_get_grid_pos_auto_row(self):
        _gridPos = (-1, 7, 5, 3)
        obj = self.get_widget()
        _grid_pos = _get_grid_pos(obj, gridPos=_gridPos)
        self.assertEqual(_grid_pos, (0, ) + _gridPos[1:])

    def test_get_grid_pos_auto_row_more_items(self):
        _gridPos = (-1, 7, 5, 3)
        _nwidget = 4
        obj = self.get_widget()
        for i in range(_nwidget):
            _w = TestWidget()
            obj.layout().addWidget(_w, i, 0, 1, 1)
        _grid_pos = _get_grid_pos(obj, gridPos=_gridPos)
        self.assertEqual(_grid_pos, (_nwidget, ) + _gridPos[1:])

    def test__get_widget_layout_args_no_layout(self):
        obj = TestWidget()
        with self.assertRaises(WidgetLayoutError):
            _get_widget_layout_args(obj)

    def test__get_widget_layout_box(self):
        _stretch = 1.3
        _alignment = 'random'
        obj = TestWidget()
        obj.setLayout(QtWidgets.QVBoxLayout())
        items = _get_widget_layout_args(obj, stretch=_stretch,
                                        alignment=_alignment)
        self.assertEqual(items, [_stretch, _alignment])

    def test__get_widget_layout_stacked(self):
        _stretch = 1.3
        _alignment = 'random'
        obj = TestWidget()
        obj.setLayout(QtWidgets.QStackedLayout())
        items = _get_widget_layout_args(obj, stretch=_stretch,
                                        alignment=_alignment)
        self.assertEqual(items, [])

    def test__get_widget_layout_grid_no_alignment(self):
        _gridPos = (2, 7, 5, 3)
        obj = TestWidget()
        obj.setLayout(QtWidgets.QGridLayout())
        items = _get_widget_layout_args(obj, gridPos=_gridPos,
                                        alignment=None)
        self.assertEqual(items, [*_gridPos])

    def test__get_widget_layout_grid(self):
        _gridPos = (2, 7, 5, 3)
        obj = TestWidget()
        obj.setLayout(QtWidgets.QGridLayout())
        items = _get_widget_layout_args(obj, gridPos=_gridPos)
        self.assertEqual(items, [*_gridPos])

    def test_get_widget_layout_args(self):
        obj = self.get_widget()
        _grid_pos = _get_grid_pos(obj)
        self.assertEqual(_grid_pos, (0, 0, 1, 2))

    def test_init(self):
        obj = TestWidget()
        self.assertIsInstance(obj, CreateWidgetsMixIn)
        self.assertTrue(hasattr(obj, '_widgets'))

    def test_create_label(self):
        obj = self.get_widget()
        obj.create_label('ref', 'Test text', parent_widget=obj)
        _label = obj._widgets['ref']
        self.assertEqual(_label, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_label, QtWidgets.QLabel)

    def test_create_line(self):
        obj = self.get_widget()
        obj.create_line('ref', parent_widget=obj)
        _line = obj._widgets['ref']
        self.assertEqual(_line, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_line, QtWidgets.QFrame)

    def test_create_spacer(self):
        obj = self.get_widget()
        obj.create_spacer('ref', parent_widget=obj)
        _spacer = obj._widgets['ref']
        self.assertEqual(_spacer, obj.layout().itemAtPosition(0, 0))
        self.assertIsInstance(_spacer, QtWidgets.QSpacerItem)

    def test_create_button(self):
        _text = 'button text'
        obj = self.get_widget()
        obj.create_button('ref', _text, parent_widget=obj)
        _but = obj._widgets['ref']
        self.assertEqual(_but, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_but, QtWidgets.QPushButton)
        self.assertEqual(_but.text(), _text)

    def test_create_spinbox(self):
        obj = self.get_widget()
        obj.create_spin_box('ref', parent_widget=obj)
        _spin = obj._widgets['ref']
        self.assertEqual(_spin, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_spin, QtWidgets.QSpinBox)

    def test_create_progress_bar(self):
        obj = self.get_widget()
        obj.create_progress_bar('ref', parent_widget=obj)
        _bar = obj._widgets['ref']
        self.assertEqual(_bar, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_bar, QtWidgets.QProgressBar)

    def test_create_check_box(self):
        _text = 'another test text'
        obj = self.get_widget()
        obj.create_check_box('ref', _text, parent_widget=obj)
        _box = obj._widgets['ref']
        self.assertEqual(_box, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_box, QtWidgets.QCheckBox)
        self.assertEqual(_box.text(), _text)

    def test_create_widget__with_layout_args(self):
        obj = self.get_widget()
        obj._CreateWidgetsMixIn__create_widget(
            get_test_widget, 'ref', layout_kwargs={})
        self.assertTrue('ref' in obj._widgets)

    def test_create_any_widget__plain(self):
        obj = self.get_widget()
        obj.create_any_widget('ref', TestWidget)
        self.assertTrue('ref' in obj._widgets)

    def test_create_any_widget__wrong_ref(self):
        obj = self.get_widget()
        with self.assertRaises(TypeError):
            obj.create_any_widget(12, TestWidget)

    def test_add_any_widget__wrong_ref(self):
        obj = self.get_widget()
        with self.assertRaises(TypeError):
            obj.add_any_widget(12, TestWidget())

    def test_add_any_widget__plain(self):
        obj = self.get_widget()
        obj.add_any_widget('ref', TestWidget(), layout_kwargs={})
        self.assertTrue('ref' in obj._widgets)

if __name__ == "__main__":
    unittest.main()
