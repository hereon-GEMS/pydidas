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

from ..core import get_generic_parameter, PydidasConfigError
from ..core.constants import INPUT_PLUGIN
from ..managers import ImageMetadataManager
from .base_plugin import BasePlugin


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
        use_filename_pattern = kwargs.get("use_filename_pattern", False)
        self.__setup_image_magedata_manager(use_filename_pattern)

    def __setup_image_magedata_manager(self, use_filename_pattern=False):
        """
        Setup the ImageMetadataManager to determine the shape of the final
        image.

        The shape of the final image is required to determine the shape of
        the processed data in the WorkflowTree.

        Parameters
        ----------
        use_filename_pattern : bool, optional
            Keyword to use a filename pattern. The default is False.

        Raises
        ------
        PydidasConfigError
            If neither or both "first_file" or "filename" Parameters are used
            for a non-basic plugin.
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
        _has_first_file = "first_file" in self.default_params
        _has_filename = "filename" in self.default_params
        if _has_first_file and not _has_filename:
            _metadata_params.append(self.get_param("first_file"))
            _use_filename = False
        elif _has_filename and not _has_first_file:
            _metadata_params.append(self.get_param("filename"))
            _use_filename = True
        elif self.basic_plugin or use_filename_pattern:
            # create some dummy value
            _use_filename = True
        else:
            raise PydidasConfigError(
                "Ambiguous choice of Parameters. Use exactly"
                ' one of  both "first_file" and "filename".'
            )
        self._image_metadata = ImageMetadataManager(*_metadata_params)
        self._image_metadata.set_param_value("use_filename", _use_filename)

    def pre_execute(self):
        """
        Run the pre-execution routines.
        """

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        self._image_metadata.update()
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
        _fname = self._image_metadata.get_filename()
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
