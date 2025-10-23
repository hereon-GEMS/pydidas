# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import random
import string
import unittest

from qtpy import QtWidgets

from pydidas.core import PydidasGuiError
from pydidas.widgets.factory.create_widgets_mixin import CreateWidgetsMixIn
from pydidas.widgets.utilities import get_grid_pos, get_widget_layout_args
from pydidas_qtcore import PydidasQApplication


class _TestWidget(QtWidgets.QWidget, CreateWidgetsMixIn):
    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(parent)
        self.hash = hash(self)
        self.name = "".join(random.choice(string.ascii_letters) for i in range(20))


class TestCreateWidgetsMixIn(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q_app = QtWidgets.QApplication.instance()
        if cls.q_app is None:
            cls.q_app = PydidasQApplication([])
        cls.widgets = []

    @classmethod
    def tearDownClass(cls):
        while cls.widgets:
            w = cls.widgets.pop()
            w.deleteLater()
        cls.q_app.quit()
        app = QtWidgets.QApplication.instance()
        if app is None:
            app.deleteLater()

    def setUp(self): ...

    def tearDown(self): ...

    def get_widget(self, layout=QtWidgets.QGridLayout):
        _w = _TestWidget()
        if layout is not None:
            _w.setLayout(layout())
        self.widgets.append(_w)
        return _w

    def testget_grid_pos_default(self):
        obj = self.get_widget()
        _grid_pos = get_grid_pos(obj)
        self.assertEqual(_grid_pos, (0, 0, 1, 1))

    def testget_grid_pos_gridPos(self):
        _gridPos = (2, 7, 5, 3)
        obj = self.get_widget()
        _grid_pos = get_grid_pos(obj, gridPos=_gridPos)
        self.assertEqual(_grid_pos, _gridPos)

    def testget_grid_pos_kwargs(self):
        _gridPos = (2, 7, 5, 3)
        obj = self.get_widget()
        _grid_pos = get_grid_pos(
            obj,
            row=_gridPos[0],
            column=_gridPos[1],
            n_rows=_gridPos[2],
            n_columns=_gridPos[3],
        )
        self.assertEqual(_grid_pos, _gridPos)

    def testget_grid_pos_auto_row(self):
        _gridPos = (-1, 7, 5, 3)
        obj = self.get_widget()
        _grid_pos = get_grid_pos(obj, gridPos=_gridPos)
        self.assertEqual(_grid_pos, (0,) + _gridPos[1:])

    def testget_grid_pos_auto_row_more_items(self):
        _gridPos = (-1, 7, 5, 3)
        _nwidget = 4
        obj = self.get_widget()
        for i in range(_nwidget):
            _w = _TestWidget()
            obj.layout().addWidget(_w, i, 0, 1, 1)
        _grid_pos = get_grid_pos(obj, gridPos=_gridPos)
        self.assertEqual(_grid_pos, (_nwidget,) + _gridPos[1:])

    def testget_widget_layout_args_no_layout(self):
        obj = _TestWidget()
        with self.assertRaises(PydidasGuiError):
            get_widget_layout_args(obj)

    def test_get_widget_layout_box(self):
        _stretch = 1.3
        _alignment = "random"
        obj = _TestWidget()
        obj.setLayout(QtWidgets.QVBoxLayout())
        items = get_widget_layout_args(obj, stretch=_stretch, alignment=_alignment)
        self.assertEqual(items, [_stretch, _alignment])

    def test_get_widget_layout_stacked(self):
        _stretch = 1.3
        _alignment = "random"
        obj = _TestWidget()
        obj.setLayout(QtWidgets.QStackedLayout())
        items = get_widget_layout_args(obj, stretch=_stretch, alignment=_alignment)
        self.assertEqual(items, [])

    def test_get_widget_layout_grid_no_alignment(self):
        _gridPos = (2, 7, 5, 3)
        obj = _TestWidget()
        obj.setLayout(QtWidgets.QGridLayout())
        items = get_widget_layout_args(obj, gridPos=_gridPos, alignment=None)
        self.assertEqual(items, [*_gridPos])

    def test_get_widget_layout_grid(self):
        _gridPos = (2, 7, 5, 3)
        obj = _TestWidget()
        obj.setLayout(QtWidgets.QGridLayout())
        items = get_widget_layout_args(obj, gridPos=_gridPos)
        self.assertEqual(items, [*_gridPos])

    def testget_widget_layout_args(self):
        obj = self.get_widget()
        _grid_pos = get_grid_pos(obj)
        self.assertEqual(_grid_pos, (0, 0, 1, 1))

    def test_init(self):
        obj = _TestWidget()
        self.assertIsInstance(obj, CreateWidgetsMixIn)
        self.assertTrue(hasattr(obj, "_widgets"))

    def test_create_label(self):
        obj = self.get_widget()
        obj.create_label("ref", "Test text", parent_widget=obj)
        _label = obj._widgets["ref"]
        self.assertEqual(_label, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_label, QtWidgets.QLabel)

    def test_create_line(self):
        obj = self.get_widget()
        obj.create_line("ref", parent_widget=obj)
        _line = obj._widgets["ref"]
        self.assertEqual(_line, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_line, QtWidgets.QFrame)

    def test_create_spacer(self):
        obj = self.get_widget()
        obj.create_spacer("ref", parent_widget=obj)
        _spacer = obj._widgets["ref"]
        self.assertEqual(_spacer, obj.layout().itemAtPosition(0, 0))
        self.assertIsInstance(_spacer, QtWidgets.QSpacerItem)

    def test_create_button(self):
        _text = "button text"
        obj = self.get_widget()
        obj.create_button("ref", _text, parent_widget=obj)
        _but = obj._widgets["ref"]
        self.assertEqual(_but, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_but, QtWidgets.QPushButton)
        self.assertEqual(_but.text(), _text)

    def test_create_spinbox(self):
        obj = self.get_widget()
        obj.create_spin_box("ref", parent_widget=obj)
        _spin = obj._widgets["ref"]
        self.assertEqual(_spin, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_spin, QtWidgets.QSpinBox)

    def test_create_progress_bar(self):
        obj = self.get_widget()
        obj.create_progress_bar("ref", parent_widget=obj)
        _bar = obj._widgets["ref"]
        self.assertEqual(_bar, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_bar, QtWidgets.QProgressBar)

    def test_create_check_box(self):
        _text = "another test text"
        obj = self.get_widget()
        obj.create_check_box("ref", _text, parent_widget=obj)
        _box = obj._widgets["ref"]
        self.assertEqual(_box, obj.layout().itemAtPosition(0, 0).widget())
        self.assertIsInstance(_box, QtWidgets.QCheckBox)
        self.assertEqual(_box.text(), _text)

    def test_create_widget__with_layout_args(self):
        obj = self.get_widget()
        obj.create_any_widget("ref", _TestWidget, layout_kwargs={})
        self.assertTrue("ref" in obj._widgets)

    def test_create_any_widget__plain(self):
        obj = self.get_widget()
        obj.create_any_widget("ref", _TestWidget)
        self.assertTrue("ref" in obj._widgets)

    def test_create_any_widget__wrong_ref(self):
        obj = self.get_widget()
        with self.assertRaises(TypeError):
            obj.create_any_widget(12, _TestWidget)

    def test_add_any_widget__wrong_ref(self):
        obj = self.get_widget()
        with self.assertRaises(TypeError):
            obj.add_any_widget(12, _TestWidget())

    def test_add_any_widget__plain(self):
        obj = self.get_widget()
        obj.add_any_widget("ref", _TestWidget(), layout_kwargs={})
        self.assertTrue("ref" in obj._widgets)


if __name__ == "__main__":
    unittest.main()
