# This file is part of pydidas.
#
# Copyright 025, Helmholtz-Zentrum Hereon
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

"""
Tests for the SubtractBackgroundImage plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import shutil
import tempfile
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas_plugins.proc_plugins.subtract_bg_image import SubtractBackgroundImage

from pydidas.core import Dataset, UserConfigError
from pydidas.data_io import export_data
from pydidas.plugins import ProcPlugin


_IMAGE = np.arange(400).reshape(20, 20)


@pytest.fixture(scope="module")
def temp_path():
    _path = Path(tempfile.mkdtemp())
    yield _path
    shutil.rmtree(_path)


def get_image_file(temp_path, filename, dtype, **kwargs) -> Path:
    fname = temp_path / filename
    kwargs["overwrite"] = True
    export_data(fname, _IMAGE.astype(dtype), **kwargs)
    return fname


def test_init():
    plugin = SubtractBackgroundImage()
    assert isinstance(plugin, ProcPlugin)
    assert plugin._bg_image is None
    assert plugin._thresh is None


@pytest.mark.parametrize("image_dtype", [float, np.float32, int, np.uint32])
@pytest.mark.parametrize("filename", ["image.npy", "image.tiff"])
def test_pre_execute__simple_input_files(
    temp_path,
    image_dtype,
    filename,
):
    plugin = SubtractBackgroundImage()
    image_file = get_image_file(temp_path, filename, image_dtype)
    plugin.set_param_value("bg_file", image_file)
    plugin.pre_execute()
    assert (
        plugin._bg_image.dtype == np.float32
        if image_dtype == np.float32
        else np.float64
    )
    assert plugin._bg_image.shape == _IMAGE.shape


@pytest.mark.parametrize("ax", [0, 1, 2])
@pytest.mark.parametrize("index", [0, 3])
@pytest.mark.parametrize("key", ["entry/data/data", "/test/data"])
def test_pre_execute__hdf5(temp_path, ax, key, index):
    plugin = SubtractBackgroundImage()
    _shape = list(_IMAGE.shape)
    _shape.insert(ax, 30)
    _tmp_data = np.random.random((_shape))
    _data_slice = (slice(None),) * ax + (index,) + (slice(None),) * (2 - ax)
    _tmp_data[_data_slice] = _IMAGE
    with h5py.File(temp_path / "test.h5", "w") as f:
        f[key] = _tmp_data
    plugin.set_param_value("bg_file", temp_path / "test.h5")
    plugin.set_param_value("bg_hdf5_key", key)
    plugin.set_param_value("bg_hdf5_frame", index)
    plugin.set_param_value("hdf5_slicing_axis", ax)
    plugin.pre_execute()
    assert np.allclose(plugin._bg_image, _IMAGE)


@pytest.mark.parametrize("multiplicator", [0.1, 1.0, 2.5])
@pytest.mark.parametrize("threshold", [None, np.inf, np.nan, -1, 0, 1.5])
@pytest.mark.parametrize("ROI", [[0, 20, 0, 20], [2, 14, 5, None]])
@pytest.mark.parametrize("use_roi", [True, False])
def test_pre_execute__outputs(temp_path, multiplicator, threshold, ROI, use_roi):
    plugin = SubtractBackgroundImage()
    image_file = get_image_file(temp_path, "image.npy", float)
    plugin.set_param_value("bg_file", image_file)
    plugin.set_param_value("multiplicator", multiplicator)
    plugin.set_param_value("threshold_low", threshold)
    plugin.set_param_value("roi_ylow", ROI[0])
    plugin.set_param_value("roi_yhigh", ROI[1])
    plugin.set_param_value("roi_xlow", ROI[2])
    plugin.set_param_value("roi_xhigh", ROI[3])
    plugin.set_param_value("use_roi", use_roi)
    plugin.pre_execute()
    _slicer = (slice(ROI[0], ROI[1]), slice(ROI[2], ROI[3])) if use_roi else None
    assert np.allclose(plugin._bg_image, multiplicator * _IMAGE[_slicer])
    if threshold in [None, np.inf, np.nan]:
        assert plugin._thresh is None
    else:
        assert plugin._thresh == threshold


@pytest.mark.parametrize("bg_image_dtype", [float, np.float32, int, np.uint32])
@pytest.mark.parametrize("data_dtype", [float, np.float32, np.uint16, np.int32])
@pytest.mark.parametrize("multiplicator", [0.1, 1.0, 2.5])
@pytest.mark.parametrize("threshold", [None, -1, 0, 1.5])
def test_execute(temp_path, bg_image_dtype, data_dtype, multiplicator, threshold):
    plugin = SubtractBackgroundImage()
    image_file = get_image_file(temp_path, "test.npy", bg_image_dtype)
    plugin.set_param_value("bg_file", image_file)
    plugin.set_param_value("multiplicator", multiplicator)
    plugin.set_param_value("threshold_low", threshold)
    plugin.pre_execute()
    _data = np.ones(_IMAGE.shape, dtype=data_dtype) * 400
    _res, _kws = plugin.execute(_data)
    _ref = _data - multiplicator * _IMAGE
    if threshold is not None:
        _ref = np.where(_ref < threshold, threshold, _ref)
    assert np.allclose(_res, _ref)
    assert _data.dtype == np.float32 if data_dtype == np.float32 else np.float64


def test_execute__w_invalid_shape(temp_path):
    plugin = SubtractBackgroundImage()
    image_file = get_image_file(temp_path, "test.npy", float)
    plugin.set_param_value("bg_file", image_file)
    _data = Dataset(np.arange(2000, dtype=float)).reshape(50, 40)
    plugin.pre_execute()
    with pytest.raises(UserConfigError):
        plugin.execute(_data)


if __name__ == "__main__":
    pytest.main()
