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


from pydidas.core import ParameterCollection, ObjectWithParameterCollection

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
    input_data = {}
    output_data = {}

    @classmethod
    def get_class_description(cls, return_list=False):
        """
        Get a description of the plugin.

        This method can generate a description of the plugin with name,
        plugin type, class name and parameters and the docstring.
        The default return is a formatted string but a list of entries can
        be created with the return_list keyword.

        Parameters
        ----------
        return_list : bool, optional
            Keyword to toggle return . The default is False.

        Returns
        -------
        _desc : str or list
            The descripion of the plugin.
        """
        _name = cls.__name__
        if return_list:
            _desc = [['Name', f'{cls.plugin_name}\n']]
            _desc.append(['Class name', f'{_name}\n'])
            _desc.append(['Plugin type', f'{ptype[cls.plugin_type]}\n'])
            _desc.append(['Plugin description', f'{cls.__doc__}\n'])
            pstr = ''
            for param in cls.parameters:
                pstr += f'\n{str(param)}'
            _desc.append(['Parameters', pstr[1:]])
        else:
            _desc = (f'Name: {cls.plugin_name}\n'
                     f'Class name: {_name}\n'
                     f'Plugin type: {ptype[cls.plugin_type]}\n\n'
                     f'Plugin description:\n{cls.__doc__}\n\n'
                     'Parameters:')
            for param in cls.parameters:
                _desc += f'\n{param}: {cls.parameters[param]}'
        return _desc

    def __init__(self, *args, **kwargs):
        """Setup the class."""
        super().__init__()
        if self.plugin_type not in [BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                                    OUTPUT_PLUGIN]:
            raise ValueError('Unknown value for the plugin type')
        self.add_params(*args)
        self.params = self.get_default_params_copy()
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
