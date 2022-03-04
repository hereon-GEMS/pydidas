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
Module with the ImageReader base class from which all readers should
inherit.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageReader']

from .rebin_2d import rebin2d
from .roi_controller import RoiController


class ImageReader:
    """Generic implementation of the image reader."""

    def __init__(self):
        """Initialization"""
        self._image = None
        self._roi_controller = RoiController()

    def read_image(self, filename, **kwargs):
        """
        Read an image from file.

        This method must be implemented by the concrete subclasses.
        """
        raise NotImplementedError

    def return_image(self, **kwargs):
        """
        Return the stored image

        Parameters
        ----------
        **kwargs : dict
            A dictionary of keyword arguments. Supported keyword arguments
            are:
        **datatype : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        **binning : int, optional
            The reb-inning factor to be applied to the image. The default
            is 1.
        **roi : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
            will be returned. The default is None.

        Raises
        ------
        ValueError
            If no image has beeen read.

        Returns
        -------
        _image : pydidas.core.Dataset
            The image in form of an ndarray
        """
        _return_type = kwargs.get('datatype', 'auto')
        self._roi_controller.roi = kwargs.get('roi', None)
        _binning = kwargs.get('binning', 1)
        if self._image is None:
            raise ValueError('No image has been read.')
        _image = self._image
        if self._roi_controller.roi is not None:
            _image = _image[self._roi_controller.roi]
        if _binning != 1:
            _image = rebin2d(_image, int(_binning))
        if _return_type not in ('auto', _image.dtype):
            _image = _image.astype(_return_type)
        return _image
