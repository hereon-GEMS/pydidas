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
__all__ = ['BasePlugin']


from pydidas.core import (ParameterCollection, ObjectWithParameterCollection,
                          get_generic_parameter)
from pydidas.constants import (BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                               OUTPUT_PLUGIN)


ptype = {BASE_PLUGIN: 'Base plugin',
         INPUT_PLUGIN: 'Input plugin',
         PROC_PLUGIN: 'Processing plugin',
         OUTPUT_PLUGIN: 'Output plugin'}
data_dim = {i: str(i) for i in range(20)}
data_dim.update({None: 'None', -1: 'any'})


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
    generic_params = ParameterCollection(get_generic_parameter('label'))
    input_data_dim = -1
    output_data_dim = -1

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
        _doc = (cls.__doc__.strip() if cls.__doc__ is not None
                else 'No docstring available')
        _desc = (f'Plugin name: {cls.plugin_name}\n'
                 f'Class name: {cls.__name__}\n'
                 f'Plugin type: {ptype[cls.plugin_type]}\n\n'
                 f'Input data dimension: {data_dim[cls.input_data_dim]}\n\n'
                 f'Output data dimension: {data_dim[cls.output_data_dim]}\n\n'
                 f'Plugin description:\n{_doc}\n\n'
                 'Parameters:')
        for param in cls.generic_params.values():
            _desc += f'\n{param}'
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
        _doc = (cls.__doc__.strip() if cls.__doc__ is not None
                else 'No docstring available')
        return {'Name': cls.plugin_name,
                'Class name': cls.__name__,
                'Plugin type': ptype[cls.plugin_type],
                'Input data dimension': data_dim[cls.input_data_dim],
                'Output data dimension': data_dim[cls.output_data_dim],
                'Plugin description': _doc,
                'Parameters': '\n'.join(
                    [str(param) for param in cls.generic_params.values()]
                    + [str(param) for param in cls.default_params.values()])}

    def __init__(self, *args, **kwargs):
        """Setup the class."""
        super().__init__()
        if self.plugin_type not in [BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                                    OUTPUT_PLUGIN]:
            raise ValueError('Unknown value for the plugin type')
        self.add_params(self.generic_params.get_copy())
        self.add_params(*args)
        self.set_default_params()
        for _kw in kwargs:
            if _kw in self.params.keys():
                self.set_param_value(_kw, kwargs[_kw])
        self._config = {'input_shape': None,
                        'result_shape': None}

    def execute(self, data, **kwargs):
        """
        Execute the processing step.
        """
        raise NotImplementedError('Execute method has not been implemented.')

    def pre_execute(self):
        """
        Run code which needs to be run only once prior to the execution of
        multiple frames.
        """

    @property
    def has_unique_parameter_config_widget(self):
        """
        Get the flag whether the Plugin has a unique ParameterConfigWidget

        Returns
        -------
        bool
            The flag value-
        """
        return False

    def get_parameter_config_widget(self):
        """
        Get the unique ParameterConfigWidget associated to this Plugin.

        This method is useful if the configuration widget should have any
        non-standard items, e.g. sliders or interactive capability.

        Raises
        ------
        NotImplementedError
            This method is not implemented in the BasePlugin and needs to be
            implemented in the concrete subclass, if required.

        Returns
        -------
        QtWidgets.QWidget
            The unique ParameterConfig widget
        """
        raise NotImplementedError('Generic plugins do not have a unique'
                                  ' parameter config widget.')

    @property
    def input_shape(self):
        """
        Get the shape of the Plugin's input.

        Returns
        -------
        Union[tuple, None]
            The shape of the plugin's input.
        """
        return self._config['input_shape']

    @input_shape.setter
    def input_shape(self, new_shape):
        """
        The the shape of the Plugin's input.

        Parameters
        ----------
        new_shape : tuple
            The new shape of the Plugin's input data. The dimensionality of
            new_shape must match the defined input_data_dim.

        Returns
        -------
        Union[tuple, None]
            The shape of the plugin's input.
        """
        if not isinstance(new_shape, tuple):
            raise TypeError('The new shape must be a tuple.')
        if self.input_data_dim > 0 and len(new_shape) != self.input_data_dim:
            raise ValueError('The new shape must be a tuple of length'
                             f'{self.input_data_dim}.')
        self._config['input_shape'] = new_shape

    @property
    def result_shape(self):
        """
        Get the shape of the plugin result.

        Any plugin that knows the shape of its results will return the value
        as a tuple with one entry for every dimension.
        If a Plugin knows the dimensionality of its results but not the size
        of each dimension, a -1 is returned for each unknown dimension.

        Unknown dimensions are represented as -1 value.

        Returns
        -------
        tuple
            The shape of the results.
        """
        self.calculate_result_shape()
        return self._config['result_shape']

    def calculate_result_shape(self):
        """
        Calculate the shape of the results based on the Plugin processing and
        the input data shape.

        This method only updates the shape and stores it internally. Use the
        "result_shape" property to access the Plugin's result_shape. The
        generic implementation assumes the output shape to be equal to the
        input shape.
        """
        if self.output_data_dim == -1:
            self._config['result_shape'] = self._config['input_shape']
            return
        _shape = self._config.get('input_shape', None)
        if _shape is None:
            self._config['result_shape'] = (-1,) * self.output_data_dim
        else:
            self._config['result_shape'] = _shape
