# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon
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
The parameter module includes the Parameter class which is used to store
processing parameters.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['export_image']


import os
import h5py
import numpy as np
import skimage.io
import matplotlib.pyplot as plt

from pydidas.config import (
    HDF5_EXTENSIONS, NUMPY_EXTENSIONS, BINARY_EXTENSIONS, TIFF_EXTENSIONS,
    JPG_EXTENSIONS)


def export_image(image, output_fname):
    _ext = os.path.splitext(output_fname)[1].lower()
    if _ext in NUMPY_EXTENSIONS:
        np.save(output_fname, image)
    elif _ext in HDF5_EXTENSIONS:
        with h5py.File(output_fname, 'w') as f:
            f['entry/data/data'] = image
    elif _ext in BINARY_EXTENSIONS:
        image.tofile(output_fname)
    elif _ext in TIFF_EXTENSIONS:
        skimage.io.imsave(output_fname, image)
    elif _ext == '.png' or _ext in JPG_EXTENSIONS:
        _backend = plt.get_backend()
        plt.rcParams['backend'] = 'Agg'
        _figshape, _dpi = _get_fig_arguments(image)
        fig1 = plt.figure(figsize=_figshape, dpi=50)
        ax = fig1.add_axes([0, 0, 1, 1])
        ax.imshow(image, interpolation='none', vmin=np.amin(image),
                  vmax=np.amax(image), cmap='gray')
        ax.set_xticks([])
        ax.set_yticks([])
        fig1.savefig(output_fname, dpi=_dpi)
        plt.close(fig1)
        plt.rcParams['backend'] = _backend


def _get_fig_arguments(image, target_size_inches=10):
    nx = image.shape[1]
    ny = image.shape[0]
    size_x = target_size_inches * nx / max(nx, ny)
    size_y = target_size_inches * ny / max(nx, ny)
    _shape = (size_x, size_y)
    _dpi = max(nx, ny) / target_size_inches
    return _shape, _dpi

