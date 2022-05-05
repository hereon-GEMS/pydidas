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
__maintainer__ = "Malte Storm"
__status__ = "Development"


import os
import unittest
import tempfile

import numpy as np

from pydidas.data_io.implementations import IoBase
from pydidas.data_io import IoMaster


def create_tester_class():
    class Tester(IoBase):
        extensions_export = [".test", ".export"]
        extensions_import = [".test", ".import"]
        format_name = "Tester"

        @classmethod
        def export_to_file(cls, filename, data, **kwargs):
            cls._exported = [filename, data, kwargs]

        @classmethod
        def import_from_file(cls, filename, **kwargs):
            cls._imported = [filename, kwargs]


class TestIoBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._stored_exts_import = IoMaster.registry_import.copy()
        cls._stored_exts_export = IoMaster.registry_export.copy()
        create_tester_class()
        cls._tmpdir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        IoMaster.registry_import = cls._stored_exts_import
        IoMaster.registry_export = cls._stored_exts_export

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_export_to_file(self):
        with self.assertRaises(NotImplementedError):
            IoBase.export_to_file("", None)

    def test_import_from_file(self):
        with self.assertRaises(NotImplementedError):
            IoBase.export_to_file("", None)

    def test_check_for_existing_file__file_exists(self):
        _fname = os.path.join(self._tmpdir, "test.txt")
        with open(_fname, "w") as f:
            f.write("Test text")
        with self.assertRaises(FileExistsError):
            IoBase.check_for_existing_file(_fname)

    def test_check_for_existing_file__file_exists_overwrite(self):
        _fname = os.path.join(self._tmpdir, "test.txt")
        with open(_fname, "w") as f:
            f.write("Test text")
        IoBase.check_for_existing_file(_fname, overwrite=True)
        # assert does not raise an error

    def test_check_for_existing_file__file_does_not_exist(self):
        _fname = os.path.join(self._tmpdir, "test.txt")
        IoBase.check_for_existing_file(_fname)
        # assert does not raise an error

    def test_return_data__no_data(self):
        with self.assertRaises(ValueError):
            IoBase.return_data()

    def test_return_data__plain(self):
        IoBase._data = np.random.random((10, 10))
        _data = IoBase.return_data()
        self.assertTrue((IoBase._data == _data).all())

    def test_return_data_w_roi(self):
        _roi = [2, 8, 2, 8]
        IoBase._data = np.random.random((10, 10))
        _cropped_data = IoBase._data[_roi[0] : _roi[1], _roi[2] : _roi[3]]
        _data = IoBase.return_data(roi=_roi)
        self.assertTrue((_cropped_data == _data).all())

    def test_return_data_w_return_type(self):
        IoBase._data = np.random.random((10, 10))
        _data = IoBase.return_data(datatype=np.float32)
        self.assertEqual(_data.dtype, np.float32)

    def test_return_data_w_binning(self):
        IoBase._data = np.random.random((10, 10))
        _data = IoBase.return_data(binning=2)
        self.assertEqual(_data.shape, (5, 5))

    def test_get_data_range__simple(self):
        _data = np.random.random((15, 15))
        _range = IoBase.get_data_range(_data)
        self.assertEqual(_range[0], np.amin(_data))
        self.assertEqual(_range[1], np.amax(_data))

    def test_get_data_range__lower_bound_only(self):
        _data = np.random.random((15, 15))
        _range = IoBase.get_data_range(_data, data_range=(0.4, None))
        self.assertEqual(_range[0], 0.4)
        self.assertEqual(_range[1], np.amax(_data))

    def test_get_data_range__upper_bound_only(self):
        _data = np.random.random((15, 15))
        _range = IoBase.get_data_range(_data, data_range=(None, 0.8))
        self.assertEqual(_range[0], np.amin(_data))
        self.assertEqual(_range[1], 0.8)

    def test_get_data_range__both_bounds(self):
        _data = np.random.random((15, 15))
        _range = IoBase.get_data_range(_data, data_range=(0.3, 0.8))
        self.assertEqual(_range[0], 0.3)
        self.assertEqual(_range[1], 0.8)


if __name__ == "__main__":
    unittest.main()
