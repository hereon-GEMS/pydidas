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

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import os
import tempfile
import h5py
import shutil

import numpy as np
from PyQt5 import QtWidgets, QtTest

from pydidas.constants import FrameConfigError
from pydidas.widgets.hdf5_dataset_selector import Hdf5DatasetSelector


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

    def setUp(self):
        self.q_app = QtWidgets.QApplication([])
        self.widgets = []
        self._path = tempfile.mkdtemp()
        self._fname = os.path.join(self._path, 'test.h5')
        self.data1d = np.random.random((20))
        self.data2d = np.random.random((20, 20))
        self.data3d = np.random.random((20, 20, 20))
        with h5py.File(self._fname, 'w') as _file:
            _file.create_group('test')
            _file['test'].create_group('test2')
            _file['test/test2'].create_dataset('data1', data=self.data1d)
            _file['test/test2'].create_dataset('data2', data=self.data2d)
            _file['test/test2'].create_dataset('data3', data=self.data3d)
        self._dsets = ['/test/test2/data1', '/test/test2/data2',
                       '/test/test2/data3']

    def tearDown(self):
        self.q_app.deleteLater()
        self.q_app.quit()
        del self.q_app
        shutil.rmtree(self._path)

    def test_init(self):
        obj = Hdf5DatasetSelector()
        self.assertIsInstance(obj, Hdf5DatasetSelector)
        self.assertIsNone(obj._frame)
        self.assertEqual(obj._config['activeDsetFilters'], [])

    def test_register_view_widget_no_widget(self):
        obj = Hdf5DatasetSelector()
        _widget = None
        with self.assertRaises(TypeError):
            obj.register_view_widget(_widget)

    def test_register_view_widget_widget_without_set_data(self):
        obj = Hdf5DatasetSelector()
        _widget = TestWidget()
        with self.assertRaises(TypeError):
            obj.register_view_widget(_widget)

    def test_register_view_widget_correct_widget(self):
        obj = Hdf5DatasetSelector()
        _widget = TestWidgetWithSetData()
        obj.register_view_widget(_widget)
        self.assertEqual(obj._widgets['viewer'], _widget)

    def test_toggle_filter_key_nothing_happens(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        obj._toggle_filter_key(widget, 'test')
        self.assertEqual(obj._config['activeDsetFilters'], [])

    def test_toggle_filter_key_remove_key(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        obj._config['activeDsetFilters'] = ['test']
        obj._toggle_filter_key(widget, 'test')
        self.assertEqual(obj._config['activeDsetFilters'], [])

    def test_toggle_filter_key_add_key(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        widget.setChecked(True)
        obj._toggle_filter_key(widget, 'test')
        self.assertEqual(obj._config['activeDsetFilters'], ['test'])

    def test_toggle_filter_key_key_already_in_list(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        widget = TestCheckBox()
        obj._config['activeDsetFilters'] = ['test']
        widget.setChecked(True)
        obj._toggle_filter_key(widget, 'test')
        self.assertEqual(obj._config['activeDsetFilters'], ['test'])

    def test__populate_dataset_list_no_limit(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['min_datasize'].setValue(0)
        obj._widgets['min_datadim'].setValue(0)
        _widget = obj._widgets['select_dataset']
        _items = [_widget.itemText(i) for i in range(_widget.count())]
        self.assertEqual(_items, self._dsets)

    def test__populate_dataset_list_limit(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['min_datasize'].setValue(50)
        obj._widgets['min_datadim'].setValue(0)
        _widget = obj._widgets['select_dataset']
        _items = [_widget.itemText(i) for i in range(_widget.count())]
        self.assertEqual(_items, ['/test/test2/data2', '/test/test2/data3'])

    def test__populate_dataset_list_dimlimit(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['min_datasize'].setValue(0)
        obj._widgets['min_datadim'].setValue(2)
        _widget = obj._widgets['select_dataset']
        _items = [_widget.itemText(i) for i in range(_widget.count())]
        self.assertEqual(_items, ['/test/test2/data2', '/test/test2/data3'])

    def test__get_frame_3d(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['select_dataset'].setCurrentIndex(1)
        obj._Hdf5DatasetSelector__get_frame()
        self.assertTrue(np.allclose(self.data3d[0], obj._frame))

    def test__get_frame_2d(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['select_dataset'].setCurrentIndex(0)
        obj._Hdf5DatasetSelector__get_frame()
        self.assertTrue(np.allclose(self.data2d, obj._frame))

    def test_toggle_auto_update_false(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['auto_update'].setChecked(False)
        obj._toggle_auto_update()
        self.assertFalse(obj.flags['autoUpdate'])

    def test_toggle_auto_update_true(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj._widgets['auto_update'].setChecked(True)
        obj._toggle_auto_update()
        self.assertTrue(obj.flags['autoUpdate'])

    def test_enable_signal_slot_enable(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj.enable_signal_slot(True)
        spy = QtTest.QSignalSpy(obj.new_frame_signal)
        obj._Hdf5DatasetSelector__update()
        self.assertEqual(len(spy), 1)
        self.assertTrue(np.allclose(spy[0], self.data2d))

    def test_enable_signal_slot_disable(self):
        obj = Hdf5DatasetSelector()
        obj.set_filename(self._fname)
        obj.enable_signal_slot(False)
        spy = QtTest.QSignalSpy(obj.new_frame_signal)
        obj._Hdf5DatasetSelector__update()
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
        with self.assertRaises(FrameConfigError):
            obj.click_view_button()


if __name__ == "__main__":
    unittest.main()
