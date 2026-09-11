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

"""Unit tests for pydidas.data_io.implementations.raw_io module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from tests.data_io.implementations.test_io_base import IoBaseTests

from pydidas.core import FileReadError, UserConfigError
from pydidas.core.constants import BINARY_EXTENSIONS
from pydidas.data_io.implementations.raw_io import RawIo


_DATA_SHAPE = (12, 13, 14)
_READ_KWS = {"datatype": np.float64, "shape": _DATA_SHAPE}


@pytest.fixture
def io_class():
    return RawIo


@pytest.fixture
def raw_file(tmp_path):
    _data = np.random.random(_DATA_SHAPE)
    _fname = tmp_path / "test.dat"
    _data.tofile(_fname)
    return _fname, _data


class TestRawIo(IoBaseTests):
    """Runs the generic IoBase tests against RawIo."""


def test_class_extensions():
    for _ext in BINARY_EXTENSIONS:
        assert _ext in RawIo.extensions_export
        assert _ext in RawIo.extensions_import


def test_import_from_file__default(raw_file):
    _fname, _data = raw_file
    assert np.allclose(RawIo.import_from_file(_fname, **_READ_KWS), _data)


def test_import_from_file__shape_missing(raw_file):
    _fname, _data = raw_file
    with pytest.raises(UserConfigError, match="The shape must be specified"):
        RawIo.import_from_file(_fname, datatype=np.float16)


def test_import_from_file__datatype_missing(raw_file):
    _fname, _data = raw_file
    with pytest.raises(UserConfigError, match="The datatype must be specified"):
        RawIo.import_from_file(_fname, shape=_DATA_SHAPE)


def test_import_from_file__wrong_name(raw_file):
    _fname, _ = raw_file
    with pytest.raises(FileReadError):
        RawIo.import_from_file(_fname / "dummy", datatype=np.float64, shape=_DATA_SHAPE)


def test_import_from_file__wrong_type(tmp_path):
    _fname = tmp_path / "test2.dat"
    _fname.write_text("now it's just an ASCII text file.")
    with pytest.raises(FileReadError):
        RawIo.import_from_file(_fname, datatype=np.float64, shape=_DATA_SHAPE)


def test_export_to_file__file_exists(raw_file):
    _fname, _data = raw_file
    with pytest.raises(FileExistsError):
        RawIo.export_to_file(_fname, _data)


def test_export_to_file__file_exists_and_overwrite(tmp_path, raw_file):
    _fname_orig, _data = raw_file
    _fname = tmp_path / "test_overwrite.bin"
    RawIo.export_to_file(_fname, _data[:11])
    RawIo.export_to_file(_fname, _data, overwrite=True)
    assert RawIo.import_from_file(_fname, **_READ_KWS).shape == _DATA_SHAPE


def test_export_to_file__simple(tmp_path):
    _data = np.random.random(_DATA_SHAPE)
    _fname = tmp_path / "test_simple.bin"
    RawIo.export_to_file(_fname, _data)
    assert np.allclose(RawIo.import_from_file(_fname, **_READ_KWS), _data)


if __name__ == "__main__":
    pytest.main([__file__])
