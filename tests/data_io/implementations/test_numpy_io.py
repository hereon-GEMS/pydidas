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

"""Unit tests for pydidas.data_io.implementations.numpy_io module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from tests.data_io.implementations.test_io_base import IoBaseTests

from pydidas.core import FileReadError
from pydidas.core.constants import NUMPY_EXTENSIONS
from pydidas.data_io.implementations.numpy_io import NumpyIo


@pytest.fixture
def io_class():
    return NumpyIo


@pytest.fixture
def npy_file(tmp_path):
    _data = np.random.random((12, 13, 14, 15))
    _fname = tmp_path / "test.npy"
    np.save(_fname, _data)
    return _fname, _data


class TestNumpyIo(IoBaseTests):
    """Runs the generic IoBase tests against NumpyIo."""


def test_class_extensions():
    for _ext in NUMPY_EXTENSIONS:
        assert _ext in NumpyIo.extensions_export
        assert _ext in NumpyIo.extensions_import


def test_import_from_file__default(npy_file):
    _fname, _data = npy_file
    assert np.allclose(NumpyIo.import_from_file(_fname), _data)


def test_import_from_file__wrong_name(npy_file):
    _fname, _ = npy_file
    with pytest.raises(FileReadError):
        NumpyIo.import_from_file(_fname / "dummy", astype=np.float64)


def test_import_from_file__wrong_type(tmp_path):
    _fname = tmp_path / "test2.dat"
    _fname.write_text("now it's just an ASCII text file.")
    with pytest.raises(FileReadError):
        NumpyIo.import_from_file(_fname, astype=np.float64)


def test_export_to_file__file_exists(npy_file):
    _fname, _data = npy_file
    with pytest.raises(FileExistsError):
        NumpyIo.export_to_file(_fname, _data)


def test_export_to_file__file_exists_and_overwrite(tmp_path):
    _data = np.random.random((12, 13, 14, 15))
    _fname = tmp_path / "test_new.npy"
    NumpyIo.export_to_file(_fname, _data)
    NumpyIo.export_to_file(_fname, _data[:11], overwrite=True)
    assert NumpyIo.import_from_file(_fname).shape == (11,) + _data.shape[1:]


def test_export_to_file__simple(tmp_path):
    _data = np.random.random((12, 13, 14, 15))
    _fname = tmp_path / "test_fname.npy"
    NumpyIo.export_to_file(_fname, _data)
    assert np.allclose(NumpyIo.import_from_file(_fname), _data)


if __name__ == "__main__":
    pytest.main([__file__])
