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

"""Module with the basic Plugin classes."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BasePlugin', 'InputPlugin', 'ProcPlugin', 'OutputPlugin']


from pydidas.core import (ParameterCollection, ObjectWithParameterCollection,
                          get_generic_parameter)
from pydidas.constants import (BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                               OUTPUT_PLUGIN)
from .base_plugin import BasePlugin
from pydidas.apps.app_utils import ImageMetadataManager


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Base input plugin'
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_params(
        get_generic_parameter('use_roi'),
        get_generic_parameter('roi_xlow'),
        get_generic_parameter('roi_xhigh'),
        get_generic_parameter('roi_ylow'),
        get_generic_parameter('roi_yhigh'),
        get_generic_parameter('binning'))
    default_params = BasePlugin.default_params.get_copy()

    def __init__(self, *args, **kwargs):
        BasePlugin.__init__(self, *args, **kwargs)
        self._image_metadata = ImageMetadataManager(
            *[self.get_param(key)
              for key in ['use_roi', 'roi_xlow', 'roi_xhigh',
                          'roi_ylow', 'roi_yhigh', 'binning']])

    @property
    def result_shape(self):
        """
        Get the shape of the plugin result.

        Unknown dimensions are represented as -1 value.

        Returns
        -------
        tuple
            The shape of the results.
        """
        if self.output_data_dim == -1:
            return (-1,)
        _shape = self._config.get('result_shape', None)
        if _shape is None:
            return (-1,) * self.output_data_dim
        return _shape


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    plugin_type = PROC_PLUGIN
    plugin_name = 'Base processing plugin'
    generic_params = BasePlugin.generic_params.get_copy()
    default_params = BasePlugin.default_params.get_copy()


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """
    plugin_type = OUTPUT_PLUGIN
    plugin_name = 'Base output plugin'
    generic_params = BasePlugin.generic_params.get_copy()
    default_params = BasePlugin.default_params.get_copy()
