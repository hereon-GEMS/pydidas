# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
Module with the TiffIo class for importing and exporting tiff data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import warnings
from pathlib import Path
from typing import Any, ClassVar

import numpy as np

from pydidas.core import Dataset
from pydidas.core.constants import TIFF_EXTENSIONS
from pydidas.core.lazy_imports.skimage import TiffFileError, imread, imsave
from pydidas.core.utils import CatchFileErrors, verify_is_new_file_or_replace_set
from pydidas.data_io.implementations.io_base import IoBase


class TiffIo(IoBase):
    """IObase implementation for tiff files."""

    extensions_export: ClassVar[list[str]] = TIFF_EXTENSIONS
    extensions_import: ClassVar[list[str]] = TIFF_EXTENSIONS
    format_name: ClassVar[str] = "Tiff"
    dimensions: ClassVar[list[int]] = [2]

    @staticmethod
    def import_from_file(filename: Path | str, **kwargs: Any) -> Dataset:
        """
        Read data from a tiff file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file with the data to be imported.
        **kwargs : Any
            Supported arguments are:

            roi : tuple or None, optional
                A region of interest for cropping. Acceptable are both 4-tuples
                of integers in the format (y_low, y_high, x_low, x_high) and
                2-tuples of integers or slice objects. If None, the full image
                will be returned. The default is None.
            astype : type or 'auto', optional
                If 'auto', the image will be returned in its native data type.
                If a specific datatype has been selected, the image is converted
                to this type. The default is 'auto'.
            binning : int, optional
                The rebinning factor to be applied to the image. The default
                is 1.

        Returns
        -------
        data : Dataset
            The data in the form of a pydidas Dataset (with embedded metadata)
        """
        with (
            CatchFileErrors(filename, TiffFileError),
            warnings.catch_warnings(action="ignore", category=UserWarning),
        ):
            _data = imread(filename)
            _data = Dataset(_data)
        return TiffIo.return_data(_data, **kwargs)

    @staticmethod
    def export_to_file(filename: Path | str, data: np.ndarray, **kwargs: Any) -> None:
        """
        Export data to a tiff file.

        Note
        ----
        1. scikit-image only supports saving 32-bit float, and all floating
           point numbers will be converted to 32 bit.
        2. scikit-image will save tiff files in different bit-depths, but it is
           not guaranteed that they can be opened by all programs.

        Parameters
        ----------
        filename : Path or str
            The filename
        data : np.ndarray
            The data to be written to file.
        **kwargs : Any
            Supported arguments are:

            overwrite : bool, optional
                Flag to allow overwriting of existing files. The default is
                False.
        """
        verify_is_new_file_or_replace_set(filename, **kwargs)
        with warnings.catch_warnings(action="ignore", category=UserWarning):
            if data.dtype.type in [np.float64, np.longdouble]:
                imsave(filename, data.astype(np.float32))
            else:
                imsave(filename, data)
