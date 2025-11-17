# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import multiprocessing as mp
import os
import random
import time
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.apps.directory_spy_app import DirectorySpyApp
from pydidas.core import FileReadError, UserConfigError, get_generic_parameter
from pydidas.core.utils import get_random_string


_FNAME_PATTERN = "test_12345_#####_suffix.npy"
_FNAME_GLOB_STR = _FNAME_PATTERN.replace("#####", "*")
_IMG_SHAPE = (20, 20)
_SHARE_SHAPE = (100, 100)


def _glob_pattern(path: os.PathLike) -> str:
    _full_path = os.path.join(str(path), _FNAME_PATTERN)
    return _full_path.replace("#####", "*")


def random_image(shape=None):
    if shape is None:
        shape = _IMG_SHAPE
    return np.random.random(shape)


def create_pattern_files(path: Path, pattern=None, n=20) -> list[Path]:
    pattern = pattern or _FNAME_PATTERN
    _len_pattern = pattern.count("#")
    pattern = pattern.replace("#" * _len_pattern, "{:0" + str(_len_pattern) + "d}")
    _names = []
    for _index in range(n):
        _data = np.random.random(_IMG_SHAPE)
        _fpath = path / pattern.format(_index)
        np.save(_fpath, _data)
        _names.append(str(_fpath))
        time.sleep(0.005)
    return _names


def create_hdf5_image(path: Path):
    _fname = path / _FNAME_PATTERN.replace("#####", "00000").replace("npy", "h5")
    _dset = "/entry/nodata/data"
    _n = 42
    _data = np.zeros((_n,) + _IMG_SHAPE)
    with h5py.File(_fname, "w") as f:
        f[_dset] = _data
    return _fname, _dset, _data.shape


@pytest.fixture(scope="module")
def mask() -> np.ndarray:
    return np.asarray(
        [random.choice([True, False]) for _ in range(_IMG_SHAPE[0] * _IMG_SHAPE[1])]
    ).reshape(_IMG_SHAPE)


@pytest.fixture
def app(empty_temp_path):
    app = DirectorySpyApp(image_size=_SHARE_SHAPE)
    app.set_param_value("scan_for_all", False)
    app.set_param_value("directory_path", empty_temp_path)
    app.set_param_value("use_detector_mask", False)
    app.set_param_value("filename_pattern", _FNAME_PATTERN)
    app.prepare_run()
    app._det_mask = np.zeros(_IMG_SHAPE)
    yield app
    del app


@pytest.fixture
def mask_file(mask, empty_temp_path):
    _mask_fname = empty_temp_path / "mask.npy"
    np.save(_mask_fname, mask)
    return _mask_fname


@pytest.fixture
def dummy_parse_func():
    original = DirectorySpyApp.parse_func
    DirectorySpyApp.parse_func = lambda x: {"scan_for_all": True}
    yield
    DirectorySpyApp.parse_func = original


def test_creation():
    app = DirectorySpyApp()
    assert isinstance(app, DirectorySpyApp)
    assert app._DirectorySpyApp__image_size == DirectorySpyApp.AVAILABLE_IMAGE_SIZE


def test_creation_with_args():
    _scan_for_all = get_generic_parameter("scan_for_all")
    _scan_for_all.value = True
    app = DirectorySpyApp(_scan_for_all)
    assert app.get_param_value("scan_for_all")


def test_creation_with_cmdargs(dummy_parse_func):
    app = DirectorySpyApp()
    assert app.get_param_value("scan_for_all")


def test_reset_runtime_vars(app):
    app._shared_array = 42
    app._index = np.pi
    app.reset_runtime_vars()
    assert app._shared_array is None
    assert app._index == -1


def test_apply_mask__no_mask(app):
    _image = random_image()
    _new_image = app._apply_mask(_image)
    assert np.allclose(_image, _new_image)


def test_apply_mask__with_mask(app, mask):
    _val = 42
    app._det_mask = mask
    app.set_param_value("detector_mask_val", _val)
    _image = random_image()
    _new_image = app._apply_mask(_image)
    assert np.allclose(_new_image[mask], _val)


def test_get_detector_mask__no_mask(app):
    app.set_param_value("use_detector_mask", False)
    _mask = app._get_detector_mask()
    assert _mask is None


def test_get_detector_mask__with_mask(app, mask, mask_file):
    app.set_param_value("use_detector_mask", True)
    app.set_param_value("detector_mask_file", mask_file)
    _mask = app._get_detector_mask()
    assert np.allclose(_mask, mask)


def test_define_path_and_name__scan_for_all(empty_temp_path, app):
    app.set_param_value("scan_for_all", True)
    app.set_param_value("filename_pattern", "")
    app.define_path_and_name()
    assert empty_temp_path == Path(app._config["path"])
    assert app._fname(0) == ""


