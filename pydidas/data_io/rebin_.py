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

"""Module with the rebin2d function to rebin images."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['rebin2d', 'rebin']

import numpy as np

from ..core import Dataset


def rebin2d(image, binning):
    """
    Rebin a 2-d numpy.ndarray.

    This function rebins a 2d image in the form of a numpy.ndarray with a
    factor by calculating the corresponding mean values.

    Parameters
    ----------
    image : Union[np.ndarray, Dataset]
        The 2d image to be re-binned.
    binning : int
        The re-binning factor.

    Returns
    -------
    image : np.ndarray or Dataset
        The re-binned image in the same data type as the input image.
    """
    if binning == 1:
        return image
    if isinstance(image, Dataset):
        return image.get_rebinned_copy(binning)
    _shape = image.shape
    if _shape[0] % binning != 0:
        _r0 = _shape[0] % binning
        image = image[:-_r0]
    if _shape[1] % binning != 0:
        _r1 = _shape[1] % binning
        image = image[:, :-_r1]
    _s0 = _shape[0] // binning
    _s1 = _shape[1] // binning
    _sh = _s0, image.shape[0] // _s0, _s1, image.shape[1] // _s1
    return image.reshape(_sh).mean(-1).mean(1)


def rebin(data, binning):
    """
    Rebin a n-d numpy.ndarray.

    This function rebins an n-d array in the form of a numpy.ndarray with a
    factor by calculating the corresponding mean values.

    Parameters
    ----------
    data : np.ndarray
        The n-d data to be re-binned.
    binning : int
        The re-binning factor.

    Returns
    -------
    data : np.ndarray
        The re-binned data.
    """
    if binning == 1:
        return data
    if isinstance(data, Dataset):
        return data.get_rebinned_copy(binning)
    _shape = np.asarray(data.shape)
    _lowlim = (_shape % binning) // 2
    _highlim = _shape - (_shape % binning) + _lowlim
    _highlim[_highlim == _lowlim] += 1
    _slices = tuple(slice(low, high) for low, high in zip(_lowlim, _highlim))
    data = data[_slices]
    _newshape = tuple()
    for _s in data.shape:
        _addon = (1, 1) if _s == 1 else (_s // binning, binning)
        _newshape = _newshape + _addon
    data.shape = _newshape
    _flataxes = tuple(np.arange(1, data.ndim, 2))
    data = np.mean(data, axis=_flataxes)
    return data
