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
Module with the input Plugin base class for 1 dim-data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputPlugin1d']

import os

from ..core import get_generic_parameter, AppConfigError
from ..core.constants import INPUT_PLUGIN
from ..managers import ImageMetadataManager
from .base_plugin import BasePlugin


class InputPlugin1d(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Base input plugin 1d'
    input_data_dim = None
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_params(
        get_generic_parameter('use_roi'),
        get_generic_parameter('roi_xlow'),
        get_generic_parameter('roi_xhigh'),
        get_generic_parameter('binning'))
    default_params = BasePlugin.default_params.get_copy()

    def __init__(self, *args, **kwargs):
        """
        Create BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)

    def pre_execute(self):
        """
        Run the pre-execution routines.
        """

    def prepare_carryon_check(self):
        """
        Prepare the checks of the multiprocessing carryon.

        By default, this gets and stores the file target size for live
        processing.
        """
        self._config['file_size'] = self.get_first_file_size()

    def get_first_file_size(self):
        """
        Get the size of the first file to be processed.

        Returns
        -------
        int
            The file size in bytes.
        """
        _fname = self.get_filename(0)
        self._config['file_size'] = os.stat(_fname).st_size
        return self._config['file_size']

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
            return self._config['file_size'] == os.stat(_fname).st_size
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

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """

        _n = self.get_raw_input_size()
        if self.get_param_value('use_roi'):
            _n_result = self.get_roi_size()
        else:
            _n_result = _n
        self._config['result_shape'] = (_n_result, )
        self._original_input_shape = (_n, )

    def get_raw_input_size(self):
        """
        Get the raw input size.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by the concrete subclass.

        Returns
        -------
        int
            The raw input size in bins.
        """
        raise NotImplementedError

    def get_roi_size(self):
        """
        Get the size of the ROI in points.

        Returns
        -------
        int
            The number of points in the ROI.
        """
        _low = self.get_param_value('roi_xlow')
        if _low is None:
            _low = 0
        _low = np.mod(_low, _n)
        _high = self.get_param_value('roi_xhigh')
        if _high is None or _high > _n:
            _high = _n
        _high = max(0, _high)
        return _high - _low + 1
