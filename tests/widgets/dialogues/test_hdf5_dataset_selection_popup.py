# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import shutil
import tempfile
import h5py
import os
import time

import numpy as np
from PyQt5 import  QtWidgets, QtTest, QtCore

from pydidas.widgets.dialogues.hdf5_dataset_selection_popup import (
    Hdf5DatasetSelectionPopup)
from pydidas.utils import timed_print

class TestHdf5DatasetSelectionPopup(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication([])
        self.obj = None
        self._path = tempfile.mkdtemp()
        self._fname = os.path.join(self._path, 'test_file.h5')
        self._h5keys = ['/test/data', '/other/data/set', '/other/data/set2',
                        '/another/data/set/in/the/file']
        with h5py.File(self._fname, 'w') as f:
            for _key in self._h5keys:
                f.create_dataset(_key, data=np.zeros((10, 10)))

    def tearDown(self):
        if isinstance(self.obj, QtCore.QObject):
            QtTest.QTest.keyClick(self.obj, QtCore.Qt.Key_Escape, delay=0)
            self.obj.deleteLater()
        self.q_app.deleteLater()
        self.q_app.quit()
        shutil.rmtree(self._path)

    def test_init__plain(self):
        obj = Hdf5DatasetSelectionPopup()
        self.assertIsInstance(obj, Hdf5DatasetSelectionPopup)

    def test_init__with_parent(self):
        _parent = QtWidgets.QWidget()
        obj = Hdf5DatasetSelectionPopup(_parent)
        self.assertEqual(obj.parent(), _parent)

    def test_init__with_fname(self):
        obj = Hdf5DatasetSelectionPopup(fname=self._fname)
        self.assertEqual(set(obj.comboBoxItems()), set(self._h5keys))

    def test_set_filename(self):
        obj = Hdf5DatasetSelectionPopup()
        obj.set_filename(self._fname)
        self.assertEqual(set(obj.comboBoxItems()), set(self._h5keys))

    def test_set_filename__no_file(self):
        obj = Hdf5DatasetSelectionPopup()
        with self.assertRaises(TypeError):
            obj.set_filename('something')

    def test_exec__esc(self):
        self.obj = Hdf5DatasetSelectionPopup()
        def click_esc():
            timed_print('click escape')
            QtTest.QTest.keyClick(self.obj, QtCore.Qt.Key_Escape, delay=1)

        QtCore.QTimer.singleShot(50, click_esc)
        timed_print('start event loop')
        _res = self.obj.exec_()
        timed_print('finished loop')
        self.assertEqual(_res, 0)

    # def test_exec__confirm(self):
    #     obj = Hdf5DatasetSelectionPopup()
    #     def click_esc():
    #         QtTest.QTest.keyClick(obj, QtCore.Qt.Enter, delay=0)
    #     QtCore.QTimer.singleShot(50, click_esc)
    #     _res = obj.exec_()
    #     print(_res)
    #     self.assertEqual(_res, 0)

        # QtTest.QTest.mouseClick(obj, QtCore.Qt.LeftButton, pos=(0, 0))

#         QTest::mouseClick(lw->viewport(), Qt::LeftButton, 0, itemPt);
#             QTest::qWait(1000);
#             // Reopen the combobox
#             QTest::mouseClick(cb, Qt::LeftButton);
#             QTest::qWait(1000);
#         }
#     }
# }
# // Close the combo box popup
# QTest::keyClick(cb, Qt::Key_Escape);

    # def test_set_text__text(self):
    #     _text = 'new text'
    #     obj = Hdf5DatasetSelectionPopup()
    #     obj.set_text(_text)
    #     self.assertEqual(obj._label.text(), _text)

    # def test_exec(self):
    #     obj = Hdf5DatasetSelectionPopup()
    #     obj.exec_()


if __name__ == "__main__":
    unittest.main()
