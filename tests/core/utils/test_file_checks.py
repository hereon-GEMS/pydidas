# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import shutil
import tempfile
from pathlib import Path

import h5py
import numpy as np
import pytest

from pydidas.core import FileReadError, UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS, NUMPY_EXTENSIONS
from pydidas.core.utils.file_checks import (
    verify_file_exists,
    verify_file_exists_and_extension_matches,
    verify_filenames_have_same_parent,
    verify_files_of_range_are_same_size,
)


@pytest.fixture
def temp_files():
    """Create temporary test files and directories."""
    path = Path(tempfile.mkdtemp())
    no_fname = path / "no_file.test"
    hdf5_fname = path / "test01.h5"
    with h5py.File(hdf5_fname, "w") as _file:
        _file["test/path/data"] = [1, 2, 3, 4, 5]
    npy_fname = path / "test.npy"
    np.save(npy_fname, np.array([1, 2, 3]))
    yield {
        "dir": path,
        "no_file": no_fname,
        "npy_fname": npy_fname,
        "hdf5_fname": hdf5_fname,
    }
    shutil.rmtree(path)


@pytest.mark.parametrize("name", ["hdf5_fname", "npy_fname"])
def test_check_file_exists(temp_files, name):
    assert verify_file_exists(temp_files[name])


@pytest.mark.parametrize("name", ["dir", "no_file"])
def test_verify_file_exists_dir_illegal_choice(temp_files, name):
    with pytest.raises(UserConfigError):
        verify_file_exists(temp_files[name])


@pytest.mark.parametrize("name1_type", [str, Path])
@pytest.mark.parametrize("name2", ["test.txt", Path("test.txt"), "::hdf5_fname"])
def test_verify_filenames_have_same_parent(temp_files, name1_type, name2):
    _name1 = name1_type(temp_files["npy_fname"])
    if isinstance(name2, str) and name2.startswith("::"):
        name2 = temp_files[name2[2:]]
    verify_filenames_have_same_parent(_name1, name2)


@pytest.mark.parametrize("name", ["npy_fname", "hdf5_fname"])
@pytest.mark.parametrize("str_exts", [True, False])
def test_verify_file_exists_and_extension_matches(temp_files, name, str_exts):
    _exts = NUMPY_EXTENSIONS if name.startswith("npy") else HDF5_EXTENSIONS
    if str_exts:
        _exts = ";;".join(_exts)
    verify_file_exists_and_extension_matches(temp_files[name], _exts)


@pytest.mark.parametrize("name", ["hdf5_fname", "no_file"])
@pytest.mark.parametrize("str_exts", [True, False])
def test_verify_file_exists_and_extension_matches__false(temp_files, name, str_exts):
    _exts = ";;".join(NUMPY_EXTENSIONS) if str_exts else NUMPY_EXTENSIONS
    with pytest.raises(FileReadError):
        verify_file_exists_and_extension_matches(temp_files[name], _exts)


@pytest.mark.parametrize("name1_type", [str, Path])
@pytest.mark.parametrize("name2", ["::dir", Path("some/file.txt"), "some/file.txt"])
def test_verify_filenames_have_same_parent_false(temp_files, name1_type, name2):
    _name1 = name1_type(temp_files["npy_fname"])
    if isinstance(name2, str) and name2.startswith("::"):
        name2 = temp_files[name2[2:]]
    with pytest.raises(UserConfigError):
        verify_filenames_have_same_parent(_name1, name2)


def test_verify_files_of_range_are_same_size_correct(temp_files):
    _data = np.random.random((10, 10))
    _fnames = [f"test{i:02d}.npy" for i in range(10)]
    for _name in _fnames:
        np.save(temp_files["dir"] / _name, _data)
    verify_files_of_range_are_same_size(
        [temp_files["dir"] / _name for _name in _fnames]
    )


def test_verify_files_of_range_are_same_size_wrong(temp_files):
    _data = np.random.random((10, 10))
    _fnames = [f"test{i:02d}.npy" for i in range(10)]
    for i, _name in enumerate(_fnames):
        np.save(temp_files["dir"] / _name, _data[:i, :i])
    with pytest.raises(UserConfigError):
        verify_files_of_range_are_same_size(
            [temp_files["dir"] / _name for _name in _fnames]
        )


if __name__ == "__main__":
    pytest.main([__file__])
