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

"""Module with the TiffReader class for reading tiff images.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from skimage.io import imread

from ..image_reader import ImageReader
from ..image_reader_factory import ImageReaderFactory
from ...config import TIFF_EXTENSIONS


class TiffReader(ImageReader):
    """ImageReader implementation for tiff files."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)

    def read_image(self, filename, **kwargs):
        """
        Read an image from a TIFF file.

        The read_image method extracts an image from a TIFF file
        and returns it after processing any operations specified by the
        keywords (binning, cropping).

        Parameters
        ----------
        filename : str
            The full path and filename of the file to be read.
        ROI : Union[tuple, None], optional
            A region of interest for cropping. Acceptable are both 4-tuples
            of integers in the format (y_low, y_high, x_low, x_high) as well
            as 2-tuples of integers or slice  objects. If None, the full image
            will be returned. The default is None.
        returnType : Union[datatype, 'auto'], optional
            If 'auto', the image will be returned in its native data type.
            If a specific datatype has been selected, the image is converted
            to this type. The default is 'auto'.
        binning : int, optional
            The reb-inning factor to be applied to the image. The default
            is 1.

        Returns
        -------
        _image : np.ndarray
            The image in form of an ndarray
        _metadata : dict
            The image metadata. For tiff images, this will be None.
        """
        _data = imread(filename)
        assert len(_data.shape) == 2
        self._image = _data
        return self.return_image(**kwargs)


reader = ImageReaderFactory()
reader.register_format('tiff', TIFF_EXTENSIONS, TiffReader)
