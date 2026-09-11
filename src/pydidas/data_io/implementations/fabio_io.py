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

"""
Module with the FabioIo class for reading ESRF-type images, e.g. EDF.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


from pathlib import Path
from typing import Any, ClassVar

from pydidas.core import Dataset
from pydidas.core.constants import FABIO_EXTENSIONS
from pydidas.core.lazy_imports.fabio import fabio_open
from pydidas.core.utils import CatchFileErrors
from pydidas.data_io.implementations.io_base import IoBase


class FabioIo(IoBase):
    """IObase implementation for files supported by FabIO (e.g. EDF)."""

    extensions_export: ClassVar[list[str]] = []
    extensions_import: ClassVar[list[str]] = FABIO_EXTENSIONS
    format_name: ClassVar[str] = "FabIO reader"
    dimensions: ClassVar[list[int]] = [2]

    @staticmethod
    def import_from_file(filename: Path | str, **kwargs: Any) -> Dataset:
        """
        Read an image from a FabIO-supported file format.

        Parameters
        ----------
        filename : Path or str
            The filename to read the image from.
        **kwargs : Any
            Additional keyword arguments to be passed to the import function.
            Supported keywords are:

            roi : tuple or None, optional
                A region of interest for cropping. Acceptable are both
                4-tuples of integers in the format (y_low, y_high, x_low,
                x_high) and 2-tuples of integers or slice objects.
                If None, the full image will be returned. The default is None.
            astype : datatype or 'auto', optional
                If 'auto', the image will be returned in its native data
                type. If a specific datatype has been selected, the image
                is converted to this type. The default is 'auto'.
            binning : int, optional
                The rebinning factor to be applied to the image. The default
                is 1.

        Returns
        -------
        image : Dataset
            The image in form of a Dataset (with embedded metadata)
        """
        with CatchFileErrors(filename, Exception), fabio_open(filename) as _file:
            _data = _file.data
            _header = _file.header

        _data = Dataset(_data, metadata=_header)
        return FabioIo.return_data(_data, **kwargs)
