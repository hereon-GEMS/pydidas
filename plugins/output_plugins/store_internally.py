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
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['AsciiSaver']

import numpy as np

from pydidas.core.constants import OUTPUT_PLUGIN
from pydidas.core import Dataset
from pydidas.plugins import OutputPlugin, BasePlugin


class StoreInternally(OutputPlugin):
    """
    A plugin to store the current results internally.

    This class is designed to store data passed down from other processing
    plugins into Ascii data.

    Parameters
    ----------
    label : str
        The prefix for saving the data.
    directory_path : Union[pathlib.Path, str]
        The output directory.
    """
    plugin_name = 'Store data internally'
    basic_plugin = False
    plugin_type = OUTPUT_PLUGIN
    input_data_dim = -1
    output_data_dim = -1
    generic_params = BasePlugin.generic_params.get_copy()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pre_execute(self):
        """
        Run the pre-execution.
        """
        pass

    def execute(self, data, **kwargs):
        """
        Execute the plugin.

        This plugin only passes the data on to store it internally in the
        WorkflowResults

        Parameters
        ----------
        data : Union[np.ndarray, pydidas.core.Dataset]
            The data to be stored.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        return data, kwargs
