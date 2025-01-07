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
The rebin_ module includes functions to rebin 2d and n-dimensional data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["rebin2d", "rebin"]


import numpy as np

from pydidas.core.dataset import Dataset


def rebin2d(image: np.ndarray, binning: int) -> np.ndarray:
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


def rebin(data: np.ndarray, binning: int) -> np.ndarray:
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
    data = data[get_cropping_slices(data.shape, binning)]
    _newshape = tuple()
    for _s in data.shape:
        _addon = (1, 1) if _s == 1 else (_s // binning, binning)
        _newshape = _newshape + _addon
    if 0 in _newshape:
        raise ValueError(
            "Binning factor too large for the dataset. The resulting shape "
            "contains a dimension of size 0."
        )
    data.shape = _newshape
    return np.mean(data, axis=tuple(np.arange(1, data.ndim, 2)))


def get_cropping_slices(shape: tuple[int], binning: int) -> tuple[slice]:
    """
    Get the slices for cropping an array to be re-binned.

    This function will calculate the slices to crop an array to a shape which allows
    reshaping it in preparation for re-binning.

    Parameters
    ----------
    shape : tuple[int]
        The shape of the array to be re-binned.
    binning : int
        The re-binning factor.

    Returns
    -------
    tuple[slice]
        The slices to crop the array.
    """
    _shape = np.asarray(shape)
    _low_crop = (_shape % binning) // 2
    _upper_crop = np.maximum(_shape - (_shape % binning) + _low_crop, _low_crop + 1)
    return tuple(slice(low, high) for low, high in zip(_low_crop, _upper_crop))
