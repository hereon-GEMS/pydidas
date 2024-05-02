# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with the Hdf5Io class for importing and exporting Hdf5 data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


import os
from copy import copy
from numbers import Integral
from pathlib import Path
from typing import Union

import h5py
from numpy import amax, ndarray, squeeze

from ...core import Dataset
from ...core.constants import HDF5_EXTENSIONS
from ...core.utils import CatchFileErrors
from ..low_level_readers import read_hdf5_dataset
from .io_base import IoBase


class Hdf5Io(IoBase):
    """IoBase implementation for Hdf5 files."""

    extensions_export = HDF5_EXTENSIONS
    extensions_import = HDF5_EXTENSIONS
    format_name = "Hdf5"
    dimensions = [1, 2, 3, 4, 5, 6]

    @classmethod
    def import_from_file(cls, filename: Union[Path, str], **kwargs: dict) -> Dataset:
        """
        Read data from a Hdf5 file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename of the file with the data to be imported.
        **kwargs : dict
            The following kwargs are supported:

            dataset : str, optional
                The full path to the hdf dataset within the file. The default is
                "entry/data/data".
            slicing_axes : list, optional
                The axes to be slices by the specified frame indices. The default
                is [0].
            frame : Union[int, list], optional
                The indices of the unused axes to identify the selected dataset.
                Integer values will be interpreted as values for axis 0.
                The default is 0.
            roi : Union[tuple, None], optional
                A region of interest for cropping. Acceptable are both 4-tuples
                of integers in the format (y_low, y_high, x_low, x_high) or
                2-tuples of integers or slice objects. If None, the full image
                will be returned. The default is None.
            returnType : Union[datatype, 'auto'], optional
                If 'auto', the image will be returned in its native data type.
                If a specific datatype has been selected, the image is converted
                to this type. The default is 'auto'.
            binning : int, optional
                The re-binning factor to be applied to the image. The default
                is 1.
            auto_squeeze : bool, optional
                Flag to automatically squeeze data dimensions before returning
                the data. The default is True.

        Returns
        -------
        data : pydidas.core.Dataset
            The data in form of a pydidas Dataset (with embedded metadata)
        """
        frame = kwargs.get("frame", [])
        if isinstance(frame, Integral):
            frame = [frame]
        dataset = kwargs.get("dataset", "entry/data/data")
        slicing_axes = kwargs.get("slicing_axes", [])
        if isinstance(slicing_axes, Integral):
            slicing_axes = [slicing_axes]

        auto_squeeze = kwargs.get("auto_squeeze", True)

        if len(frame) != len(slicing_axes):
            raise ValueError(
                "The length of frame items must be equal to the number of "
                f"slicing indices. Given frames: `{frame}`; given slicing axes: "
                f"`{slicing_axes}`."
            )

        if len(slicing_axes) == 0:
            _slicer = []
        else:
            _tmpframe = copy(frame)
            _slicer = [
                (_tmpframe.pop(0) if _i in slicing_axes else None)
                for _i in range(amax(slicing_axes) + 1)
            ]
        with CatchFileErrors(filename):
            _data = read_hdf5_dataset(filename, dataset, _slicer)
            if auto_squeeze:
                _data = squeeze(_data)
        cls._data = Dataset(
            _data,
            metadata={"slicing_axes": slicing_axes, "frame": frame, "dataset": dataset},
        )
        return cls.return_data(**kwargs)

    @classmethod
    def export_to_file(cls, filename: Union[Path, str], data: ndarray, **kwargs: dict):
        """
        Export data to a Hdf5 file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        **kwargs : dict
            Additional keyword arguments. Supported keyword arguments are:

            dataset : str, optional
                The full path to the hdf dataset within the file. The default is
                "entry/data/data".
            overwrite : bool, optional
                Flag to allow overwriting of existing files. The default is False.
        """
        cls.check_for_existing_file(filename, **kwargs)
        dataset = kwargs.get("dataset", "entry/data/data")
        _groupname = os.path.dirname(dataset)
        _key = os.path.basename(dataset)
        with h5py.File(filename, "w") as _file:
            _group = _file.create_group(_groupname)
            _group.create_dataset(_key, data=data)
