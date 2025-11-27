# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with pydidas unittests
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.core import Parameter, UserConfigError
from pydidas.core.constants import (
    ASCII_IMPORT_EXTENSIONS,
    BINARY_EXTENSIONS,
    HDF5_EXTENSIONS,
    NUMPY_EXTENSIONS,
    TIFF_EXTENSIONS,
)
from pydidas.core.generic_parameters import get_generic_parameter
from pydidas.core.utils.associated_file_mixin import AssociatedFileMixin


_EXTENSIONS = (
    HDF5_EXTENSIONS
    + NUMPY_EXTENSIONS
    + BINARY_EXTENSIONS
    + ASCII_IMPORT_EXTENSIONS
    + TIFF_EXTENSIONS
)

_FILENAMES = ["ascii_file.txt", "npy_file.npy", "hdf5_file.h5", "binary_file.bin"]


@pytest.fixture(scope="module")
def path_w_data_files(temp_path):
    _path = temp_path / "associated_file_mixin"
    _path.mkdir()
    with open(_path / "ascii_file.txt", "w") as f:
        f.write("1 2")
    np.save(_path / "npy_file.npy", np.arange(10))
    with h5py.File(_path / "hdf5_file.h5", "w") as f:
        f["/entry/data/data"] = np.random.random((10, 15))
    np.arange(10).tofile(_path / "binary_file.bin")
    yield _path


@pytest.mark.parametrize("use_filename", [True, False])
@pytest.mark.parametrize("use_param", [True, False])
def test__creation(temp_path, use_filename, use_param):
    kwargs = {}
    if use_filename:
        kwargs["filename"] = temp_path / "testfile.txt"
    if use_param:
        kwargs["filename_param"] = get_generic_parameter("filename")
    obj = AssociatedFileMixin(**kwargs)
    assert isinstance(obj, AssociatedFileMixin)
    assert isinstance(obj._filename_param, Parameter)
    assert isinstance(obj._filetype, str)
    if use_filename and use_param:
        assert obj._filename_param.value == temp_path / "testfile.txt"
        assert kwargs["filename_param"].value == temp_path / "testfile.txt"


@pytest.mark.parametrize("extension", _EXTENSIONS)
def test__file_type_properties(path_w_data_files, extension):
    obj = AssociatedFileMixin()
    obj.current_filename = path_w_data_files / f"testfile.{extension}"
    assert obj.hdf5_file == (extension in HDF5_EXTENSIONS)
    assert obj.binary_file == (extension in BINARY_EXTENSIONS)
    assert obj.ascii_file == (extension in ASCII_IMPORT_EXTENSIONS)
    assert obj.generic_file == (
        extension not in (HDF5_EXTENSIONS + BINARY_EXTENSIONS + ASCII_IMPORT_EXTENSIONS)
    )


@pytest.mark.parametrize("property_name", ["filename", "filepath"])
def test_current_file_properties(path_w_data_files, property_name):
    obj = AssociatedFileMixin()
    _new_path = path_w_data_files / "testfile.txt"
    if property_name == "filename":
        obj.current_filename = _new_path
    elif property_name == "filepath":
        obj.current_filepath = _new_path
    assert obj._filename_param.value == _new_path
    assert isinstance(obj.current_filepath, Path)
    assert isinstance(obj.current_filename, str)
    assert obj.current_filepath == _new_path
    assert obj.current_filename == str(_new_path)


@pytest.mark.parametrize("value", [12, (Path("some_path"),), 5.5, [1, 2, 3]])
def test_current_filename_invalid_type(path_w_data_files, value):
    obj = AssociatedFileMixin()
    with pytest.raises(UserConfigError):
        obj.current_filename = value


@pytest.mark.parametrize("filename", _FILENAMES)
def test_current_filename_is_valid(path_w_data_files, filename):
    obj = AssociatedFileMixin()
    obj.current_filename = path_w_data_files / filename
    assert obj.current_filename_is_valid
    obj.current_filename = path_w_data_files / "subfolder" / filename
    assert not obj.current_filename_is_valid


def test__with_directory_instead_of_file(path_w_data_files):
    obj = AssociatedFileMixin()
    obj.current_filename = path_w_data_files
    assert not obj.current_filename_is_valid
    assert obj.generic_file


def test__with_empty_value():
    obj = AssociatedFileMixin()
    obj.current_filename = ""
    assert not obj.current_filename_is_valid
    assert obj.generic_file


def test__w_associated_parameter_and_external_change(path_w_data_files):
    param = get_generic_parameter("filename")
    obj = AssociatedFileMixin(filename_param=param)
    new_path = path_w_data_files / "ascii_file.txt"
    param.value = new_path
    assert obj.current_filename == str(new_path)
    assert obj.ascii_file


if __name__ == "__main__":
    pytest.main([])
