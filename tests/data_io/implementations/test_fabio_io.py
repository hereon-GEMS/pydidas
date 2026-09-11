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

"""Unit tests for pydidas.data_io.implementations.fabio_io module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import fabio
import numpy as np
import pytest

from tests.data_io.implementations.test_io_base import IoBaseTests

from pydidas.core import FileReadError
from pydidas.data_io.implementations.fabio_io import FabioIo


@pytest.fixture
def io_class():
    return FabioIo


@pytest.fixture
def edf_file(tmp_path):
    _fname = tmp_path / "test.edf"
    _data = np.random.random((10, 10))
    fabio.edfimage.EdfImage(_data).write(_fname)
    return _fname, _data


class TestFabioIo(IoBaseTests):
    """Runs the generic IoBase tests against FabioIo."""


def test_import_from_file(edf_file):
    _fname, _data = edf_file
    _result = FabioIo.import_from_file(_fname)
    assert np.allclose(_result, _data)


def test_import_from_file__wrong_name(edf_file):
    _fname, _ = edf_file
    with pytest.raises(FileReadError):
        FabioIo.import_from_file(_fname / "dummy")


def test_import_from_file__wrong_type(edf_file):
    _fname, _ = edf_file
    _fname.write_text("now it's just an ASCII text file.")
    with pytest.raises(FileReadError):
        FabioIo.import_from_file(_fname)


if __name__ == "__main__":
    pytest.main([__file__])