@pytest.mark.parametrize("missing_indices", [[3, 7], [0, 1, 2, 3], []])
def test_find_current_index__missing_inbetween(empty_temp_path, app, missing_indices):
    _num = 21
    _names = create_pattern_files(empty_temp_path, n=_num)
    for _index in missing_indices:
        os.remove(_names[_index])
    app._config["path"] = str(empty_temp_path)
    app._config["glob_pattern"] = _FNAME_GLOB_STR
    app._DirectorySpyApp__find_current_index()
    assert app._index == _num - 1


def test_find_current_index__empty(empty_temp_path, app):
    app._index = None
    app._config["path"] = str(empty_temp_path)
    app._config["glob_pattern"] = "*"
    app._DirectorySpyApp__find_current_index()
    assert app._index == -1


def test_find_latest_file_of_pattern__empty(empty_temp_path, app):
    app.define_path_and_name()
    _check_result = app._DirectorySpyApp__check_for_new_file_of_pattern()
    assert app._config["latest_file"] is None
    assert app._config["2nd_latest_file"] is None
    assert not _check_result


@pytest.mark.parametrize("n_files, start_n", [(1, 0), (20, 0), (20, 5)])
def test_find_latest_file_of_pattern_w_files(empty_temp_path, app, n_files, start_n):
    app.define_path_and_name()
    _names = create_pattern_files(empty_temp_path, n=n_files)
    for _ in range(start_n):
        _name = _names.pop(0)
        os.remove(_name)
    _check_result = app._DirectorySpyApp__check_for_new_file_of_pattern()
    assert app._config["latest_file"] == _names[-1]
    if n_files == 1:
        assert app._config["2nd_latest_file"] is None
    else:
        assert app._config["2nd_latest_file"] == _names[-2]
    assert _check_result


def test_find_latest_file_of_pattern__repeated_calls(empty_temp_path, app):
    app.define_path_and_name()
    _names = create_pattern_files(empty_temp_path, n=12)
    _check_result = app._DirectorySpyApp__check_for_new_file_of_pattern()
    assert _check_result
    _check_result = app._DirectorySpyApp__check_for_new_file_of_pattern()
    assert not _check_result
    # modify the latest file and check that it is detected as new:
    with open(_names[-1], "w") as f:
        f.write("other content")
    _check_result = app._DirectorySpyApp__check_for_new_file_of_pattern()
    assert _check_result


def test_find_latest_file_of_pattern__missing_file(empty_temp_path, app):
    app.define_path_and_name()
    _names = create_pattern_files(empty_temp_path, n=20)
    _index = 12
    os.remove(_names[_index])
    app.define_path_and_name()
    app._DirectorySpyApp__check_for_new_file_of_pattern()
    assert app._config["latest_file"] == _names[_index - 1]
    assert app._config["2nd_latest_file"] == _names[_index - 2]


@pytest.mark.parametrize("w_dirs", [True, False])
def test_find_latest_file__empty(empty_temp_path, app, w_dirs):
    if w_dirs:
        (empty_temp_path / "dir1").mkdir()
        (empty_temp_path / "dir2").mkdir()
    app.define_path_and_name()
    _check_result = app._DirectorySpyApp__check_for_new_file()
    assert app._config["latest_file"] is None
    assert app._config["2nd_latest_file"] is None
    assert not _check_result


@pytest.mark.parametrize("n_files", [1, 20])
def test_find_latest_file__w_files(empty_temp_path, app, n_files):
    _names = create_pattern_files(empty_temp_path, n=n_files)
    app.define_path_and_name()
    _check_result = app._DirectorySpyApp__check_for_new_file()
    assert app._config["latest_file"] == _names[n_files - 1]
    if n_files == 1:
        assert app._config["2nd_latest_file"] is None
    else:
        assert app._config["2nd_latest_file"] == _names[-2]
    assert _check_result
    # check that a second call returns False:
    _check_result = app._DirectorySpyApp__check_for_new_file()
    assert not _check_result


def test_initialize_shared_memory(app):
    app.initialize_shared_memory()
    for _key in ["flag", "width", "height"]:
        assert isinstance(
            app._config["shared_memory"][_key], mp.sharedctypes.Synchronized
        )
    assert isinstance(
        app._config["shared_memory"]["array"], mp.sharedctypes.SynchronizedArray
    )


def test_initialize_arrays_from_shared_memory(app):
    app.initialize_shared_memory()
    app._DirectorySpyApp__initialize_array_from_shared_memory()
    assert isinstance(app._shared_array, np.ndarray)
    assert app._shared_array.shape == _SHARE_SHAPE


def test_load_bg_file__simple(empty_temp_path, app):
    _fname = create_pattern_files(empty_temp_path, n=1)[0]
    _data = np.load(_fname)
    app.set_param_value("bg_file", _fname)
    app._load_bg_file()
    assert np.allclose(_data, app._bg_image)


