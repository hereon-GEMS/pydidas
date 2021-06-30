# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the rebin2d function to rebin images."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['rebin2d']


def rebin2d(image, binning):
    """
    Rebin an 2-d numpy.ndarray.

    This function rebins a 2d image in the form of a numpy.ndarray with a
    factor by calculating the corresponding mean values.

    Parameters
    ----------
    image : np.ndarray
        The 2d image to be re-binned.
    binning : int
        The re-binning factor.

    Returns
    -------
    image : np.ndarray
        The re-binned image.
    """
    if binning == 1:
        return image
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
