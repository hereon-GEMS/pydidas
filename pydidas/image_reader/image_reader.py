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

"""Module with the ImageReader base class from which all readers should
inherit."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageReader']

from .rebin_2d import rebin2d


class ImageReader:
    """Generic implementation of the image reader."""

    def __init__(self, *args, **kwargs):
        """Initialization"""
        self._image = None
        self._image_metadata = None

    def read_image(self, filename, **kwargs):
        """
        Read an image from file.

        This method must be implemented by the concrete subclasses.
        """
        raise NotImplementedError

    def return_image(self, *args, **kwargs):
        """
        Return the stored image

        Parameters
        ----------
        *args : object
            A list of arguments. Currently not used.
        **kwargs : dict
            A dictionary of keyword arguments. Supported keyword arguments
            include the following
        returnType : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        binning : int, optional
            The reb-inning factor to be applied to the image. The default
            is 1.
        ROI : Union[tuple, None], optional
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
        _image : np.ndarray
            The image in form of an ndarray
        _metadata : dict
            The image metadata, as returned from the concrete reader.
        """
        _return_type = kwargs.get('returnType', 'auto')
        _roi = self.check_ROI(**kwargs)
        _binning = kwargs.get('binning', 1)
        if not hasattr(self, '_image'):
            raise ValueError('No image has been read.')
        _image = self._image
        if _roi is not None:
            _image = _image[_roi]
        if _binning != 1:
            _image = rebin2d(_image, int(_binning))
        if _return_type not in ('auto', _image.dtype):
            _image = _image.astype(_return_type)
        return _image, self._image_metadata

    @staticmethod
    def check_ROI(**kwargs):
        """Verification of ROI format.

        This method checks the ROI and verifies its format. If the format
        differs from the expected format (a tuple of two slices),
        the method tries to convert the ROI to a tuple of two slices.

        Parameters
        ----------
            **kwargs: This should include the 'ROI' keyword

        Raises
        ------
        ValueError
            If conversion to two slice objects was not successful.

        Returns
        -------
        Union[None, tuple]
            If ROI is None, None is returned. Else, a tuple of 2 slice
            objects will be returned.
        """
        roi = kwargs.get('ROI', None)
        errorstr = f'The format of the ROI "{roi}" could not be interpreted.'
        if roi is None:
            return roi
        if isinstance(roi, tuple):
            roi = list(roi)
        elif not isinstance(roi, list):
            raise ValueError(errorstr)
        # filter strings and convert them to integers:
        roi = [int(i) if isinstance(i, str) else i for i in roi]
        # check for other datatypes
        roi_dtypes = {type(e) for e in roi}
        roi_dtypes.discard(int)
        roi_dtypes.discard(slice)
        if not roi_dtypes:
            raise ValueError(errorstr)
        # convert to slices
        try:
            if isinstance(roi[0], int) and isinstance(roi[1], int):
                out = [slice(roi.pop(0), roi.pop(0))]
            elif isinstance(roi[0], slice):
                out = [roi.pop(0)]
            else:
                raise ValueError(errorstr)
            if isinstance(roi[0], int) and isinstance(roi[1], int):
                out.append(slice(roi.pop(0), roi.pop(0)))
            elif isinstance(roi[0], slice):
                out.append(roi.pop(0))
            else:
                raise ValueError(errorstr)
            return tuple(out)
        except ValueError:
            raise ValueError(errorstr) from ValueError
