# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
This module includes the ParameterCollectionMixIn class which can be used to extend
class functionality to make simplified use of the pydidas ParameterCollection.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterCollectionMixIn"]


from numbers import Integral
from typing import Union

from numpy import mod

from pydidas.core.exceptions import UserConfigError
from pydidas.core.parameter import Parameter
from pydidas.core.parameter_collection import ParameterCollection


class ParameterCollectionMixIn:
    """
    MixIn class with ParameterCollection convenience methods.

    The ParameterCollectionMixIn class will create the generic .params attribute
    to be used. It will not overwrite existing params attributes.
    """

    default_params = ParameterCollection()

    def __init__(self):
        if not hasattr(self, "params"):
            self.params = ParameterCollection()
        if not isinstance(self.params, ParameterCollection):
            raise TypeError(
                "The class has a .params attribute which is not a ParameterCollection. "
                "The ParameterCollectionMixIn class requires an instance of "
                "ParameterCollection."
            )

    @classmethod
    def get_default_params_copy(cls) -> ParameterCollection:
        """
        Get a copy of the default ParameterCollection.

        Returns
        -------
        ParameterCollection
            A copy of the default ParameterCollection.
        """
        return cls.default_params.copy()

    @property
    def param_values(self) -> dict:
        """
        Get the values of all stored Parameters along with their refkeys.

        Returns
        -------
        Dict
            The refkey, value pairs for all stored Parameters.
        """
        return self.get_param_values_as_dict()

    @property
    def param_keys(self) -> list[str]:
        """
        Get the keys of all stored Parameters.

        Returns
        -------
        list[str]
            The keys of all stored Parameters.
        """
        return list(self.params.keys())

    def add_param(self, param: Parameter):
        """
        Add a parameter to the ParameterCollection.

        This is a wrapper for the ParameterCollection.add_parameter method.

        Parameters
        ----------
        param : Parameter
            An instance of a Parameter object.
        """
        self.params.add_param(param)

    def update_params_from_init(self, *args: tuple, **kwargs: dict):
        """
        Update the Parameters from the given init args and kwargs.

        Parameters
        ----------
        *args : Tuple
            The input arguments.
        **kwargs : Dict
            The input keyword arguments.
        """
        self.add_params(*args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)

    def add_params(self, *params: tuple[Union[Parameter, dict, ParameterCollection]]):
        """
        Add parameters to the object.

        This method adds Parameters to the ParameterCollection of the object.
        Parameters can be either supplies as args or a ParameterCollection
        or dictionary in the form of <ref_key>: <Parameter>.
        This method is explicitly separate from the __init__ method to allow
        subclasses full control over args and kwargs.

        Parameters
        ----------
        *params : Tuple[Union[Parameter, dict, ParameterCollection]]
            Any Parameter or ParameterCollection
        """
        for _param in params:
            if isinstance(_param, Parameter):
                self.add_param(_param)
            elif isinstance(_param, ParameterCollection):
                self.params.update(_param)
            else:
                raise TypeError(
                    f'Cannot add object of type "{_param.__class__}" '
                    "to ParameterCollection."
                )

    def set_default_params(self):
        """
        Set default entries.

        This method will go through the supplied defaults iterable.
        If there are no entries for the Parameter keys, it will add a
        Parameter with default value.
        """
        for _key, _param in self.default_params.items():
            if _key not in self.params:
                self.add_param(_param.copy())

    def update_param_values_from_kwargs(self, **kwargs: dict):
        """
        Update the Parameter values corresponding to the given keys.

        Parameters
        ----------
        **kwargs : dict
            The dictionary with Parameter refkeys and values.
        """
        for _key, _val in kwargs.items():
            if _key in self.params:
                self.set_param_value(_key, _val)

    def get_param_value(
        self,
        param_key: str,
        *default: object,
        dtype: Union[type, None] = None,
        for_export: bool = False,
    ) -> object:
        """
        Get a Parameter value.

        Parameters
        ----------
        param_key : str
            The key name of the Parameter.
        default : object
            The default value if the param_key does not exist.
        dtype : type, optional
            A datatype to convert the value into. If None, the native
            datatype is returned. The default is None.
        for_export : bool, optional
            An optional flag to force converting the Parameter value to an
            export-compatible format. This flag is not compatible with a specific
            dtype. The default is False.

        Returns
        -------
        object
            The value of the Parameter.
        """
        if param_key not in self.params:
            if len(default) == 1:
                return default[0]
            raise KeyError(
                f"No parameter with the name '{param_key}' has been registered."
            )
        if for_export:
            return self.params[param_key].value_for_export
        _val = self.params.get_value(param_key)
        if dtype is not None:
            _val = dtype(_val)
        return _val

    def get_param(self, param_key: str) -> Parameter:
        """
        Get a parameter.

        *Note*: This method returns the Parameter itself, *not* a copy.

        Parameters
        ----------
        param_key : str
            The key name of the Parameter.

        Returns
        -------
        Parameter
            The Parameter object.
        """
        self._check_key(param_key)
        return self.params[param_key]

    def get_params(self, *param_keys: tuple[str, ...]) -> list[Parameter]:
        """
        Get multiple parameters based on their reference keys.

        Parameters
        ----------
        *param_keys : Tuple[str, ...]
            Any number of reference keys.

        Returns
        -------
        list
            A list with the Parameter instances referenced by the supplied
            keys.
        """
        _params = []
        for _key in param_keys:
            self._check_key(_key)
            _params.append(self.params[_key])
        return _params

    def set_param_value(self, param_key: str, value: object):
        """
        Set a parameter value.

        Parameters
        ----------
        param_key : str
            The key name of the Parameter.
        value : object
            The value to be set. This has to be the datatype associated with
            the Parameter.
        """
        self._check_key(param_key)
        self.params.set_value(param_key, value)

    def set_param_values(self, **kwargs: dict):
        """
        Set multiple parameter values at once.

        Parameters
        ----------
        **kwargs : dict
            The reference key and value pairs for all Parameters to be set.
        """
        _wrong_keys = [_key for _key in kwargs if _key not in self.params]
        if _wrong_keys:
            raise KeyError(
                "The following keys are not registered with "
                f"{self.__class__.__name__}: " + ", ".join(_wrong_keys)
            )
        for _key, _val in kwargs.items():
            self.params.set_value(_key, _val)

    def get_param_values_as_dict(self, filter_types_for_export: bool = False) -> dict:
        """
        Get a dictionary with Parameter names and values only.

        Parameters
        ----------
        filter_types_for_export : bool
            Flag to return objects in types suitable for exporting (i.e. pickleable).

        Returns
        -------
        name_val_pairs : dict
            The dictionary with Parameter <name>: <value> pairs.
        """
        name_val_pairs = {
            _key: (_param.value_for_export if filter_types_for_export else _param.value)
            for _key, _param in self.params.items()
        }
        return name_val_pairs

    def set_param_values_from_dict(self, value_dict: dict):
        """
        Set the Parameter values from a dict with name, value paris.

        Parameters
        ----------
        value_dict : dict
            The dictionary with the stored information.
        """
        for _key, _value in value_dict.items():
            if _key in self.params:
                self.set_param_value(_key, _value)

    def get_param_keys(self) -> list[str]:
        """
        Get the keys of all registered Parameters.

        Returns
        -------
        list
            The keys of all registered Parameters.
        """
        return list(self.params.keys())

    def print_param_values(self):
        """
        Print the name and value of all Parameters.
        """
        _config = self.get_param_values_as_dict()
        for _key in _config:
            print(f"{_key}: {_config[_key]}")

    def _get_param_value_with_modulo(
        self, param_refkey: str, modulo: float, none_low: bool = True
    ) -> float:
        """
        Get a Parameter value modulo another value.

        This method applies a modulo to a Parameter value, referenced by its
        refkey, for example for converting image sizes of -1 to the actual
        detector dimensions. None keys can be converted to zero or the modulo,
        depending on the settings of "none_low".
        Note: This method only returns the modulated value and does not update
        the Parameter itself.

        Parameters
        ----------
        param_refkey : str
            The reference key for the selected Parameter.
        modulo : float
            The mathematical modulo to be applied.
        none_low : bool, optional
            Keyword to define the behaviour of None values. If True, None
            will be interpreted as 0. If False, None will be interpreted as
            the modulo range.

        Raises
        ------
        ValueError
            If the datatype of the selected Parameter is not integer.

        Returns
        -------
        _val : int
            The modulated Parameter value
        """
        _param = self.get_param(param_refkey)
        if _param.dtype is not Integral:
            raise ValueError(
                f"The datatype of Parameter *{_param.refkey}* is not integer."
            )
        if _param.value == modulo:
            return _param.value
        if _param.value is None:
            return modulo * (not none_low)
        _val = mod(_param.value, modulo)
        # create offset for negative indices to capture the whole array
        _offset = 1 if _param.value < 0 else 0
        return _val + _offset

    def restore_all_defaults(self, confirm: bool = False):
        """
        Restore the default values to all entries.

        Parameters
        ----------
        confirm : bool
            Confirmation flag as safety feature.
        """
        if not confirm:
            raise UserConfigError("Restoration of defaults not confirmed. Aborting.")
        for _key in self.params.keys():
            self.params[_key].restore_default()

    def _check_key(self, key: str):
        """
        Check a key exists.

        Parameters
        ----------
        key : str
            The name of the Parameter reference key.

        Raises
        ------
        KeyError
            If the key does not exist.
        """
        if key not in self.params:
            raise KeyError(
                f"The key {key} is not registered with {self.__class__.__name__}!"
            )
