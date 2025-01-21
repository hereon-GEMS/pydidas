# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the RawIo class for importing and exporting raw binary data without
a header.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


from pathlib import Path
from typing import Union

import numpy as np

from pydidas.core import Dataset
from pydidas.core.constants import BINARY_EXTENSIONS
from pydidas.core.utils import CatchFileErrors
from pydidas.data_io.implementations.io_base import IoBase


class RawIo(IoBase):
    """IObase implementation for raw binary files."""

    extensions_export = BINARY_EXTENSIONS
    extensions_import = BINARY_EXTENSIONS
    format_name = "Raw binary"
    dimensions = [1, 2, 3, 4, 5, 6]

    @classmethod
    def import_from_file(
        cls,
        filename: Union[Path, str],
        datatype: Union[None, type],
        shape: tuple = (),
        **kwargs: dict,
    ) -> Dataset:
        """
        Read data from a raw binary data without a header.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename of the file with the data to be imported.
        datatype : object
            The python datatype used for decoding the bit-information of the
            binary file. The default is None which will raise an exception.
        shape : Union[tuple, list]
            The shape of the raw data to be imported. This keyword must be
            used to allow a correct shaping of the raw data. If the shape is
            empty, an Exception will be raised. The default is [].
        roi : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice objects. If None, the full image
            will be returned. The default is None.
        returnType : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        binning : int, optional
            The rebinning factor to be applied to the image. The default
            is 1.
        offset : int, optional
            The reading offset from the file start in bytes. Using an offset
            allows to account for file headers. The default is 0.

        Returns
        -------
        data : pydidas.core.Dataset
            The data in form of a pydidas Dataset (with embedded metadata)
        """
        if datatype is None:
            raise KeyError("The datatype has not been specified.")
        _offset = kwargs.get("offset", 0)
        with CatchFileErrors(filename):
            _data = np.fromfile(filename, dtype=datatype, offset=_offset)
        if _data.size != np.prod(shape):
            cls.raise_filereaderror_from_exception(
                ValueError("The given shape does not match the data size."),
                str(filename),
            )
        cls._data = Dataset(_data.reshape(shape))
        return cls.return_data(**kwargs)

    @classmethod
    def export_to_file(
        cls, filename: Union[Path, str], data: np.ndarray, **kwargs: dict
    ):
        """
        Export data to raw binary file without a header.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        overwrite : bool, optional
            Flag to allow overwriting of existing files. The default is False.

        """
        cls.check_for_existing_file(filename, **kwargs)
        with open(filename, "wb") as _file:
            data.tofile(_file)