def test_load_bg_file__no_such_file(empty_temp_path, app):
    app.set_param_value("bg_file", empty_temp_path / "no_such_file.npy")
    with pytest.raises(UserConfigError):
        app._load_bg_file()


def test_load_bg_file__hdf5file(empty_temp_path, app):
    _fname = empty_temp_path / "hdf5_bg_file.h5"
    _data = random_image()
    _dset = "entry/other/bg/data"
    with h5py.File(_fname, "w") as f:
        f[_dset] = _data[None, :, :]
    app = DirectorySpyApp()
    app.set_param_value("bg_file", _fname)
    app.set_param_value("bg_hdf5_key", _dset)
    app._load_bg_file()
    assert np.allclose(_data, app._bg_image)


def test_load_bg_file__wrong_shape(empty_temp_path, app):
    _fname = empty_temp_path / "3d_bg_file.np"
    np.save(_fname, np.zeros((10, 10, 10)))
    app.set_param_value("bg_file", _fname)
    with pytest.raises(UserConfigError):
        app._load_bg_file()


def test_define_path_and_name__with_scan_for_all(empty_temp_path, app):
    app.set_param_value("scan_for_all", True)
    app.define_path_and_name()
    assert app._config["path"] == str(empty_temp_path)


def test_define_path_and_name__with_pattern_no_wildcard(empty_temp_path, app):
    _pattern = empty_temp_path / "names_with_no_pattern123.tif"
    app.set_param_value("filename_pattern", _pattern)
    with pytest.raises(UserConfigError):
        app.define_path_and_name()


def test_define_path_and_name__with_pattern_multiple_wildcard(empty_temp_path, app):
    _pattern = empty_temp_path / "names_with_###_patterns_###.tif"
    app.set_param_value("filename_pattern", _pattern)
    with pytest.raises(UserConfigError):
        app.define_path_and_name()


def test_define_path_and_name__with_pattern_correct(empty_temp_path, app):
    _pattern = str(app.get_param_value("filename_pattern"))
    app.define_path_and_name()
    assert app._config["glob_pattern"] == _pattern.replace("#####", "*")
    assert app._fname(42) == os.path.join(app._config["path"], _pattern).replace(
        "#####", "00042"
    )
    assert app._config["path"] == str(empty_temp_path)


def test_multiprocessing_carryon(app):
    app.prepare_run()
    assert not app.multiprocessing_carryon()


def test_prepare_run__master(empty_temp_path, app):
    app.prepare_run()
    assert app._fname(42) != ""
    assert app._config["path"] == str(empty_temp_path)
    assert isinstance(app._shared_array, np.ndarray)
    assert app._shared_array.shape == _SHARE_SHAPE


def test_prepare_run__as_clone(app):
    app.prepare_run()
    app_clone = app.copy(clone_mode=True)
    app_clone.prepare_run()
    for _key in ["flag", "width", "height", "array"]:
        assert (
            app._config["shared_memory"][_key]
            == app_clone._config["shared_memory"][_key]
        )


def test_multiprocessing_pre_run(empty_temp_path, app):
    app.multiprocessing_pre_run()
    # these tests are the same as for the prepare_run method:
    assert app._fname(42) != ""
    assert app._config["path"] == str(empty_temp_path)
    assert isinstance(app._shared_array, np.ndarray)
    assert app._shared_array.shape == _SHARE_SHAPE


def test_multiprocessing_post_run(app):
    app.multiprocessing_post_run()
    # assert does not raise an Exception


def test_multiprocessing_get_tasks(app):
    assert app.multiprocessing_get_tasks() == []


def test_multiprocessing_pre_cycle(app):
    app.multiprocessing_pre_cycle(0)
    # assert does not raise an Exception


def test_update_hdf5_metadata(empty_temp_path, app):
    _fname, _dset, _shape = create_hdf5_image(empty_temp_path)
    app.set_param_value("hdf5_key", _dset)
    app._DirectorySpyApp__update_hdf5_metadata(_fname)
    _meta = app._DirectorySpyApp__read_image_meta
    assert _meta["indices"] == (_shape[0] - 1,)
    assert _meta["dataset"] == _dset


@pytest.mark.parametrize("axis", [1, 2, None])
def test_update_hdf5_metadata__w_slice_ax(empty_temp_path, app, axis):
    _fname, _dset, _shape = create_hdf5_image(empty_temp_path)
    app.set_param_value("hdf5_key", _dset)
    app.set_param_value("hdf5_slicing_axis", axis)
    app._DirectorySpyApp__update_hdf5_metadata(_fname)
    _meta = app._DirectorySpyApp__read_image_meta
    _indices_ref = None if axis is None else (None,) * axis + (_shape[1] - 1,)
    assert _meta["indices"] == _indices_ref
    assert _meta["dataset"] == _dset


