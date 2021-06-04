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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

def read_hdf(h5file, location, axes):
    """Function to read unchunked/chunked data from an hdf file.
    
    Warning: Reading data from an unchunked file requires loading the full
    file with all the resulting memory and performance implications.

    :param h5file: file name of the hdf5 file
    :type h5file: str

    :param location: The path to the dataset in the hdf5 structure
    :type location: str

    :param axes: The indices for the individual axes (order as in the file).
                 The input needs to be in form of a list of entries for each
                 axis. Any missing axes will take the full data indices.

                 The following input formats are supported:

                 - None will take the full axis
                 - <value> will select only the slice of <value> from this axis
                 - [ax_low, ax_high] will take the range of ax_low to ax_high
                 - (ax_low, ax_high) will take the range of ax_low to ax_high

    :type axes: list of 2-tuple, 2-list, None, or integer

    :return: The dataset as a numpy array.
    :rtype: :py:class:`np.ndarray`
    """
    with h5py.File(h5file, 'r') as f:
        ds = f[location]
        limits = np.r_[[(0, ds.shape[i1]) for i1 in range(len(ds.shape))]]
        for i1 in range(len(axes)):
            if axes[i1] is None:
                limits[i1] = (0, ds.shape[i1])
            elif isinstance(axes[i1], (list, tuple)) and not axes[i1]:
                limits[i1] = (0, ds.shape[i1])
            elif isinstance(axes[i1], (list, tuple)) and len(axes[i1]) == 1:
                limits[i1] = (axes[i1][0], axes[i1][0]+1)
            elif isinstance(axes[i1], (list, tuple)) and len(axes[i1]) == 2:
                if axes[i1][0] is None:
                    axes[i1][0] = 0
                if axes[i1][1] in [-1, None]:
                    axes[i1][1] = ds.shape[i1]
                limits[i1] = (axes[i1][0], axes[i1][1])
            elif isinstance(axes[i1], (int, np.int16, np.int32)):
                limits[i1] = (axes[i1], axes[i1]+1)
            else:
                raise Exception('Slicing "{}" not supported.'.format(axes[i1]))

        if ds.chunks is None:
            roi = tuple(slice(limits[i1,0], limits[i1,1]) for i1 in 
                        range(limits.shape[0]))
            data = ds[roi]
        else:
            data = np.empty((limits[:, 1] - limits[:, 0]).astype(np.int16),
                            dtype=ds.dtype)
    
            numSlices = (np.ceil(limits[:, 1] / ds.chunks) \
                -np.floor(limits[:, 0] / ds.chunks)).astype(np.int16)
    
            slicesData = [None] * numSlices.size
            slicesTarget = [None] * numSlices.size
            for i0 in range(numSlices.size):
                s0, s1 = limits[i0, 0], limits[i0, 1]
                chk = ds.chunks[i0]
                ioff = int(s0 // ds.chunks[i0])
                slicesData[i0] = [slice(max((i1 + ioff) * chk, s0),
                                        min((i1 + 1 + ioff) * chk, s1))
                                  for i1 in range(numSlices[i0])]
                slicesTarget[i0] = [slice(max((i1 + ioff) * chk -s0, 0),
                                          min((i1 + 1 + ioff) * chk, s1) - s0)
                                    for i1 in range(numSlices[i0])]
    
            sliceFrom = itertools.product(*slicesData)
            sliceTo = itertools.product(*slicesTarget)
    
            for sF, sT in zip(sliceFrom, sliceTo):
                data[sT] = ds[sF]
    return data
#read_hdf