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

"""Module with the rebin2d function to rebin images."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
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
