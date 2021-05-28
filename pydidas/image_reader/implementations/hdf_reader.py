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

"""Module with the Hdf5Reader class for reading hdf5 images."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

from ..image_reader import ImageReader
from ..image_reader_factory import ImageReaderFactory
from ..low_level_readers.read_hdf_slice import read_hdf_slice
from ...config import HDF5_EXTENSIONS

class Hdf5Reader(ImageReader):
    """ImageReader implementation for hdf5 files."""

    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)

    def read_image(self, filename, **kwargs):
        """
        Read an image from an hdf5 file.

        The read_image method extracts an image from a HDF file and returns
        it after processing any operations specified by the keywords
        (binning, cropping).

        The datapath, imageNo, axisNo parameters are required.

        Parameters
        ----------
        filename : str
            The full path and filename of the file to be read.
        dataset : str
            The full path to the hdf dataset within the file. The default is
            None which will raise an exception.
        imageNo : int
            The number of the image in the dataset. The default is 0.
        axisNo : int
            The number of the axis with the image. The default is 0.
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
            The image metadata. For hdf5 images, this will be information
            about the dataset and axis and image numbers.
       """
        axisNo = kwargs.get('axisNo', 0)
        imageNo = kwargs.get('imageNo', 0)
        dataset = kwargs.get('dataset', None)

        self._image_metadata = {'axisNo': axisNo, 'imageNo': imageNo,
                                'dataset': dataset}
        kwargs.update(self._image_metadata)
        if dataset is None:
            raise KeyError('The hdf dataset has not been specified.')
        self._image = read_hdf_slice(
            filename, dataset, [None] * axisNo + [imageNo])
        return self.return_image(**kwargs)


reader = ImageReaderFactory()
reader.register_format('hdf5', HDF5_EXTENSIONS, Hdf5Reader)
