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
#
# Parts of this file have been created using AI tools.

"""Unit tests for pydidas.data_io.implementations.io_base module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.core import FileReadError
from pydidas.data_io.implementations import IoBase


@pytest.fixture
def io_class():
    return IoBase


class IoBaseTests:
    """
    Generic test class for shared IoBase functionality.

    Concrete IoBase subclass test suites can inherit from this class to run
    all generic tests against their implementation. Redefine the module-level
    ``io_class`` fixture in the subclass test module to provide the class
    under test.
    """

    def test_return_data__no_data(self, io_class):
        with pytest.raises(ValueError):
            io_class.return_data(None)

    def test_return_data__plain(self, io_class):
        _input = np.random.random((10, 10))
        _data = io_class.return_data(_input)
        assert (_input == _data).all()

    def test_return_data__with_roi(self, io_class):
        _roi = [2, 8, 2, 8]
        _input = np.random.random((10, 10))
        _expected = _input[2:8, 2:8].copy()
        _data = io_class.return_data(_input, roi=_roi)
        assert (_expected == _data).all()

    def test_return_data__with_return_type(self, io_class):
        _input = np.random.random((10, 10))
        _data = io_class.return_data(_input, astype=np.float32)
        assert _data.dtype == np.float32

    def test_return_data__with_binning(self, io_class):
        _input = np.random.random((10, 10))
        _data = io_class.return_data(_input, binning=2)
        assert _data.shape == (5, 5)

    def test_get_data_range__no_bounds(self, io_class):
        _data = np.random.random((15, 15))
        _range = io_class.get_data_range(_data)
        assert _range[0] == np.amin(_data)
        assert _range[1] == np.amax(_data)

    @pytest.mark.parametrize(
        "data_range,expected_min,expected_max",
        [
            ((0.4, None), 0.4, None),
            ((None, 0.8), None, 0.8),
            ((0.3, 0.8), 0.3, 0.8),
        ],
    )
    def test_get_data_range__with_bounds(
        self, io_class, data_range, expected_min, expected_max
    ):
        _data = np.random.random((15, 15))
        _range = io_class.get_data_range(_data, data_range=data_range)
        assert _range[0] == (
            expected_min if expected_min is not None else np.amin(_data)
        )
        assert _range[1] == (
            expected_max if expected_max is not None else np.amax(_data)
        )


class TestIoBase(IoBaseTests):
    """Runs the generic IoBase tests against IoBase itself."""


# ------------------------------------------------------------------
# IoBase-specific tests (abstract interface)
# ------------------------------------------------------------------


def test_export_to_file__raises_not_implemented():
    with pytest.raises(NotImplementedError):
        IoBase.export_to_file("", None)


def test_import_from_file__raises_not_implemented():
    with pytest.raises(NotImplementedError):
        IoBase.import_from_file("")


# ------------------------------------------------------------------
# raise_filereaderror_from_exception
# ------------------------------------------------------------------


def test_raise_filereaderror_from_exception__raises_file_read_error():
    _ex = RuntimeError("Something went wrong")
    with pytest.raises(FileReadError):
        IoBase.raise_filereaderror_from_exception(_ex, "file.txt")


def test_raise_filereaderror_from_exception__short_filename_not_truncated():
    _ex = RuntimeError("Some error")
    _fname = "short_file.txt"
    with pytest.raises(FileReadError) as exc_info:
        IoBase.raise_filereaderror_from_exception(_ex, _fname)
    assert _fname in str(exc_info.value)
    assert "[...]" not in str(exc_info.value)


def test_raise_filereaderror_from_exception__long_filename_truncated():
    _ex = RuntimeError("Some error")
    _fname = "a" * 70 + ".txt"
    with pytest.raises(FileReadError) as exc_info:
        IoBase.raise_filereaderror_from_exception(_ex, _fname)
    assert "[...]" in str(exc_info.value)


def test_raise_filereaderror_from_exception__numeric_first_arg_uses_second():
    _ex = RuntimeError(42, "Descriptive error message")
    with pytest.raises(FileReadError) as exc_info:
        IoBase.raise_filereaderror_from_exception(_ex, "file.txt")
    assert "Descriptive error message" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
