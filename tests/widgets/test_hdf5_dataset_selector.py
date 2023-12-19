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


import os
import shutil
import tempfile
import unittest

import h5py
import numpy as np
from qtpy import QtTest, QtWidgets

from pydidas import IS_QT6
from pydidas.core import PydidasGuiError
from pydidas.widgets.selection import Hdf5DatasetSelector
from pydidas_qtcore import PydidasQApplication


class TestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class TestWidgetWithSetData(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setData(self, data):
        self.data = data


class TestCheckBox(QtWidgets.QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)


class TestHdf5DatasetSelector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q_app = QtWidgets.QApplication.instance()
        if cls.q_app is None:
            cls.q_app = PydidasQApplication([])
        cls.widgets = []

        cls._path = tempfile.mkdtemp()
        cls._fname = os.path.join(cls._path, "test.h5")
        cls.data1d = np.random.random((20))
        cls.data2d = np.random.random((20, 20))
        cls.data3d = np.random.random((20, 20, 20))
        with h5py.File(cls._fname, "w") as _file:
            _file.create_group("test")
            _file["test"].create_group("test2")
            _file["test/test2"].create_dataset("data1", data=cls.data1d)
            _file["test/test2"].create_dataset("data2", data=cls.data2d)
            _file["test/test2"].create_dataset("data3", data=cls.data3d)
        cls._dsets = ["/test/test2/data1", "/test/test2/data2", "/test/test2/data3"]

    @classmethod
    def tearDownClass(cls):
        cls.q_app.quit()
        app = QtWidgets.QApplication.instance()
        if app is None:
            app.deleteLater()
        shutil.rmtree(cls._path)

    def test_init(self):
        obj = Hdf5DatasetSelector()
        self.assertIsInstance(obj, Hdf5DatasetSelector)
        self.assertIsNone(obj._frame)
        self.assertEqual(obj._config["activeDsetFilters"], [])

    def test_register_view_widget__no_widget(self):
        obj = Hdf5DatasetSelector()
        _widget = None
        with self.assertRaises(TypeError):
            obj.register_view_widget(_widget)

    def test_register_view_widget__widget_without_set_data(self):
        obj = Hdf5DatasetSelector()
        _widget = TestWidget()
        with self.assertRaises(TypeError):
            obj.register_view_widget(_widget)

    def test_register_view_widget__correct_widget(self):
        obj = Hdf5DatasetSelector()
        _widget = TestWidgetWithSetData()
        obj.register_view_widget(_widget)
        self.assertEqual(obj._widgets["viewer"], _widget)

    def test_toggle_filter_key__nothing_happens(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        obj._toggle_filter_key(widget, "test")
        self.assertEqual(obj._config["activeDsetFilters"], [])

    def test_toggle_filter_key__remove_key(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        obj._config["activeDsetFilters"] = ["test"]
        obj._toggle_filter_key(widget, "test")
        self.assertEqual(obj._config["activeDsetFilters"], [])

    def test_toggle_filter_key__add_key(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        widget.setChecked(True)
        obj._toggle_filter_key(widget, "test")
        self.assertEqual(obj._config["activeDsetFilters"], ["test"])

    def test_toggle_filter_key_key_already_in_list(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        obj._config["activeDsetFilters"] = ["test"]
        widget.setChecked(True)
        obj._toggle_filter_key(widget, "test")
        self.assertEqual(obj._config["activeDsetFilters"], ["test"])

    def test_populate_dataset_list_no_limit(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["min_datasize"].setValue(0)
        obj._widgets["min_datadim"].setValue(0)
        _widget = obj._widgets["select_dataset"]
        _items = [_widget.itemText(i) for i in range(_widget.count())]
        self.assertEqual(_items, self._dsets)

    def test_populate_dataset_list_limit(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["min_datasize"].setValue(50)
        obj._widgets["min_datadim"].setValue(0)
        _widget = obj._widgets["select_dataset"]
        _items = [_widget.itemText(i) for i in range(_widget.count())]
        self.assertEqual(_items, ["/test/test2/data2", "/test/test2/data3"])

    def test_populate_dataset_list_dimlimit(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["min_datasize"].setValue(0)
        obj._widgets["min_datadim"].setValue(2)
        _widget = obj._widgets["select_dataset"]
        _items = [_widget.itemText(i) for i in range(_widget.count())]
        self.assertEqual(_items, ["/test/test2/data2", "/test/test2/data3"])

    def test_get_frame_3d(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["select_dataset"].setCurrentIndex(1)
        obj._Hdf5DatasetSelector__get_frame()
        self.assertTrue(np.allclose(self.data3d[0], obj._frame))

    def test_get_frame_2d(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["select_dataset"].setCurrentIndex(0)
        obj._Hdf5DatasetSelector__get_frame()
        self.assertTrue(np.allclose(self.data2d, obj._frame))

    def test_toggle_auto_update_false(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["auto_update"].setChecked(False)
        obj._toggle_auto_update()
        self.assertFalse(obj.flags["autoUpdate"])

    def test_toggle_auto_update_true(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets["auto_update"].setChecked(True)
        obj._toggle_auto_update()
        self.assertTrue(obj.flags["autoUpdate"])

    def test_enable_signal_slot_enable(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj.enable_signal_slot(True)
        spy = QtTest.QSignalSpy(obj.new_frame_signal)
        obj._Hdf5DatasetSelector__update()
        if IS_QT6:
            self.assertEqual(spy.count(), 1)
            self.assertTrue(np.allclose(spy.at(0)[0], self.data2d))
        else:
            self.assertEqual(len(spy), 1)
            self.assertTrue(np.allclose(spy[0], self.data2d))

    def test_enable_signal_slot_disable(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj.enable_signal_slot(False)
        spy = QtTest.QSignalSpy(obj.new_frame_signal)
        obj._Hdf5DatasetSelector__update()
        if IS_QT6:
            self.assertEqual(spy.count(), 0)
        else:
            self.assertEqual(len(spy), 0)

    def test_click_view_button(self):
        _widget = TestWidgetWithSetData()
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj.register_view_widget(_widget)
        obj.click_view_button()
        self.assertTrue(np.allclose(_widget.data, self.data2d))

    def test_click_view_button_no_widget(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        with self.assertRaises(PydidasGuiError):
            obj.click_view_button()


if __name__ == "__main__":
    unittest.main()
