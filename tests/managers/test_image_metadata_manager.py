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


import os
import shutil
import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np

from pydidas.core import UserConfigError, get_generic_parameter
from pydidas.managers import ImageMetadataManager


class TestImageMetadataManager(unittest.TestCase):
    def setUp(self):
        self._dsize = 40
        self._path = tempfile.mkdtemp()
        self._fname = lambda _i: Path(os.path.join(self._path, f"test_{_i:03d}.npy"))
        self._img_shape = (32, 35)
        self._data = np.random.random((self._dsize,) + self._img_shape)
        for i in range(self._dsize):
            np.save(self._fname(i), self._data[i])
        self._hdf5_fname = Path(os.path.join(self._path, "test_000.h5"))
        with h5py.File(self._hdf5_fname, "w") as f:
            f["/entry/data/data"] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def create_second_dataset(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path, f"test_{i:03d}.npy"))
        _img_shape = (47, 35)
        _data = np.random.random((self._dsize,) + _img_shape)
        _hdf5_fname = Path(os.path.join(self._path, "test_001.h5"))
        with h5py.File(_hdf5_fname, "w") as f:
            f["/entry/data/data"] = _data
        self._hdf5_fname2 = _hdf5_fname
        self._img_shape2 = _img_shape

    def test_creation(self):
        imm = ImageMetadataManager()
        self.assertIsInstance(imm, ImageMetadataManager)

    def test_get_modulated_roi__no_roi(self):
        _shapex = 123
        _shapey = 435
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_shapex, _roi[1] - _roi[0])
        self.assertEqual(_shapey, _roi[3] - _roi[2])

    def test_get_modulated_roi__xlow_set(self):
        _shapex = 123
        _shapey = 435
        _xlow = 23
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.set_param_value("roi_xlow", _xlow)
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_shapex - _xlow, _roi[1] - _roi[0])
        self.assertEqual(_shapey, _roi[3] - _roi[2])

    def test_get_modulated_roi__xhigh_set_positive(self):
        _shapex = 123
        _shapey = 435
        _xhigh = 23
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.set_param_value("roi_xhigh", _xhigh)
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_xhigh, _roi[1] - _roi[0])
        self.assertEqual(_shapey, _roi[3] - _roi[2])

    def test_get_modulated_roi__xhigh_set_negative(self):
        _shapex = 123
        _shapey = 435
        _xhigh = -32
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.set_param_value("roi_xhigh", _xhigh)
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_shapex + _xhigh + 1, _roi[1] - _roi[0])
        self.assertEqual(_shapey, _roi[3] - _roi[2])

    def test_get_modulated_roi__ylow_set(self):
        _shapex = 123
        _shapey = 435
        _ylow = 23
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.set_param_value("roi_ylow", _ylow)
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_shapex, _roi[1] - _roi[0])
        self.assertEqual(_shapey - _ylow, _roi[3] - _roi[2])

    def test_get_modulated_roi__yhigh_set_positive(self):
        _shapex = 123
        _shapey = 435
        _yhigh = 23
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.set_param_value("roi_yhigh", _yhigh)
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_shapex, _roi[1] - _roi[0])
        self.assertEqual(_yhigh, _roi[3] - _roi[2])

    def test_get_modulated_roi__yhigh_set_negative(self):
        _shapex = 123
        _shapey = 435
        _yhigh = -32
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.set_param_value("roi_yhigh", _yhigh)
        _roi = imm._ImageMetadataManager__get_modulated_roi()
        self.assertEqual(_shapex, _roi[1] - _roi[0])
        self.assertEqual(_shapey + _yhigh + 1, _roi[3] - _roi[2])

    def test_check_roi_for_consistency(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        imm.set_param_value("use_roi", True)
        imm._ImageMetadataManager__check_roi_for_consistency()

    def test_check_roi_for_consistency__wrong_range(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        imm.set_param_value("use_roi", True)
        imm.set_param_value("roi_xlow", 12)
        imm.set_param_value("roi_xhigh", 9)
        imm.set_param_value("roi_ylow", 12)
        imm.set_param_value("roi_yhigh", 9)
        with self.assertRaises(UserConfigError):
            imm._ImageMetadataManager__check_roi_for_consistency()

    def test_calculate_final_image_shape(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        imm.set_param_value("use_roi", False)
        imm.set_param_value("binning", 1)
        imm._calculate_final_image_shape()
        self.assertIsNone(imm.roi)
        self.assertEqual(imm.final_shape, self._img_shape)

    def test_calculate_final_image_shape__with_binning(self):
        _bin = 3
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        imm.set_param_value("use_roi", False)
        imm.set_param_value("binning", _bin)
        imm._calculate_final_image_shape()
        self.assertIsNone(imm.roi)
        _shape = (self._img_shape[0] // _bin, self._img_shape[1] // _bin)
        self.assertEqual(imm.final_shape, _shape)

    def test_calculate_final_image_shape__with_roi(self):
        _xlow = 7
        _xhigh = 17
        _ylow = 2
        _yhigh = 22
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        imm.set_param_value("use_roi", True)
        imm.set_param_value("roi_xlow", _xlow)
        imm.set_param_value("roi_xhigh", _xhigh)
        imm.set_param_value("roi_ylow", _ylow)
        imm.set_param_value("roi_yhigh", _yhigh)
        imm.set_param_value("binning", 1)
        imm._calculate_final_image_shape()
        self.assertEqual(imm.roi, (slice(_ylow, _yhigh), slice(_xlow, _xhigh)))
        self.assertEqual(imm.final_shape, (_yhigh - _ylow, _xhigh - _xlow))

    def test_calculate_final_image_shape__with_roi_and_binning(self):
        _xlow = 7
        _xhigh = 17
        _ylow = 2
        _yhigh = 22
        _bin = 3
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        imm.set_param_value("use_roi", True)
        imm.set_param_value("roi_xlow", _xlow)
        imm.set_param_value("roi_xhigh", _xhigh)
        imm.set_param_value("roi_ylow", _ylow)
        imm.set_param_value("roi_yhigh", _yhigh)
        imm.set_param_value("binning", _bin)
        imm._calculate_final_image_shape()
        self.assertEqual(imm.roi, (slice(_ylow, _yhigh), slice(_xlow, _xhigh)))
        self.assertEqual(
            imm.final_shape, ((_yhigh - _ylow) // _bin, (_xhigh - _xlow) // _bin)
        )

    def test_store_image_data(self):
        imm = ImageMetadataManager()
        imm.store_image_data(self._img_shape, self._data.dtype, self._dsize)
        self.assertEqual(imm._config["datatype"], self._data.dtype)
        self.assertEqual(imm._config["raw_img_shape_x"], self._img_shape[1])
        self.assertEqual(imm._config["raw_img_shape_y"], self._img_shape[0])
        self.assertEqual(imm._config["images_per_file"], self._dsize)

    def test_store_image_data_from_single_image(self):
        imm = ImageMetadataManager()
        imm.filename = self._fname(0)
        imm._store_image_data_from_single_image()
        self.assertEqual(imm._config["datatype"], self._data.dtype)
        self.assertEqual(imm._config["raw_img_shape_x"], self._img_shape[1])
        self.assertEqual(imm._config["raw_img_shape_y"], self._img_shape[0])
        self.assertEqual(imm._config["numbers"], [0])
        self.assertEqual(imm._config["images_per_file"], 1)

    def test_store_image_data_from_single_image__no_file(self):
        imm = ImageMetadataManager()
        with self.assertRaises(UserConfigError):
            imm.filename = self._fname(90)
        self.assertEqual(imm._config["datatype"], None)
        self.assertEqual(imm._config["raw_img_shape_x"], None)
        self.assertEqual(imm._config["raw_img_shape_y"], None)

    def test_verify_selection_range(self):
        _range = self._data.shape[0]
        _i0 = 12
        _i1 = 27
        imm = ImageMetadataManager()
        imm.set_param_value("hdf5_first_image_num", _i0)
        imm.set_param_value("hdf5_last_image_num", _i1)
        imm._ImageMetadataManager__verify_selection_range(_range)

    def test_verify_selection_range__negative_indices(self):
        _range = self._data.shape[0]
        _i0 = 12
        _i1 = -3
        imm = ImageMetadataManager()
        imm.set_param_value("hdf5_first_image_num", _i0)
        imm.set_param_value("hdf5_last_image_num", _i1)
        imm._ImageMetadataManager__verify_selection_range(_range)

    def test_verify_selection_range__no_selection(self):
        _range = self._data.shape[0]
        _i0 = 12
        _i1 = 9
        imm = ImageMetadataManager()
        imm.set_param_value("hdf5_first_image_num", _i0)
        imm.set_param_value("hdf5_last_image_num", _i1)
        with self.assertRaises(UserConfigError):
            imm._ImageMetadataManager__verify_selection_range(_range)

    def test_store_image_data_from_hdf5(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm._store_image_data_from_hdf5_file()
        self.assertEqual(imm._config["datatype"], self._data.dtype)
        self.assertEqual(imm._config["raw_img_shape_x"], self._img_shape[1])
        self.assertEqual(imm._config["raw_img_shape_y"], self._img_shape[0])
        self.assertEqual(imm._config["numbers"], range(self._dsize))
        self.assertEqual(imm._config["images_per_file"], self._dsize)

    def test_store_image_data_from_hdf5__slice_ax_1(self):
        imm = ImageMetadataManager(hdf5_slicing_axis=1)
        imm.filename = self._hdf5_fname
        imm._store_image_data_from_hdf5_file()
        self.assertEqual(imm._config["datatype"], self._data.dtype)
        self.assertEqual(imm._config["raw_img_shape_x"], self._img_shape[1])
        self.assertEqual(imm._config["raw_img_shape_y"], self._dsize)
        self.assertEqual(imm._config["numbers"], range(self._img_shape[0]))
        self.assertEqual(imm._config["images_per_file"], self._img_shape[0])

    def test_store_image_data_from_hdf5__wrong_key(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.set_param_value("hdf5_key", "foo/bar")
        with self.assertRaises(UserConfigError):
            imm._store_image_data_from_hdf5_file()

    def test_store_image_data_from_hdf5__with_stepping(self):
        _step = 3
        imm = ImageMetadataManager()
        imm.set_param_value("hdf5_stepping", _step)
        imm.filename = self._hdf5_fname
        imm._store_image_data_from_hdf5_file()
        self.assertEqual(imm._config["images_per_file"], self._dsize // _step + 1)
        self.assertEqual(imm._config["numbers"], range(0, self._dsize, _step))

    def test_update_final_image(self):
        _shapex = 123
        _shapey = 435
        imm = ImageMetadataManager()
        imm._config["raw_img_shape_x"] = _shapex
        imm._config["raw_img_shape_y"] = _shapey
        imm.update_final_image()
        # assert does not raise an Exception.

    def test_set_filename(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        self.assertEqual(imm._config["filename"], self._hdf5_fname)

    def test_update_input_data__hdf5_file(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        # assert does not raise an Exception

    def test_update_input_data__other_file(self):
        imm = ImageMetadataManager()
        imm.filename = self._fname(0)
        imm.update_input_data()
        # assert does not raise an Exception

    def test_update(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        self.assertEqual(imm._config["images_per_file"], self._dsize)
        self.assertEqual(imm._config["numbers"], range(self._dsize))

    def test_update__single_file(self):
        imm = ImageMetadataManager()
        imm.filename = self._fname(0)
        imm.update_input_data()
        self.assertEqual(imm._config["images_per_file"], 1)
        self.assertEqual(imm._config["numbers"], [0])

    def test_update__w_filename(self):
        imm = ImageMetadataManager()
        imm.update(filename=self._fname(0))
        self.assertEqual(imm._config["images_per_file"], 1)
        self.assertEqual(imm._config["numbers"], [0])

    def test_update__new_data(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update()
        self.create_second_dataset()
        imm.filename = self._hdf5_fname2
        imm.update()
        self.assertEqual(imm.final_shape, self._img_shape2)

    def test_update__new_data_with_roi(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.set_param_value("roi_xlow", 5)
        imm.update()
        self.create_second_dataset()
        imm.filename = self._hdf5_fname2
        imm.update()
        self.assertEqual(imm.final_shape, self._img_shape2)

    def test_creation_with_params(self):
        p = get_generic_parameter("binning")
        p.value = 4
        imm = ImageMetadataManager(p)
        self.assertIsInstance(imm, ImageMetadataManager)
        self.assertEqual(imm.get_param_value("binning"), 4)

    def test_external_param_manipulation(self):
        p = get_generic_parameter("binning")
        p.value = 4
        imm = ImageMetadataManager(p)
        p.value = 8
        self.assertEqual(imm.get_param_value("binning"), p.value)

    def test_property_sizex(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        self.assertEqual(imm.raw_size_x, self._img_shape[1])

    def test_property_sizey(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        self.assertEqual(imm.raw_size_y, self._img_shape[0])

    def test_property_numbers(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        _n = imm.numbers
        self.assertEqual(_n, range(self._dsize))

    def test_property_datatype(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        self.assertEqual(imm.datatype, self._data.dtype)

    def test_property_roi(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.set_param_value("use_roi", True)
        imm.update()
        self.assertEqual(
            imm.roi, (slice(0, self._img_shape[0]), slice(0, self._img_shape[1]))
        )

    def test_property_final_shape(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update()
        self.assertEqual(imm.final_shape, self._img_shape)

    def test_property_images_per_file(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update()
        self.assertEqual(imm.images_per_file, self._dsize)

    def test_property_hdf5_dset_shape(self):
        imm = ImageMetadataManager()
        imm.filename = self._hdf5_fname
        imm.update_input_data()
        self.assertEqual(imm.hdf5_dset_shape, (self._dsize,) + self._img_shape)


if __name__ == "__main__":
    unittest.main()
