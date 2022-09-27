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
Module with the InputPlugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["InputPlugin"]

import os

import numpy as np

from ..core import get_generic_parameter
from ..core.constants import INPUT_PLUGIN
from ..experiment import SetupScan
from ..managers import ImageMetadataManager
from .base_plugin import BasePlugin


SCAN = SetupScan()


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """

    plugin_type = INPUT_PLUGIN
    plugin_name = "Base input plugin"
    output_data_label = "Image intensity"
    output_data_unit = "counts"
    input_data_dim = None
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_params(
        get_generic_parameter("use_roi"),
        get_generic_parameter("roi_xlow"),
        get_generic_parameter("roi_xhigh"),
        get_generic_parameter("roi_ylow"),
        get_generic_parameter("roi_yhigh"),
        get_generic_parameter("binning"),
    )
    default_params = BasePlugin.default_params.get_copy()

    def __init__(self, *args, **kwargs):
        """
        Create BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)
        self.filename_string = ""
        self.__setup_image_magedata_manager()

    def __setup_image_magedata_manager(self):
        """
        Setup the ImageMetadataManager to determine the shape of the final
        image.

        The shape of the final image is required to determine the shape of
        the processed data in the WorkflowTree.
        """
        _metadata_params = [
            self.get_param(key)
            for key in [
                "use_roi",
                "roi_xlow",
                "roi_xhigh",
                "roi_ylow",
                "roi_yhigh",
                "binning",
            ]
        ]
        if "hdf5_key" in self.params:
            _metadata_params.append(self.get_param("hdf5_key"))
        self._image_metadata = ImageMetadataManager(*_metadata_params)

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        self.update_filename_string()
        self._image_metadata.update(filename=self.filename_string.format(index=0))
        self._config["result_shape"] = self._image_metadata.final_shape
        self._original_input_shape = (
            self._image_metadata.raw_size_y,
            self._image_metadata.raw_size_x,
        )

    def prepare_carryon_check(self):
        """
        Prepare the checks of the multiprocessing carryon.

        By default, this gets and stores the file target size for live
        processing.
        """
        self._config["file_size"] = self.get_first_file_size()

    def get_first_file_size(self):
        """
        Get the size of the first file to be processed.

        Returns
        -------
        int
            The file size in bytes.
        """
        _fname = self._image_metadata.filename
        self._config["file_size"] = os.stat(_fname).st_size
        return self._config["file_size"]

    def input_available(self, index):
        """
        Check whether a new input file is available.

        Note: This function returns False by default. It is intended to be
        used only for checks during live processing.

        Parameters
        ----------
        index : int
            The frame index.

        Returns
        -------
        bool
            flag whether the file for the frame #<index> is ready for reading.
        """
        _fname = self.get_filename(index)
        if os.path.exists(_fname):
            return self._config["file_size"] == os.stat(_fname).st_size
        return False

    def pre_execute(self):
        """
        Run generic pre-execution routines.
        """
        self._config["n_multi"] = SCAN.get_param_value("scan_multiplicity")
        self._config["start_index"] = SCAN.get_param_value("scan_start_index")
        self._config["delta_index"] = SCAN.get_param_value("scan_index_stepping")

    def execute(self, index, **kwargs):
        """
        Import the data and pass it on after (optionally) handling image multiplicity.

        Parameters
        ----------
        index : int
            The index of the scan point.
        **kwargs : dict
            Keyword arguments passed to the execute method.

        Returns
        -------
        pydidas.core.Dataset
            The image data frame.
        """
        _data = None
        _frames = (
            self._config["n_multi"] * self._config["delta_index"] * index
            + self._config["start_index"]
            + self._config["delta_index"] * np.arange(self._config["n_multi"])
        )
        for _frame_index in _frames:
            if _data is None:
                _data = self.get_frame(_frame_index, **kwargs)
            else:
                _data += self.get_frame(_frame_index, **kwargs)
        if SCAN.get_param_value("scan_multi_image_handling") == "Average":
            _data /= self._config["n_multi"]
        return _data, kwargs

    def get_filename(self, index):
        """
        Get the filename of the file associated with the index.

        Parameters
        ----------
        index : int
            The frame index.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by the concrete subclass.

        Returns
        -------
        str
            The filename.
        """
        raise NotImplementedError

    def get_frame(self, frame_index, **kwargs):
        """
        Get the specified image frame (which does not necessarily correspond to the
        scan point index).

        Parameters
        ----------
        frame_index : int
            The index of the specific frame to be loaded.
        **kwargs : dict
            Keyword arguments passed for loading the frame.

        Returns
        -------
        pydidas.core.Dataset
            The image data frame.
        """
        raise NotImplementedError

    def update_filename_string(self):
        """
        Update the filename_string from the input Parameters.
        """
        raise NotImplementedError
