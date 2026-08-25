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

"""Unit tests for pydidas.data_io.implementations.tiff_io module."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from collections.abc import Callable
from itertools import count
from pathlib import Path

import numpy as np
import pytest

from tests.data_io.implementations.test_io_base import IoBaseTests

from pydidas.core import FileReadError
from pydidas.core.constants import TIFF_EXTENSIONS
from pydidas.core.lazy_imports.skimage import imsave
from pydidas.data_io.implementations.tiff_io import TiffIo


@pytest.fixture
def io_class():
    return TiffIo


@pytest.fixture
def tiff_file(tmp_path: Path) -> tuple[Path, np.ndarray]:
    data = np.random.random((12, 13))
    filename = tmp_path / "test.tif"
    imsave(filename, data)
    return filename, data


@pytest.fixture
def tiff_filename_factory(tmp_path: Path) -> Callable[[], Path]:
    index = count(1)

    def factory() -> Path:
        return tmp_path / f"test_name{next(index):03d}.tif"

    return factory


class TestTiffIo(IoBaseTests):
    """Runs the generic IoBase tests against TiffIo."""


def test_class_extensions() -> None:
    for extension in TIFF_EXTENSIONS:
        assert extension in TiffIo.extensions_export
        assert extension in TiffIo.extensions_import


def test_import_from_file__default(tiff_file: tuple[Path, np.ndarray]) -> None:
    filename, data = tiff_file
    assert np.allclose(TiffIo.import_from_file(filename), data)


def test_import_from_file__wrong_name(
    tiff_file: tuple[Path, np.ndarray],
) -> None:
    filename, _ = tiff_file
    with pytest.raises(FileReadError):
        TiffIo.import_from_file(filename / "dummy")


def test_import_from_file__wrong_type(
    tiff_file: tuple[Path, np.ndarray],
) -> None:
    filename, _ = tiff_file
    filename.write_text("now it's just an ASCII text file.")
    with pytest.raises(FileReadError):
        TiffIo.import_from_file(filename)


def test_export_to_file__file_exists(
    tiff_file: tuple[Path, np.ndarray],
) -> None:
    filename, data = tiff_file
    with pytest.raises(FileExistsError):
        TiffIo.export_to_file(filename, data)


def test_export_to_file__file_exists_and_overwrite(
    tiff_file: tuple[Path, np.ndarray],
    tiff_filename_factory: Callable[[], Path],
) -> None:
    filename = tiff_filename_factory()
    _, data = tiff_file
    TiffIo.export_to_file(filename, data)
    TiffIo.export_to_file(filename, data[:11], overwrite=True)
    imported = TiffIo.import_from_file(filename)
    assert imported.shape == (11,) + data.shape[1:]


def test_export_to_file__simple(
    tiff_file: tuple[Path, np.ndarray],
    tiff_filename_factory: Callable[[], Path],
) -> None:
    filename = tiff_filename_factory()
    _, data = tiff_file
    TiffIo.export_to_file(filename, data)
    imported = TiffIo.import_from_file(filename)
    assert np.allclose(imported, data)


@pytest.mark.parametrize(
    "dtype,scale,expected_dtype",
    [
        (np.int8, 125, np.int8),
        (np.uint8, 125, np.uint8),
        (np.int16, 1257, np.int16),
        (np.uint16, 1257, np.uint16),
        (np.int32, 12573, np.int32),
        (np.uint32, 12573, np.uint32),
        (np.float16, 1, np.float16),
        (np.float32, 1, np.float32),
        (np.float64, 1, np.float32),
        (np.longdouble, 1, np.float32),
    ],
)
def test_export_to_file__dtype_roundtrip(
    tiff_filename_factory: Callable[[], Path],
    dtype: np.dtype,
    scale: int,
    expected_dtype: np.dtype,
) -> None:
    filename = tiff_filename_factory()
    raw = (np.random.random((11, 12, 13)) * scale).astype(dtype)
    TiffIo.export_to_file(filename, raw)
    imported = TiffIo.import_from_file(filename)
    assert np.allclose(imported, raw)
    assert imported.dtype == expected_dtype


if __name__ == "__main__":
    pytest.main([__file__])
