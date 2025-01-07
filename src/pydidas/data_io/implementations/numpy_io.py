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
Module with the NumpyIo class for importing and exporting numpy data.
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
from pydidas.core.constants import NUMPY_EXTENSIONS
from pydidas.core.utils import CatchFileErrors
from pydidas.data_io.implementations.io_base import IoBase


class NumpyIo(IoBase):
    """IObase implementation for numpy files."""

    extensions_export = NUMPY_EXTENSIONS
    extensions_import = NUMPY_EXTENSIONS
    format_name = "Numpy"
    dimensions = [1, 2, 3, 4, 5, 6]

    @classmethod
    def import_from_file(cls, filename: Union[Path, str], **kwargs: dict):
        """
        Read data from a numpy file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename of the file with the data to be imported.
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

        Returns
        -------
        data : pydidas.core.Dataset
            The data in form of a pydidas Dataset (with embedded metadata)
        """
        with CatchFileErrors(filename):
            _data = np.squeeze(np.load(filename))
        cls._data = Dataset(_data)
        return cls.return_data(**kwargs)

    @classmethod
    def export_to_file(
        cls, filename: Union[Path, str], data: np.ndarray, **kwargs: dict
    ):
        """
        Export data to a numpy file.

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
        np.save(filename, data)
