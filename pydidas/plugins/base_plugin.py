# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BasePlugin"]


import copy
from numbers import Integral
from typing import Self, Union

import numpy as np
from qtpy import QtCore

from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import (
    Dataset,
    ObjectWithParameterCollection,
    ParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import BASE_PLUGIN, INPUT_PLUGIN, OUTPUT_PLUGIN, PROC_PLUGIN
from pydidas.core.utils import rebin2d
from pydidas.data_io.utils import RoiSliceManager
from pydidas.managers import ImageMetadataManager


ptype = {
    BASE_PLUGIN: "Base plugin",
    INPUT_PLUGIN: "Input plugin",
    PROC_PLUGIN: "Processing plugin",
    OUTPUT_PLUGIN: "Output plugin",
}

_TYPES_NOT_TO_COPY = (
    QtCore.SignalInstance,
    QtCore.QMetaObject,
    ParameterCollection,
    ImageMetadataManager,
)

EXP = DiffractionExperimentContext()
SCAN = ScanContext()


def _data_dim(entry):
    if entry is None:
        return "None"
    if entry == -1:
        return "any"
    if isinstance(entry, Integral) and entry >= 0:
        return str(entry)
    raise TypeError("Entry type not understood.")


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
    plugin_name : str
        The plugin name key in human-readable form for referencing the plugin.
    default_params : ParameterCollection, optional
        A ParameterCollection with the class parameters which are required to use the
        plugin. The default is an empty ParameterCollection.
    generic_params : ParameterCollection, optional
        A ParameterCollection with the generic parameters for all plugins of a specific
        type. The default are the Parameters "keep_results" and "label" for all plugins.
    input_data_dim : int, optional
        The dimensionality of the input data. Use -1 for arbitrary dimensionality or
        None if the plugin does not accept any input data. The default is -1.
    output_data_dim : int, optional
        The dimensionality of the output data. Use -1 for arbitrary dimensionality or
        None if the plugin does not create any output data. The default is -1.
    output_data_label : str, optional
        The label for the output Dataset. The default is an empty string.
    output_data_unit : str, optional
        The unit of the output Dataset. The default is an empty string.
    new_dataset : bool
        Keyword that the Plugin creates a new dataset. This will trigger a
        re-evaluation of the output data shape.
    has_unique_parameter_config_widget : bool, optional
        Flag to use a unique ParameterConfigWidget for this plugin. The widget must be
        made accessible through the "get_parameter_config_widget" method. the default
        is False.
    advanced_parameters : list[str, ...], optional
        A list with the keys of "advanced parameters". These Parameters are hidden in
        the plugin's Parameter configuration widget be default and can be accessed
        through the associated button for "advances parameters" not to overwhelm
        users with too many options. The default is an empty list [].
    """

    basic_plugin = True
    plugin_type = BASE_PLUGIN
    plugin_name = "Base plugin"
    default_params = ParameterCollection()
    generic_params = get_generic_param_collection("keep_results", "label")

    input_data_dim = -1
    output_data_dim = -1
    output_data_label = ""
    output_data_unit = ""
    new_dataset = False
    has_unique_parameter_config_widget = False
    advanced_parameters = []

    @classmethod
    def get_class_description(cls) -> str:
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
        _doc = (
            cls.__doc__.strip() if cls.__doc__ is not None else "No docstring available"
        )
        _desc = (
            f"Plugin name: {cls.plugin_name}\n\n"
            f"Plugin description:\n{_doc}\n\n"
            "Parameters:"
        )
        for param in cls.generic_params.values():
            _desc += f"\n{param}"
        for param in cls.default_params.values():
            _desc += f"\n{param}"
        _desc += (
            f"Class name: {cls.__name__}\n\n"
            f"Plugin type: {ptype[cls.plugin_type]}\n\n"
            f"Input data dimension: {cls.input_data_dim_str()}\n\n"
            f"Output data dimension: {cls.output_data_dim_str()}\n"
        )
        return _desc

    @classmethod
    def get_class_description_as_dict(cls) -> dict:
        """
        Get a description of the plugin as a dictionary of entries.

        This method can generate a description of the plugin with name,
        plugin type, class name and Parameters and the docstring.
        The return is a dictionary of entries.

        Returns
        -------
        dict
            The description of the plugin.
        """
        _doc = (
            cls.__doc__.strip() if cls.__doc__ is not None else "No docstring available"
        )
        return {
            "Name": cls.plugin_name,
            "Plugin description": _doc,
            "Parameters": "\n".join(
                [str(param) for param in cls.generic_params.values()]
                + [str(param) for param in cls.default_params.values()]
            ),
            "Class name": cls.__name__,
            "Plugin type": ptype[cls.plugin_type],
            "Input data dimension": cls.input_data_dim_str(),
            "Output data dimension": cls.output_data_dim_str(),
        }

    @classmethod
    def input_data_dim_str(cls) -> str:
        """
        Get the input data dimensionality as string.

        Returns
        -------
        str
            The formatted input data dimensionality.
        """
        if cls.input_data_dim == -1:
            return "n"
        return str(cls.input_data_dim)

    @classmethod
    def output_data_dim_str(cls) -> str:
        """
        Get the output data dimensionality as string.

        Returns
        -------
        str
            The formatted input data dimensionality.
        """
        if cls.output_data_dim == -1:
            return "n"
        if cls.output_data_dim is None:
            return "None"
        return str(cls.output_data_dim)

    def __init__(self, *args, **kwargs):
        super().__init__()
        if self.plugin_type not in [
            BASE_PLUGIN,
            INPUT_PLUGIN,
            PROC_PLUGIN,
            OUTPUT_PLUGIN,
        ]:
            raise ValueError("Unknown value for the plugin type")
        self.add_params(self.generic_params.copy(), *args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)
        for _kw, _item in kwargs.items():
            if _kw in self.params.keys():
                self.set_param_value(_kw, _item)
        self._config = {"input_shape": None, "result_shape": None, "input_data": None}
        self._legacy_image_ops_meta = {"num": 0, "included": False}
        self._legacy_image_ops = []
        self._original_input_shape = None
        self.node_id = None
        self._roi_data_dim = None

    def __copy__(self) -> Self:
        """
        Implement a (deep)copy routine for Plugins.

        Returns
        -------
        BasePlugin
            The copy of the plugin.
        """
        _obj_copy = type(self)()
        _obj_copy.__dict__.update(
            {
                _key: copy.copy(_value)
                for _key, _value in self.__dict__.items()
                if not isinstance(_value, _TYPES_NOT_TO_COPY)
            }
        )
        for _key, _param in self.params.items():
            _obj_copy.set_param_value(_key, _param.value)
        if hasattr(self, "_EXP") and self._EXP == EXP:
            _obj_copy._EXP = EXP
        if hasattr(self, "_SCAN") and self._SCAN == SCAN:
            _obj_copy._SCAN = SCAN
        return _obj_copy

    def __deepcopy__(self, memo: dict) -> Self:
        """
        Create a deep copy of the Plugin.

        Parameters
        ----------
        memo : dict
            The dictionary of already copied objects.

        Returns
        -------
        BasePlugin
            The deep copy of the plugin.
        """
        return self.__copy__()

    def __getstate__(self) -> dict:
        """
        Get the state of the Plugin for pickling.

        Returns
        -------
        dict
            A dictionary with Parameter refkeys and the associated values.
        """
        _state = {
            _key: _value
            for _key, _value in self.__dict__.items()
            if not isinstance(_value, (QtCore.SignalInstance, QtCore.QMetaObject))
        }
        return _state

    def __setstate__(self, state: dict):
        """
        Set the Plugin state after pickling.

        Parameters
        ----------
        state : dict
            A state dictionary for restoring the object.
        """
        for key, val in state.items():
            setattr(self, key, val)

    def __reduce__(self) -> tuple:
        """
        Allow picking of classes dynamically loaded through the PluginCollection.

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

        return plugin_getter, (self.__class__.__name__,), self.__getstate__()

    def copy(self) -> Self:
        """
        Create a copy of itself.

        Returns
        -------
        BasePlugin :
            The plugin's copy.
        """
        return copy.copy(self)

    def execute(self, data: Union[int, Dataset], **kwargs: dict):
        """
        Execute the processing step.

        Parameters
        ----------
        data : Union[int, Dataset]
            The input data to be processed.
        kwargs : dict
            Keyword arguments passed to the processing.
        """
        raise NotImplementedError("Execute method has not been implemented.")

    def pre_execute(self):
        """
        Run the pre-execution code before processing individual datapoints.
        """

    def get_parameter_config_widget(self):
        """
        Get the unique configuration widget associated with this Plugin.

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
        raise NotImplementedError(
            "Generic plugins do not have a unique parameter config widget."
        )

    @property
    def input_data(self) -> Union[int, Dataset]:
        """
        Get the current input data.

        Returns
        -------
        Union[int, pydidas.core.Dataset]
            The input data passed to the plugin.
        """
        return self._config["input_data"]

    @property
    def result_data_label(self) -> str:
        """
        Get the combined result data label, consisting of the formatted
        output_data_label and output_data_unit.

        Returns
        -------
        str
            The formatted data label.
        """
        return self.output_data_label + (
            f" / {self.output_data_unit}" if len(self.output_data_unit) > 0 else ""
        )

    @property
    def result_title(self) -> str:
        """
        Get the formatted title of the plugin's results.

        Returns
        -------
        str
            The formatted result title.
        """
        _id = self.node_id if self.node_id is not None else -1
        return (
            f"{self.get_param_value('label')} (node #{_id:03d})"
            if len(self.get_param_value("label")) > 0
            else f"[{self.plugin_name}] (node #{_id:03d})"
        )

    def store_input_data_copy(self, data: Dataset, **kwargs: dict):
        """
        Store a copy of the input data internally in the plugin.

        Parameters
        ----------
        data : Union[int, np.ndarray]
            The input data for the plugin.
        **kwargs : dict
            The calling keyword arguments
        """
        self._config["input_data"] = copy.deepcopy(data)
        self._config["input_kwargs"] = copy.deepcopy(kwargs)

    @property
    def input_shape(self) -> Union[tuple, None]:
        """
        Get the shape of the Plugin's input.

        Returns
        -------
        Union[tuple, None]
            The shape of the plugin's input.
        """
        return self._config["input_shape"]

    @input_shape.setter
    def input_shape(self, new_shape: tuple[int, ...]):
        """
        Set the shape of the Plugin's input.

        Parameters
        ----------
        new_shape : tuple
            The new shape of the Plugin's input data. The dimensionality of
            new_shape must match the defined input_data_dim.

        Returns
        -------
        Union[tuple[int, ...], None]
            The shape of the plugin's input.
        """
        if not isinstance(new_shape, tuple):
            raise UserConfigError(
                f"Error when updating the input shape of plugin\n\t{self.plugin_name}:"
                f"\nThe new shape must be a tuple, but received {new_shape} which is "
                f"of type {type(new_shape)}."
            )
        if self.input_data_dim is None:
            raise UserConfigError(
                f"Error when updating the input shape of plugin\n\t{self.plugin_name}:"
                "\nThe plugin is an input plugin and cannot accept any input. This is "
                "due to an incorrect and inconsistent workflow tree. Please check the "
                "full workflow."
            )
        if 0 < self.input_data_dim != len(new_shape):
            raise UserConfigError(
                f"Error when updating the input shape of plugin\n\t{self.plugin_name}:"
                f"\nThe new shape must be a tuple of length {self.input_data_dim} but "
                f"received a tuple of length {len(new_shape)}."
            )
        self._config["input_shape"] = new_shape

    @property
    def result_shape(self) -> Union[tuple, None]:
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
        Union[tuple, None]
            The shape of the results with a value for each dimension. Unknown
            dimensions are represented as -1 value. If no result shape has been
            calculated yet, return None.
        """
        return self._config["result_shape"]

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
            self._config["result_shape"] = self._config["input_shape"]
            return
        _shape = self._config.get("input_shape", None)
        if _shape is None:
            self._config["result_shape"] = (-1,) * self.output_data_dim
        else:
            self._config["result_shape"] = _shape

    def apply_legacy_image_ops_to_data(self, data: np.ndarray) -> np.ndarray:
        """
        Apply the legacy image operations to a new data frame.

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
        _num = self._legacy_image_ops_meta["num"]
        if self._legacy_image_ops_meta["included"] and _num > 0:
            self._legacy_image_ops = self._legacy_image_ops[:-_num]
            self._legacy_image_ops_meta["num"] = 0
        if self.get_param_value("use_roi", False):
            self._legacy_image_ops.append(["roi", self._get_own_roi()])
            self._legacy_image_ops_meta["num"] += 1
        _bin = self.get_param_value("binning", 1)
        if _bin != 1:
            self._legacy_image_ops.append(["binning", _bin])
            self._legacy_image_ops_meta["num"] += 1
        self._legacy_image_ops_meta["included"] = True

    def _get_own_roi(self) -> Union[tuple[slice, slice], None]:
        """
        Get the ROI defined within the plugin.

        Note: This method will not check whether the Plugin has the required
        Parameters to define a ROI. This check must be performed by the user
        or calling method.

        Returns
        -------
        Union[tuple[slice. slice], None]
            The tuple with two slice objects which define the image ROI.
        """
        _roi_data_dim = (
            self._roi_data_dim
            if self._roi_data_dim is not None
            else self.output_data_dim
        )
        if _roi_data_dim == 1:
            _roi_bounds = (
                self.get_param_value("roi_xlow"),
                self.get_param_value("roi_xhigh"),
            )
            _dim = 1
        elif _roi_data_dim == 2:
            _roi_bounds = (
                self.get_param_value("roi_ylow"),
                self.get_param_value("roi_yhigh"),
                self.get_param_value("roi_xlow"),
                self.get_param_value("roi_xhigh"),
            )
            _dim = 2
        else:
            raise UserConfigError(
                "The Plugin does not have the correct data dimensionality to define a "
                "ROI."
            )
        _roi = RoiSliceManager(roi=_roi_bounds, input_shape=self.input_shape, dim=_dim)
        return _roi.roi

    def get_single_ops_from_legacy(self) -> tuple[tuple[slice, ...], int]:
        """
        Get the parameters for a single ROI and binning operation.

        This method combines all legacy operations on the data into one set of
        operations to be applied.

        Returns
        -------
        roi : tuple[slice, ...]
            The ROI which needs to be applied to the original image.
        binning : int
            The binning factor which needs to be applied to the original image.
        """
        if self.input_data_dim == 1:
            return self.__get_legacy_op_for_1d_input()
        else:
            return self.__get_legacy_op_for_2d_input()

    def __get_legacy_op_for_1d_input(self) -> tuple[slice, int]:
        """
        Get a single operation that converts the raw input to the input shape.

        Returns
        -------
        roi : tuple[slice, slice]
            The ROI which needs to be applied to the original image.
        binning : int
            The binning factor which needs to be applied to the original image.
        """
        _roi = RoiSliceManager(
            roi=(0, self._original_input_shape[0]),
            input_shape=self._original_input_shape,
            dim=1,
        )
        _binning = 1
        _all_ops = self._legacy_image_ops[:]
        while len(_all_ops) > 0:
            _op_name, _op = _all_ops.pop(0)
            if _op_name == "binning":
                _x = int(_roi.roi[1].stop - _roi.roi[1].start)
                _dx = int(((_x // _binning) % _op) * _binning)
                _tmproi = (0, _x - _dx)
                _roi.apply_second_roi(_tmproi)
                _binning *= _op
            if _op_name == "roi":
                _roi_unbinned = [
                    _binning * _r for _r in RoiSliceManager(roi=_op, dim=1).roi_coords
                ]
                _roi.apply_second_roi(_roi_unbinned)
        return _roi.roi, _binning

    def __get_legacy_op_for_2d_input(self) -> tuple[tuple[slice, ...], int]:
        """
        Get a single operation that converts the raw input to the input shape.

        Returns
        -------
        roi : tuple[slice, ...]
            The ROI which needs to be applied to the original image.
        binning : int
            The binning factor which needs to be applied to the original image.
        """
        _roi = RoiSliceManager(
            roi=(0, self._original_input_shape[0], 0, self._original_input_shape[1]),
            input_shape=self._original_input_shape,
        )
        _binning = 1
        _all_ops = self._legacy_image_ops[:]
        while len(_all_ops) > 0:
            _op_name, _op = _all_ops.pop(0)
            if _op_name == "binning":
                _y = int(_roi.roi[0].stop - _roi.roi[0].start)
                _x = int(_roi.roi[1].stop - _roi.roi[1].start)
                _dy = int(((_y // _binning) % _op) * _binning)
                _dx = int(((_x // _binning) % _op) * _binning)
                _tmproi = (0, _y - _dy, 0, _x - _dx)
                _roi.apply_second_roi(_tmproi)
                _binning *= _op
            if _op_name == "roi":
                _roi_unbinned = [
                    _binning * _r for _r in RoiSliceManager(roi=_op).roi_coords
                ]
                _roi.apply_second_roi(_roi_unbinned)
        return _roi.roi, _binning
