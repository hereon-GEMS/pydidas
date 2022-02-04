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
Module with the BasePlugin base class from which all plugins must inherit.
Direct inheritance from BasePlugin is limited to the InputPlugin, ProcPlugin
and OutputPlugin base classes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BasePlugin']

import copy
from numbers import Integral

from pydidas.core import (ParameterCollection, ObjectWithParameterCollection,
                          get_generic_parameter)
from pydidas.image_io import rebin2d, RoiController
from pydidas.core.constants import (BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                               OUTPUT_PLUGIN)


ptype = {BASE_PLUGIN: 'Base plugin',
         INPUT_PLUGIN: 'Input plugin',
         PROC_PLUGIN: 'Processing plugin',
         OUTPUT_PLUGIN: 'Output plugin'}


def _data_dim(entry):
    if entry is None:
        return 'None'
    if entry == -1:
        return 'any'
    if isinstance(entry, Integral) and entry >= 0:
        return str(entry)
    raise TypeError('Entry type not understood.')


class BasePlugin(ObjectWithParameterCollection):
    """
    The base plugin class from which all plugins inherit.

    Class attributes are used in the descriptions of individual plugins and
    all these attributes should be re-defined in individual plugins to
    prevent falling back to the base class attributes:

    basic_plugin : bool
        A keyword to mark basic plugin classes.
    plugin_type : int
        A key to discriminate between the different types of plugins
        (input, processing, output)
    default_params : ParameterCollection
        A ParameterCollection with the class parameters which are required
        to perform the execute operation.
    generic_params : ParameterCollection
        A ParameterCollection with the generic parameters for all plugins of
        a specific type.
    input_data_dim : int
        The dimensionality of the input data. Use -1 for arbitraty
        dimensionality.
    output_data_dim : int
        The dimensionality of the output data. Use -1 for arbitraty
        dimensionality.
    new_dataset : bool
        Keyword that the Plugin creates a new dataset. This will trigger a
        re-evaluation of the output data shape.
    """
    basic_plugin = True
    plugin_type = BASE_PLUGIN
    plugin_name = 'Base plugin'
    default_params = ParameterCollection()
    generic_params = ParameterCollection(get_generic_parameter('label'))
    input_data_dim = -1
    output_data_dim = -1
    new_dataset = False

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
        _desc = (f'Plugin name: {cls.plugin_name}\n\n'
                 f'Plugin description:\n{_doc}\n\n'
                 'Parameters:')
        for param in cls.generic_params.values():
            _desc += f'\n{param}'
        for param in cls.default_params.values():
            _desc += f'\n{param}'
        _desc += (f'Class name: {cls.__name__}\n\n'
                  f'Plugin type: {ptype[cls.plugin_type]}\n\n'
                  f'Input data dimension: {_data_dim(cls.input_data_dim)}\n\n'
                  f'Output data dimension: {_data_dim(cls.output_data_dim)}\n')
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
                'Plugin description': _doc,
                'Parameters': '\n'.join(
                    [str(param) for param in cls.generic_params.values()]
                    + [str(param) for param in cls.default_params.values()]),
                'Class name': cls.__name__,
                'Plugin type': ptype[cls.plugin_type],
                'Input data dimension': _data_dim(cls.input_data_dim),
                'Output data dimension': _data_dim(cls.output_data_dim)}

    def __init__(self, *args, **kwargs):
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
        self._legacy_image_ops_meta = {'num': 0, 'included': False}
        self._legacy_image_ops = []
        self._original_image_shape = None
        self.node_id = None

    def __copy__(self):
        """
        Implement a (deep)copy routine for Plugins.

        Returns
        -------
        BasePlugin
            The copy of the plugin.
        """
        _obj_copy = type(self)()
        for _key in self.__dict__:
            _obj_copy.__dict__[_key] = copy.copy(self.__dict__[_key])
        return _obj_copy

    def __getstate__(self):
        """
        Get the state of the Plugin for pickling.

        Returns
        -------
        dict
            A dictionary with Parameter refkeys and the associated values.
        """
        _state = self.__dict__.copy()
        return _state

    def __setstate__(self, state):
        """
        Set the Plugin state after pickling.

        Parameters
        ----------
        state : dict
            A state dictionary for restoring the object.
        """
        for key, val in state.items():
            setattr(self, key, val)

    def __reduce__(self):
        """
        Redefine the __reduce__ method to allow picking of classes dynamically
        loaded through the PluginCollection.

        Returns
        -------
        plugin_getter : callable
            The callable function to create a new instance.
        tuple
            The arguments for plugin_getter. This is only the class name.
        dict
            The state to set the state of the new object.
        """
        from .plugin_getter_ import plugin_getter
        return (plugin_getter, (self.__class__.__name__,), self.__getstate__())

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
        pass

    @property
    def has_unique_parameter_config_widget(self):
        """
        Get the flag whether the Plugin has a unique ParameterConfigWidget

        Returns
        -------
        bool
            The flag value whether the plugin has a unique configuration
            widget associated with it.
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

        Note that this property will always perform an update of the value
        before returning a result.

        Any plugin that knows the shape of its results will return the value
        as a tuple with one entry for every dimension.
        If a Plugin knows the dimensionality of its results but not the size
        of each dimension, a -1 is returned for each unknown dimension.

        Returns
        -------
        tuple
            The shape of the results with a value for each dimension. Unknown
            dimensions are represented as -1 value.
        """
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

    def apply_legacy_image_ops_to_data(self, data):
        """
        Apply the legacy image operations to a new data frame and return the
        updated data.

        Parameters
        ----------
        data : np.ndarray
            The input data frame.

        Returns
        -------
        new_data : np.ndarray
            The updated data frame with ROI and binning applied.
        """
        self.update_legacy_image_ops_with_this_plugin()
        _roi, _binning = self.get_single_ops_from_legacy()
        _new_data = rebin2d(data[_roi], _binning)
        return _new_data

    def update_legacy_image_ops_with_this_plugin(self):
        """
        Update the legacy image operations list with any ROI and binning
        operations performed in this plugin.
        """
        _num = self._legacy_image_ops_meta['num']
        if (self._legacy_image_ops_meta['included'] and _num > 0):
            self._legacy_image_ops = self._legacy_image_ops[:-_num]
            self._legacy_image_ops_meta['num'] = 0
        if self.get_param_value('use_roi', False):
            self._legacy_image_ops.append(['roi', self._get_own_roi()])
            self._legacy_image_ops_meta['num'] += 1
        _bin = self.get_param_value('binning', 1)
        if _bin != 1:
            self._legacy_image_ops.append(['binning', _bin])
            self._legacy_image_ops_meta['num'] += 1
        self._legacy_image_ops_meta['included'] = True

    def _get_own_roi(self):
        """
        Get the ROI defined within the plugin.

        Note: This method will not check whether the Plugin has the required
        Parameters to define a ROI. This check must be performed by the user
        or calling method.

        Returns
        -------
        tuple
            The tuple with two slice objects which define the image ROI.
        """
        _roi = RoiController(roi=(self.get_param_value('roi_ylow'),
                               self.get_param_value('roi_yhigh'),
                               self.get_param_value('roi_xlow'),
                               self.get_param_value('roi_xhigh')),
                          input_shape=self.input_shape)
        return _roi.roi

    def get_single_ops_from_legacy(self):
        """
        Get the parameters for a single ROI and binning operation from
        combining all legacy operations on the data.

        Returns
        -------
        roi : tuple
            The ROI which needs to be applied to the original image.
        binning : int
            The binning factor which needs to be applied to the original image.
        """
        _roi = RoiController(roi=(0, self._original_image_shape[0],
                               0, self._original_image_shape[1]),
                          input_shape=self._original_image_shape)
        _binning = 1
        _all_ops = self._legacy_image_ops[:]
        while len(_all_ops) > 0:
            _op_name, _op = _all_ops.pop(0)
            if _op_name == 'binning':
                _y = int(_roi.roi[0].stop - _roi.roi[0].start)
                _x = int(_roi.roi[1].stop - _roi.roi[1].start)
                _dy = int(((_y // _binning) % _op) * _binning)
                _dx = int(((_x // _binning) % _op) * _binning)
                _tmproi = (0, _y - _dy, 0, _x - _dx)
                _roi.apply_second_roi(_tmproi)
                _binning *= _op
            if _op_name == 'roi':
                _roi_unbinned = [_binning * _r
                                 for _r in RoiController(roi=_op).roi_coords]
                _roi.apply_second_roi(_roi_unbinned)
        return _roi.roi, _binning
