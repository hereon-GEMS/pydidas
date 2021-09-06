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

"""Module with the NumpyReader implementation of the base ImageReader."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import numpy as np

from ...core import Dataset
from ..image_reader import ImageReader
from ..image_reader_factory import ImageReaderFactory
from ...config import NUMPY_EXTENSIONS


class NumpyReader(ImageReader):
    """
    Reader for numpy data formats.
    """

    def __init__(self):
        """
        Initialization method
        """
        super().__init__()

    def read_image(self, filename, **kwargs):
        """
        Read and return a numpy image.

        The read_image method loads a numpy format type image and returns
        it after processing any operations specified by the keywords
        (binning, cropping).

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
        image : pydidas.core.Dataset
            The image in form of a Dataset (with embedded metadata)
        """
        _data = np.load(filename)
        assert len(_data.shape)==2
        self._image = Dataset(_data)
        return self.return_image(**kwargs)


reader = ImageReaderFactory()
reader.register_format('numpy', NUMPY_EXTENSIONS, NumpyReader)
