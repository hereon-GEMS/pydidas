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
The parameter module includes the Parameter class which is used to store
processing parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['export_image']


import os
import h5py
import numpy as np
import skimage.io
import matplotlib.pyplot as plt

from pydidas.constants import (
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
