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

"""
The read_image_func module includes the read_image function which queries
the ImageReaderFactory for the correct reader and reads the image from the file.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
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
    image : pydidas.core.Dataset
        The processed image.
    """
    reader = IMAGE_READER.get_reader(filename)
    return reader.read_image(filename, **kwargs)
