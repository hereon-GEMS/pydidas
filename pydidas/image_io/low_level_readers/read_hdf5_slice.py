# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the read_hdf_slice function which is the low-level implementation
of the hdf5 file reader with support for indexing and chunking.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['read_hdf5_slice']

import itertools
from numbers import Integral

import h5py
import hdf5plugin
import numpy as np


def read_hdf5_slice(h5filename, hdf5_dataset, axes=None):
    """
    Read a n-dimensional slice from an hdf5 file.

    This function will read any n-dimensional slice from an hdf5 dataset.
    The limits can be specified for each axis seperatly.
    Warning: Reading data from an unchunked file requires loading the full
    file with all the resulting memory and performance implications.

    Parameters
    ----------
    h5file : str
        The file name of the hdf5 file.
    hdf5_dataset : str
        The path to the dataset in the hdf5 structure
    axes : Union[list, None]
        The indices for the individual axes (order as in the file).
        The input needs to be in form of a list of entries for each
        axis. Any missing axes will take the full data indices. No input
        (i.e. None) will take the full hdf5 dataset. The default is None.

        The following input formats are supported for individual axes:
            - None will take the full axis
            - <value> will select only the slice of <value> from this axis
            - [ax_low, ax_high] will take the range of ax_low to ax_high
            - (ax_low, ax_high) will take the range of ax_low to ax_high

    Returns
    -------
    np.ndarray
        The dataset as a numpy array.
    """
    axes = axes if axes is not None else []
    with h5py.File(h5filename, 'r') as _file:
        _ds = _file[hdf5_dataset]

        limits = np.r_[[(0, _shape) for _shape in _ds.shape]]
        for i, _axis in enumerate(axes):
            limits[i] = get_selection(_axis, _ds.shape[i])

        if _ds.chunks is None:
            roi = tuple(slice(*limits[i1]) for i1 in range(limits.shape[0]))
            return _ds[roi]

        data = np.empty(np.diff(limits, axis=1)[:,0], dtype=_ds.dtype)

        slices_original = np.empty(_ds.ndim, dtype=object)
        slices_target = np.empty(_ds.ndim, dtype=object)
        for i in range(_ds.ndim):
            _slices = get_slices(limits[i], _ds.chunks[i])
            slices_original[i] = _slices[0]
            slices_target[i] = _slices[1]

        for s_ori, s_new in zip(itertools.product(*slices_original),
                                itertools.product(*slices_target)):
            data[s_new] = _ds[s_ori]
    return data


def get_selection(entry, size):
    """
    Get the selection from the entry.

    This function will extract the limits for the entry and the shape.

    Parameters
    ----------
    entry : Union[None, int, list, tuple]
        The object
    size : int
        The size of the dataset dimension.

    Returns
    -------
    tuple
        The selection limits
    """
    if entry is None:
        return (0, size)
    entry = list(entry) if isinstance(entry, tuple) else entry
    if isinstance(entry, list) and len(entry) == 1:
        return (entry[0], entry[0]+1)
    if isinstance(entry, list) and len(entry) == 2:
        entry[0] = entry[0] if entry[0] is not None else 0
        entry[1] = entry[1] if entry[1] not in [-1, None] else size
        return (entry[0], entry[1])
    if Integral.__subclasscheck__(entry.__class__):
        return (entry, entry + 1)
    raise ValueError(f'Slicing "{entry}" not supported.')


def get_slices(limits, chunks):
    """
    Get the slices for one dimension based on limits and chunks.

    Parameters
    ----------
    limits : tuple
        The tuple with the limits of the data to read.
    chunks : int
        The number of chunks in this data dimension.

    Returns
    -------
    original_slices : list
        The list with the slice objects for this dimension of the original
        data
    target_slices : list
        The list with the slice objects for this dimension of the new data.
    """
    num_slices = (np.ceil(limits[1] / chunks)
                  - np.floor(limits[0] / chunks)).astype(np.int16)
    index_offset = limits[0] // chunks

    _limit_low = (lambda j, offset:
                  max((j + index_offset) * chunks, limits[0]) - offset)
    _limit_high = (lambda j, offset:
                   min((j + 1 + index_offset) * chunks, limits[1]) - offset)
    _ori = [slice(_limit_low(j, 0), _limit_high(j, 0))
            for j in range(num_slices)]
    _target  = [slice(_limit_low(j, limits[0]), _limit_high(j, limits[0]))
                for j in range(num_slices)]
    return _ori, _target
