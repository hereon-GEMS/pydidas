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

"""Unit tests for pydidas.data_io.implementations.jpeg_io module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from tests.data_io.implementations.test_io_base import IoBaseTests

from pydidas.core.constants import JPG_EXTENSIONS
from pydidas.data_io.implementations.jpeg_io import JpegIo


@pytest.fixture
def io_class():
    return JpegIo


@pytest.fixture
def jpeg_data(tmp_path):
    _data = np.random.random((127, 137))
    _fname = tmp_path / "test.jpg"
    return _fname, _data


class TestJpegIo(IoBaseTests):
    """Runs the generic IoBase tests against JpegIo."""


def test_class_extensions():
    for _ext in JPG_EXTENSIONS:
        assert _ext in JpegIo.extensions_export


def test_export_to_file__file_exists(jpeg_data):
    _fname, _data = jpeg_data
    JpegIo.export_to_file(_fname, _data)
    with pytest.raises(FileExistsError):
        JpegIo.export_to_file(_fname, _data)


def test_export_to_file__file_exists_and_overwrite(tmp_path):
    _fname = tmp_path / "test_overwrite.jpg"
    _data = np.random.random((127, 137))
    JpegIo.export_to_file(_fname, _data)
    _size = _fname.stat().st_size
    JpegIo.export_to_file(_fname, _data[:57], overwrite=True)
    assert _fname.stat().st_size != _size


def test_export_to_file(jpeg_data):
    _fname, _data = jpeg_data
    JpegIo.export_to_file(_fname, _data)
    assert _fname.exists()


if __name__ == "__main__":
    pytest.main([__file__])
