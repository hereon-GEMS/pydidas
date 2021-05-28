# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Module with the read_hdf_slice function which is the low-level implementation
of the hdf5 file reader with support for indexing and chunking.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['read_hdf_slice']

import itertools
from numbers import Integral
import h5py
import hdf5plugin
import numpy as np


def read_hdf_slice(h5filename, dataset, axes):
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
    dataset : str
        The path to the dataset in the hdf5 structure
    axes : list
        The indices for the individual axes (order as in the file).
        The input needs to be in form of a list of entries for each
        axis. Any missing axes will take the full data indices.

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
    with h5py.File(h5filename, 'r') as _file:
        ds = _file[dataset]
        # set-up the limits
        limits = np.r_[[(0, ds.shape[i]) for i in range(len(ds.shape))]]

        for i, _axis in enumerate(axes):
            if _axis is None:
                limits[i] = (0, ds.shape[i])
            # elif isinstance(_axis, (list, tuple)) and not _axis:
            #     limits[i] = (0, ds.shape[i])
            elif isinstance(_axis, (list, tuple)) and len(_axis) == 1:
                limits[i] = (_axis[0], _axis[0]+1)
            elif isinstance(_axis, (list, tuple)) and len(_axis) == 2:
                if _axis[0] is None:
                    _axis[0] = 0
                if _axis[1] in [-1, None]:
                    _axis[1] = ds.shape[i]
                limits[i] = (_axis[0], _axis[1])
            elif Integral.__subclasscheck__(_axis.__class__):
                limits[i] = (_axis, _axis + 1)
            else:
                raise ValueError(f'Slicing "{_axis}" not supported for axis '
                                 '{i}.')

        if ds.chunks is None:
            roi = tuple(slice(limits[i1,0], limits[i1,1]) for i1 in
                        range(limits.shape[0]))
            data = ds[roi]
        else:
            data = np.empty((limits[:, 1] - limits[:, 0]).astype(np.int16),
                            dtype=ds.dtype)

            num_slices = (
                np.ceil(limits[:, 1] / ds.chunks)
                - np.floor(limits[:, 0] / ds.chunks)
            ).astype(np.int16)

            slices_original = [None] * num_slices.size
            slices_target = [None] * num_slices.size
            for i in range(num_slices.size):
                s0, s1 = limits[i, 0], limits[i, 1]
                chk = ds.chunks[i]
                ioff = int(s0 // ds.chunks[i])
                slices_original[i] = [slice(max((j + ioff) * chk, s0),
                                             min((j + 1 + ioff) * chk, s1))
                                       for j in range(num_slices[i])]
                slices_target[i] = [slice(max((j + ioff) * chk -s0, 0),
                                           min((j + 1 + ioff) * chk, s1) - s0)
                                     for j in range(num_slices[i])]

            for s_ori, s_new in zip(itertools.product(*slices_original),
                                    itertools.product(*slices_target)):
                data[s_new] = ds[s_ori]
    return data
