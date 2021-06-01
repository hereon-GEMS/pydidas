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

"""
The read_image_func module includes the read_image function which queries
the ImageReaderFactory for the correct reader and reads the image from the file.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['read_image']

from .image_reader_factory import ImageReaderFactory


IMAGE_READER = ImageReaderFactory()


def read_image(filename, **kwargs):
    """
    Read an image from a file and return it as numpy array.

    The read_image function will query if a reader is registered for the
    specified file format and read and return the file. The required
    keyword arguments vary, depending on file type.

    Parameters
    ----------
    filename : str
        The full filename and path to the file.
    *args : any
        further arguments (currently not used)
    **kwargs : dict
        keyword arguments

    Supported keyword arguments:

    for all images:
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
    for raw (binary) images additionally:
        datatype : object
            The python datatype used for decoding the bit-information of the
            binary file. The default is None which will raise an exception.
        nx : int
            The number of pixels in x-dimension. The default is None which
            will raise an exception.
        ny : int
            The number of pixels in x-dimension. The default is None which
            will raise an exception.
    for hdf images additionally:
        dataset : str
            The full path to the hdf dataset within the file. The default is
            None which will raise an exception.
        imageNo : int
            The number of the image in the dataset. The default is 0.
        axisNo : int
            The number of the axis with the image. The default is 0.

    Returns
    -------
    image : np.ndarray
        The processed image.
    """
    reader = IMAGE_READER.get_reader(filename)
    return reader.read_image(filename, **kwargs)
