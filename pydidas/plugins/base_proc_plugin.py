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
Module with the processing Plugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcPlugin']

import os

from ..core.constants import PROC_PLUGIN, HDF5_EXTENSIONS
from ..core.utils import check_file_exists, check_hdf5_key_exists_in_file
from ..image_io import read_image
from .base_plugin import BasePlugin


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    plugin_type = PROC_PLUGIN
    plugin_name = 'Base processing plugin'
    generic_params = BasePlugin.generic_params.get_copy()
    default_params = BasePlugin.default_params.get_copy()

    def load_image_from_file(self, fname, hdf5_dset='entry/data/data',
                             hdf5_frame=0):
        """
        Load an image from the specified filename.

        If the image filename has an HDF5 extension, the optional kwargs
        ``hdf5_dset`` and ``hdf5_frame`` will be used

        Parameters
        ----------
        fname : Union[pathlib.Path, str]
            The filename of the image file.
        hdf5_dset : Union[str, None], optional
            The Hdf5 dataset key, if the file is an Hdf5 file. If the file does
            not have an Hdf5 extension, this entry will be ignored. The default
            is entry/data/data.
        hdf5_frame : Union[int, None], optional
            The frame number in the Hdf5 file. The the file does not have an
            Hdf5 extension, this entry will be ignored. The default is 0.

        Returns
        -------
        pydidas.core.Dataset
            The loaded iamge data.
        """
        if not isinstance(fname, str):
            fname = str(fname)
        check_file_exists(fname)
        _params = {}
        if os.path.splitext(fname)[1] in HDF5_EXTENSIONS:
            check_hdf5_key_exists_in_file(fname, hdf5_dset)
            _params = {'hdf5_dataset': hdf5_dset, 'frame': hdf5_frame}
        _image = read_image(fname, **_params)
        return _image