def test_get_image__simple_image(empty_temp_path, app):
    _fname = create_pattern_files(empty_temp_path, n=1)[0]
    _data = np.load(_fname)
    _image = app.get_image(_fname)
    assert np.allclose(_data, _image)


def test_get_image__high_dim_image(empty_temp_path, app):
    _fname = create_pattern_files(empty_temp_path, n=1)[0]
    np.save(_fname, np.zeros((10, 10, 10)))
    with pytest.raises(UserConfigError):
        app.get_image(_fname)


def test_get_image__hdf5_image(empty_temp_path, app):
    _fname, _dset, _shape = create_hdf5_image(empty_temp_path)
    app.set_param_value("hdf5_key", _dset)
    with h5py.File(_fname, "r") as f:
        _data = f[_dset][()]
    _image = app.get_image(_fname)
    assert np.allclose(_data[-1], _image)


def test_store_image_in_shared_memory(app):
    app.prepare_run()
    _height, _width = 42, 27
    _image = np.random.random((_height, _width))
    app._DirectorySpyApp__store_image_in_shared_memory(_image)
    assert app._config["shared_memory"]["width"].value == _width
    assert app._config["shared_memory"]["height"].value == _height
    assert np.allclose(app._shared_array[:_height, :_width], _image)


def test_multiprocessing_func__no_files(app):
    with pytest.raises(UserConfigError):
        app.multiprocessing_func(None)


@pytest.mark.parametrize("unreadable", [[], [1], [0, 1]])
def test_multiprocessing_func(empty_temp_path, app, unreadable):
    _names = create_pattern_files(empty_temp_path, n=2)
    app._config["latest_file"] = _names[1]
    app._config["2nd_latest_file"] = _names[0]
    for _i in unreadable:
        with open(_names[_i], "w") as f:
            f.write("no image file")
    if unreadable == [0, 1]:
        with pytest.raises(FileReadError):
            app.multiprocessing_func(None)
    else:
        _iref = 0 if 1 in unreadable else 1
        _index, _fname = app.multiprocessing_func(None)
        assert _fname == _names[_iref]
        assert app._config["shared_memory"]["width"].value == _IMG_SHAPE[1]
        assert app._config["shared_memory"]["height"].value == _IMG_SHAPE[0]
        assert np.allclose(
            app._shared_array[: _IMG_SHAPE[0], : _IMG_SHAPE[1]],
            np.load(_names[_iref]),
        )


def test_multiprocessing_func__with_mask(empty_temp_path, app, mask_file, mask):
    _names = create_pattern_files(empty_temp_path, n=2)
    _mask_val = 42.1
    app.set_param_value("use_detector_mask", True)
    app.set_param_value("detector_mask_file", mask_file)
    app.set_param_value("detector_mask_val", _mask_val)
    app.prepare_run()
    app._config["latest_file"] = _names[1]
    _index, _fname = app.multiprocessing_func(None)
    _arr = app._shared_array[: _IMG_SHAPE[0], : _IMG_SHAPE[1]]
    assert np.allclose(_arr[mask], _mask_val)


def test_multiprocessing_func__with_bg_file(empty_temp_path, app):
    _bg = np.ones(_IMG_SHAPE)
    _bg_fname = empty_temp_path / "bg.npy"
    np.save(_bg_fname, _bg)
    _names = create_pattern_files(empty_temp_path, n=2)
    app.set_param_value("use_bg_file", True)
    app.set_param_value("use_detector_mask", False)
    app.set_param_value("bg_file", _bg_fname)
    app._config["latest_file"] = _names[1]
    app.prepare_run()
    _ref = np.load(_names[1]) - _bg
    _index, _fname = app.multiprocessing_func(None)
    _arr = app._shared_array[: _IMG_SHAPE[0], : _IMG_SHAPE[1]]
    assert np.allclose(_arr, _ref)


def test_multiprocessing_store_results(empty_temp_path, app):
    _names = create_pattern_files(empty_temp_path, n=2)
    app._config["latest_file"] = _names[1]
    app._config["2nd_latest_file"] = _names[0]
    _index, _fname = app.multiprocessing_func(None)
    app.multiprocessing_store_results(_index, _fname)
    assert np.allclose(app._DirectorySpyApp__current_image, np.load(_names[1]))
    assert app._DirectorySpyApp__current_fname == _names[1]


def test_image_property(app):
    _data = np.random.random(_IMG_SHAPE)
    app._DirectorySpyApp__current_image = _data
    assert np.allclose(app.image, _data)


def test_filename_property(app):
    _name = get_random_string(12)
    app._DirectorySpyApp__current_fname = _name
    assert _name == app.filename


if __name__ == "__main__":
    pytest.main()
