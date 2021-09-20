# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the RawReader class for reading raw (binary) images.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import numpy as np

from ...core import Dataset
from ..image_reader import ImageReader
from ..image_reader_collection import ImageReaderCollection
from ...config import BINARY_EXTENSIONS


class RawReader(ImageReader):
    """ImageReader implementation for raw (binary) files."""

    def __init__(self):
        super().__init__()

    def read_image(self, filename, datatype=None, nx=None, ny=None,
                   **kwargs):
        """
        Read an image from a raw (binary) file.

        The read_image method extracts an image from a raw binary file
        and returns it after processing any operations specified by the
        keywords (binning, cropping).

        The datatype, nx, ny parameters are required.

        Parameters
        ----------
        filename : str
            The full path and filename of the file to be read.
        datatype : object
            The python datatype used for decoding the bit-information of the
            binary file. The default is None which will raise an exception.
        nx : int
            The number of pixels in x-dimension. The default is None which
            will raise an exception.
        ny : int
            The number of pixels in x-dimension. The default is None which
            will raise an exception.
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
        image : pydidas.core.Dataset
            The image in form of a Dataset (with embedded metadata)
       """

        if datatype is None:
            raise KeyError('The datatype has not been specified.')
        if nx is None:
            raise KeyError('The number of pixels in x has not been specified.')
        if ny is None:
            raise KeyError('The number of pixels in y has not been specified.')
        self._image = Dataset(
            np.fromfile(filename, dtype=datatype).reshape(ny, nx))
        return self.return_image(**kwargs)


reader = ImageReaderCollection()
reader.register_format('raw', BINARY_EXTENSIONS, RawReader)
