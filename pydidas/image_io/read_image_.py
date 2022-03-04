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
The read_image_ includes the read_image function which returns a Dataset with
the image data from a filename.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['read_image']

from .image_reader_collection import ImageReaderCollection


IMAGE_READER = ImageReaderCollection()


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
        Keyword arguments. All supported keyword arguments are given below:
    **roi : Union[tuple, None], optional
        [available for all image types]
        A region of interest for cropping. Acceptable are both 4-tuples
        of integers in the format (y_low, y_high, x_low, x_high) as well
        as 2-tuples of integers or slice  objects. If None, the full image
        will be returned. The default is None.
    **returnType : Union[datatype, 'auto'], optional
        [available for all image types]
        If 'auto', the image will be returned in its native data type.
        If a specific datatype has been selected, the image is converted
        to this type. The default is 'auto'.
    **binning : int, optional
        [available for all image types]
        The reb-inning factor to be applied to the image. The default
        is 1.
    **datatype : object
        [for raw (binary) images only]
        The python datatype used for decoding the bit-information of the
        binary file. The default is None which will raise an exception.
    **nx : int
        [for raw (binary) images only]
        The number of pixels in x-dimension. The default is None which
        will raise an exception.
    **ny : int
        [for raw (binary) images only]
        The number of pixels in x-dimension. The default is None which
        will raise an exception.
    **hdf5_dataset : str
        [for hdf5 images only]
        The full path to the hdf dataset within the file. The default is
        None which will raise an exception.
    **frame : int
        [for hdf5 images only]
        The number of the image in the dataset. The default is 0.
    **axisNo : int
        [for hdf5 images only]
        The number of the axis with the image. The default is 0.

    Returns
    -------
    image : pydidas.core.Dataset
        The processed image.
    """
    reader = IMAGE_READER.get_reader(filename)
    _data = reader.read_image(filename, **kwargs)
    return _data
