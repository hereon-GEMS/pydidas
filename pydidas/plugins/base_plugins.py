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

"""Module with the basic Plugin classes."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BasePlugin', 'InputPlugin', 'ProcPlugin', 'OutputPlugin']


from pydidas.core import (ParameterCollection, ObjectWithParameterCollection,
                          get_generic_parameter, Parameter)

BASE_PLUGIN = -1
INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

ptype = {BASE_PLUGIN: 'Base plugin',
         INPUT_PLUGIN: 'Input plugin',
         PROC_PLUGIN: 'Processing plugin',
         OUTPUT_PLUGIN: 'Output plugin'}

class BasePlugin(ObjectWithParameterCollection):
    """
    The base plugin class from which all plugins inherit.

    Class attributes are:

    Class attributes
    ----------------
    basic_plugin : bool
        A keyword to mark basic plugin classes.
    plugin_type : int
        A key to discriminate between the different types of plugins
        (input, processing, output)
    parameters : ParameterCollection
        A ParameterCollection with the class parameters which are required
        to perform the execute operation.
    input_data : dict
        Dictionary with the required input data set descrptions
    output_data : dict
        Dictionary with a description of the output datasets.
    """
    basic_plugin = True
    plugin_type = BASE_PLUGIN
    plugin_name = 'Base plugin'
    default_params = ParameterCollection()
    generic_params = ParameterCollection()
    _is_pydidas_plugin = True
    input_data = {}
    output_data = {}

    @classmethod
    def get_class_description(cls):
        """
        Get a description of the plugin as a multi-line string.

        This method can generate a description of the plugin with name,
        plugin type, class name and Parameters and the docstring.
        The return is a formatted string.

        Returns
        -------
        str
            The descripion of the plugin.
        """
        _doc = (cls.__doc__ if cls.__doc__ is not None
                else 'No docstring available')
        _desc = (f'Plugin name: {cls.plugin_name}\n'
                 f'Class name: {cls.__name__}\n'
                 f'Plugin type: {ptype[cls.plugin_type]}\n\n'
                 f'Plugin description:\n{_doc}\n\n'
                 'Parameters:')
        for param in cls.default_params.values():
            _desc += f'\n{param}'
        return _desc

    @classmethod
    def get_class_description_as_dict(cls):
        """
        Get a description of the plugin as a dictionary of entries.

        This method can generate a description of the plugin with name,
        plugin type, class name and Parameters and the docstring.
        The return is a dictionary of entries.

        Returns
        -------
        dict
            The descripion of the plugin.
        """
        _doc = (cls.__doc__ if cls.__doc__ is not None
                else 'No docstring available')
        return {'Name': cls.plugin_name,
                'Class name': cls.__name__,
                'Plugin type': ptype[cls.plugin_type],
                'Plugin description': _doc,
                'Parameters': '\n'.join(
                    [str(param) for param in cls.default_params.values()])}

    def __init__(self, *args, **kwargs):
        """Setup the class."""
        super().__init__()
        if self.plugin_type not in [BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                                    OUTPUT_PLUGIN]:
            raise ValueError('Unknown value for the plugin type')
        self.add_params(*args)
        self.set_default_params()
        self.add_params(self.generic_params)
        for _kw in kwargs:
            if _kw in self.params.keys():
                self.set_param_value(_kw, kwargs[_kw])
        self._config = {}

    def execute(self, *data, **kwargs):
        """
        Execute the processing step.
        """
        raise NotImplementedError('Execute method has not been implemented.')

    @staticmethod
    def check_if_plugin():
        return True

    @staticmethod
    def has_unique_parameter_config_widget():
        return False

    def parameter_config_widget(self):
        raise NotImplementedError('Generic plugins do not have a unique'
                                  ' parameter config widget.')


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    plugin_type = INPUT_PLUGIN
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_params(
        get_generic_parameter('use_roi'),
        get_generic_parameter('roi_xlow'),
        get_generic_parameter('roi_xhigh'),
        get_generic_parameter('roi_ylow'),
        get_generic_parameter('roi_yhigh'),
        get_generic_parameter('use_thresholds'),
        get_generic_parameter('threshold_low'),
        get_generic_parameter('threshold_high'),
        get_generic_parameter('binning'))
    default_params = BasePlugin.default_params.get_copy()

class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    plugin_type = PROC_PLUGIN


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """
    plugin_type = OUTPUT_PLUGIN
