# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import os
from copy import copy
from numbers import Integral

from numpy import amax, squeeze
import h5py
import hdf5plugin

from ...core.constants import HDF5_EXTENSIONS
from ...core import Dataset
from ..low_level_readers.read_hdf5_slice import read_hdf5_slice
from .io_base import IoBase


class Hdf5Io(IoBase):
    """IObase implementation for Hdf5 files."""
    extensions_export = HDF5_EXTENSIONS
    extensions_import = HDF5_EXTENSIONS
    format_name = 'Hdf5'
    dimensions = [1, 2, 3, 4, 5, 6]

    @classmethod
    def import_from_file(cls, filename, **kwargs):
        """
        Read data from a Hdf5 file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename of the file with the data to be imported.
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
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
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
        frame = kwargs.get('frame', 0)
        if isinstance(frame, Integral):
            frame = [frame]
        dataset = kwargs.get('dataset', 'entry/data/data')
        slicing_axes = kwargs.get('slicing_axes', [0])

        if len(frame) < len(slicing_axes):
            raise ValueError('The number of frames must not be shorter than '
                             'the number of slicing indices.')

        if len(slicing_axes) == 0:
            _slicer = []
        else:
            _tmpframe = copy(frame)
            _slicer = [(_tmpframe.pop(0) if _i in slicing_axes else None)
                       for _i in range(amax(slicing_axes) + 1)]

        _data = squeeze(read_hdf5_slice(filename, dataset, _slicer))
        cls._data = Dataset(_data, metadata={'slicing_axes': slicing_axes,
                                             'frame': frame,
                                             'dataset': dataset})
        return cls.return_data(**kwargs)

    @classmethod
    def export_to_file(cls, filename, data, **kwargs):
        """
        Export data to an Hdf5 file.

        Parameters
        ----------
        filename : Union[pathlib.Path, str]
            The filename
        data : np.ndarray
            The data to be written to file.
        dataset : str, optional
            The full path to the hdf dataset within the file. The default is
            "entry/data/data".
        overwrite : bool, optional
            Flag to allow overwriting of existing files. The default is False.

        """
        cls.check_for_existing_file(filename, **kwargs)
        dataset = kwargs.get('dataset', 'entry/data/data')
        _groupname = os.path.dirname(dataset)
        _key = os.path.basename(dataset)
        with h5py.File(filename, 'w') as _file:
            _group = _file.create_group(_groupname)
            _group.create_dataset(_key, data=data)
