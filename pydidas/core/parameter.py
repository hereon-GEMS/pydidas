# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The parameter module includes the Parameter class which is used to have a
consistent interface for various data types.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Parameter"]


import numbers
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Dict, List, Self, Set, Tuple, Type, Union

from .hdf5_key import Hdf5key


def _get_base_class(cls) -> type:
    """
    Filter numerical classes and return the corresponding abstract base class.

    This function checks whether cls is a numerical class and returns the
    numerical abstract base class from the numbers module for type-checking.
    Any other class will be returned.

    Parameters
    ----------
    cls : object
        The concrete class.

    Returns
    -------
    object
        The base class of the input class if the inpu.
    """
    if cls is None:
        return None
    if numbers.Integral.__subclasscheck__(cls):
        return numbers.Integral
    if numbers.Real.__subclasscheck__(cls):
        return numbers.Real
    return cls


class Parameter:
    """
    A class used for storing a value and associated metadata.

    The Parameter has the following properties which can be accessed.
    Only the value and choices properties can be edited at runtime, all other
    properties are fixed at instanciation.

    +------------+-----------+-------------------------------------------+
    | property   | editable  | description                               |
    +============+===========+===========================================+
    | refkey     | False     | A reference key for the Parameter.        |
    |            |           | This key is used for accessing the        |
    |            |           | Parameter in the ParameterCollection      |
    +------------+-----------+-------------------------------------------+
    | datatype   | False     | The datatype of the Parameter value.      |
    |            |           | This must be a base class or None.        |
    |            |           | If None, no type-checking is performed.   |
    +------------+-----------+-------------------------------------------+
    | value      | True      | The current value.                        |
    +------------+-----------+-------------------------------------------+
    | choices    | True      | A list with choices if the value of the   |
    |            |           | parameter is limited to specific values.  |
    +------------+-----------+-------------------------------------------+
    | name       | False     | A readable name as description.           |
    +------------+-----------+-------------------------------------------+
    | unit       | False     | The unit of the Parameter value.          |
    +------------+-----------+-------------------------------------------+
    | optional   | False     | A flag whether the parameter is required  |
    |            |           | or optional.                              |
    +------------+-----------+-------------------------------------------+
    | allow_None | False     | A flag whether "None" is accepted as      |
    |            |           | Parameter value.                          |
    +------------+-----------+-------------------------------------------+
    | tooltip    | False     | A readable tooltip.                       |
    +------------+-----------+-------------------------------------------+
    | default    | False     | The default value.                        |
    +------------+-----------+-------------------------------------------+

    Parameters can be passed either as a complete meta_dict or as individual
    keyword arguments. The meta_dict will take precendence.

    Parameters
    ----------
    refkey : str
        The reference key for the Parameter in the Parameter collection.
        If not specified, this will default to the name.
    param_type : Union[None, type]
        The datatype of the parameter. If None, no type-checking will be
        performed. If any integer or float value is used, this will be
        changed to the abstract base class of numbers.Integral or
        numbers.Real.
    default : Union[None, type]
        The default value. The data type must be of the same type as
        param_type. None is only accepted if param_type is None as well.
    meta : Union[dict, None], optional
        A dictionary with meta data. Any keys specified as meta will
        overwrite the kwargs dictionary. This is added merely as
        convenience to facility copying Parameter instances. If None,
        this entry will be ignored. The default is None.
    **kwargs : dict
        All optional parameters can be passed as keyword arguments.
    **name : str, optional
        The name of the parameter. The default is None.
    **optional : bool, optional
        Keyword to toggle optional parameters. The default is False.
    **tooltip : str, optional
        A description of the parameter. It will be automatically extended
        to include certain type and unit information. The default is ''.
    **unit : str, optional
        The unit of the parameter. The default is ''.
    **choices : Union[list, tuple, None]
        A list of allowed choices. If None, no checking will be enforced.
        The default is None.
    **value : type
        The value of the parameter. This parameter should only be used
        to restore saved parameters.
    **allow_None : bool, optional
        Keyword to allow None instead of the usual datatype. The default
        is False.
    """

    def __init__(
        self,
        refkey: str,
        param_type: Union[None, Type],
        default: object,
        meta: Union[None, Dict] = None,
        **kwargs: Dict,
    ):
        super().__init__()
        self.__refkey = refkey
        self.__type = _get_base_class(param_type)
        self.__value = None
        if isinstance(meta, dict):
            kwargs.update(meta)
        self.__meta = dict(
            tooltip=kwargs.get("tooltip", ""),
            unit=kwargs.get("unit", ""),
            optional=kwargs.get("optional", False),
            name=kwargs.get("name", ""),
            allow_None=kwargs.get("allow_None", False),
        )
        self.__process_default_input(default)
        self.__process_choices_input(kwargs)
        self.value = kwargs.get("value", self.__meta["default"])

    def __process_default_input(self, default: Type):
        """
        Process the default value.

        Parameters
        ----------
        default : Type
            The default attribute passed to init.

        Raises
        ------
        TypeError
            If the default value is not of the demanded data type.
        """
        default = self.__convenience_type_conversion(default)
        if not self.__typecheck(default):
            raise TypeError(
                f"Default value '{default}' does not have data type {self.__type}!"
            )
        self.__meta["default"] = default

    def __process_choices_input(self, kwargs: Dict):
        """
        Process the choices input.

        Parameters
        ----------
        kwargs : dict
            The kwargs passed to init.

        Raises
        ------
        TypeError
            If choices is not of an accepted type (None, list, tuple)
        ValueError
            If the default has been set and it is not in choices.
        """
        _choices = kwargs.get("choices", None)
        if not (isinstance(_choices, (list, tuple, set)) or _choices is None):
            raise TypeError(
                'The type of choices (type: "{type(_choices)}"'
                "is not supported. Please use list or tuple."
            )
        self.__meta["choices"] = None if _choices is None else list(_choices)
        _def = self.__meta["default"]
        if self.__meta["choices"] is not None and _def not in self.__meta["choices"]:
            raise ValueError(
                f"The default value '{_def}' does not correspond to any of the defined "
                f"choices: {self.__meta['choices']}."
            )

    def __typecheck(self, val: object) -> bool:
        """
        Check the type of a new input.

        Parameters
        ----------
        val : object
            The value of the parameter to be checked.

        Returns
        -------
        bool
            Returns True if the type of val matches the defined data type
            or if type is None.

        """
        if self.__type is None:
            return True
        if isinstance(val, self.__type):
            return True
        if val is None and self.__meta["allow_None"]:
            return True
        return False

    def __convenience_type_conversion(self, value: object) -> object:
        """
        Convert the value to the defined type.

        This method will take the input value and do some type checking and
        conversion.

        The following conversions are supported:

            - str input and Path type
            - str input and Hdf5key type
            - list to tuple
            - tuple to list

        Parameters
        ----------
        value : any
            The input value. This can be any datatype entered by the user.

        Returns
        -------
        value : any
            The value with the above mentioned type conversions applied.
        """
        if isinstance(value, str):
            if self.__type == Path:
                value = Path(value)
            elif self.__type == Hdf5key:
                value = Hdf5key(value)
        if self.__type == numbers.Real and not self.__meta["allow_None"]:
            return float(value)
        if isinstance(value, list) and self.__type == tuple:
            return tuple(value)
        if isinstance(value, tuple) and self.__type == list:
            return list(value)
        return value

    @property
    def name(self) -> str:
        """
        Return the parameter name.

        Returns
        -------
        str
            The parameter name.
        """
        return self.__meta["name"]

    @property
    def allow_None(self) -> bool:
        """
        Returns the flag to allow "None" as value.

        Returns
        -------
        bool
            The flag setting.
        """
        return self.__meta["allow_None"]

    @property
    def refkey(self) -> str:
        """
        Return the paramter reference key.

        Returns
        -------
        str
            The parameter reference key.
        """
        return self.__refkey

    @property
    def default(self) -> object:
        """
        Return the default value.

        Returns
        -------
        default
            The default value.
        """
        return self.__meta["default"]

    @property
    def unit(self) -> str:
        """
        Get the Parameter unit.

        Returns
        -------
        str
            The unit of the Parameter.
        """
        return self.__meta["unit"]

    @property
    def tooltip(self) -> str:
        """
        Get the Parameter tooltip.

        Returns
        -------
        str
            The tooltip for the Parameter.
        """
        _t = self.__meta["tooltip"]
        if self.unit:
            _t += f" (unit: {self.unit})"
        if self.dtype == numbers.Integral:
            _t += " (type: integer)"
        elif self.dtype == numbers.Real:
            _t += " (type: float)"
        elif self.dtype == str:
            _t += " (type: str)"
        elif self.dtype == Hdf5key:
            _t += " (type: Hdf5key)"
        elif self.dtype == Path:
            _t += " (type: Path)"
        else:
            _t += f" (type: {str(self.dtype)})"
        return _t.replace(") (", ", ")

    @property
    def choices(self) -> Union[None, List]:
        """
        Get or set the allowed choices for the Parameter value.

        Parameters
        ----------
        choices : Union[list, tuple, set]
            A list or tuple of allowed choices. A check will be performed that
            all entries correspond to the defined data type and that the
            curent parameter value is one of the allowed choices.

        Returns
        -------
        Union[list, None]
            The allowed choices for the Parameter.
        """
        return self.__meta["choices"]

    @choices.setter
    def choices(self, choices: Union[None, List, Tuple, Set]):
        """
        Update the allowed choices of a Parameter.

        Raises
        ------
        TypeError
            If the supplied choices are not of datatype list or tuple.
        ValueErrror
            If any choice in choices does not pass the datatype check.
        ValueError
            If the current Parameter value is not included in the list of
            new choices.
        """
        if choices is None:
            self.__meta["choices"] = None
            return
        if not isinstance(choices, (list, tuple, set)):
            raise TypeError("New choices must be a list, set or tuple.")
        for _c in choices:
            if not self.__typecheck(_c):
                raise ValueError(
                    f"The new choice '{_c}' does not have the correct data type."
                )
        if self.__value not in choices:
            raise ValueError(
                "The new choices do not include the current "
                f"Parameter value ({self.__value})"
            )
        self.__meta["choices"] = list(choices)

    @property
    def optional(self) -> bool:
        """
        Get the flag whether the parameter is optional or not.

        Returns
        -------
        bool
            The unit of the Parameter.
        """
        return self.__meta["optional"]

    @property
    def dtype(self) -> Type:
        """
        Get the data type of the Parameter value.

        Returns
        -------
        object
            The class of the parameter value data type.
        """
        return self.__type

    @property
    def value(self) -> object:
        """
        Get the Parameter value.

        Returns
        -------
        value
            The value of the parameter.
        """
        return self.__value

    @value.setter
    def value(self, val: object):
        """
        Set a new value for the parameter.

        Parameters
        ----------
        val : type
            The new value for the parameter.

        Raises
        ------
        ValueError
            Raised if the type of val does not correspond to the required
            datatype.
        """
        val = self.__convenience_type_conversion(val)
        if self.__meta["choices"] and val not in self.__meta["choices"]:
            raise ValueError(
                f"The selected value '{val}' does not correspond to any of the allowed "
                f"choices: {self.__meta['choices']}"
            )
        if not (self.__typecheck(val) or self.__meta["optional"] and (val is None)):
            _name = self.__meta["name"]
            raise ValueError(
                f"Cannot set Parameter (object ID:{id(self)}, refkey: '{self.__refkey}'"
                f", name: '{_name}') because it is of the wrong data type. (expected: "
                f"{self.__type}, input type: {type(val)}"
            )
        self.__value = val

    @property
    def value_for_export(self) -> object:
        """
        Get the value in a pickleable format for exporting.

        Note that this method does not work with Parameters without a defined
        data type.

        Returns
        -------
        Union[str, float, int]
            The Parameter value in a pickleable format.
        """
        if self.value is None:
            return None
        if self.__type in (str, Hdf5key, Path):
            return str(self.value)
        if self.__type == numbers.Integral:
            return int(self.value)
        if self.__type == numbers.Real:
            return float(self.value)
        if self.__type in (list, tuple, dict):
            return self.value
        raise TypeError(f"No export format for type {self.__type} has been defined.")

    def update_value_and_choices(self, value: object, choices: Iterable[object, ...]):
        """
        Update the value and choices of the Parameter to prevent illegal selections.

        Parameters
        ----------
        value : object
            The new Parameter values
        choices : Iterable[object, ...]
            The new choices for the Parameter.
        """
        if not self.__typecheck(value):
            raise ValueError(
                f"The new value '{value}' of type '{type(value)}' is of the wrong "
                f"type. Expected '{self.__type}'."
            )
        if value not in choices:
            raise ValueError("The new value must be included in the new choices.")
        self.__value = value
        self.choices = choices

    def restore_default(self):
        """
        Restore the parameter to its default value.
        """
        self.value = self.__meta["default"]

    def copy(self) -> Self:
        """
        A method to get the a copy of the Parameter object.

        Returns
        -------
        Parameter
            A full copy of the object.
        """
        return Parameter(*self.dump())

    deepcopy = copy

    def dump(self) -> Tuple:
        """
        A method to get the full class information for saving.

        Returns
        -------
        refkey : str
            The name of the Parameter
        type : type
            The data type of the Parameter.
        default : object
            The default value
        meta : dict
            A dictionary with all the metadata information about the Parameter
            (value, unit, tooltip, refkey, default, choices)
        """
        _meta = self.__meta.copy()
        _meta.update({"value": self.__value})
        del _meta["default"]
        _default = self.__meta["default"]
        if self.choices is not None and self.__meta["default"] not in self.choices:
            _default = self.value
        return (self.__refkey, self.__type, _default, _meta)

    def export_refkey_and_value(self) -> Tuple:
        """
        Export the refkey and value (in a pickleable format) for saving
        in YAML files.

        Returns
        -------
        tuple
            The tuple of (refkey, value as pickleable format)
        """
        return (self.__refkey, self.value_for_export)

    def __str__(self) -> str:
        """
        Get a short string representation of the parameter.

        This method will return a short description of the Parameter in the
        format
        <Name> - type: <type>, default: <default> <unit>.

        Returns
        -------
        str
            The string of the short description.
        """

        _type = f"{self.__type.__name__}" if self.__type is not None else "None"
        if self.__meta["allow_None"]:
            _type += "/None"
        _def = (
            f'{self.__meta["default"]}'
            if self.__meta["default"] not in (None, "")
            else "None"
        )
        _unit = f" {self.unit}" if self.unit else ""
        return (
            f"{self.refkey}: {self.value}{_unit} (type: {_type}, "
            f'default: {_def} {self.__meta["unit"]})'
        )

    def __repr__(self) -> str:
        """
        Get the representation of the Parameter instance.

        Returns
        -------
        str
            The representation.
        """
        _type = f"{self.__type.__name__}" if self.__type is not None else "None"
        _unit = (
            f'{self.__meta["unit"]} '
            if self.__meta["unit"] != ""
            else self.__meta["unit"]
        )
        _val = f"{self.value}" if self.value != "" else '""'
        _def = (
            f'{self.__meta["default"]}'
            if self.__meta["default"] not in (None, "")
            else "None"
        )
        _s = f"Parameter <{self.__refkey} (type: {_type}"
        if self.__meta["optional"]:
            _s += ", optional"
        _s += f"): {_val} {_unit}(default: {_def})>"
        return _s

    def __copy__(self) -> Self:
        """
        Copy the Parameter object.

        This method is a wrapper for the "copy" method to allow the generic
        Python copy module to make copies of Parameters as well.

        Returns
        -------
        Parameter
            A copy of the Parameter.
        """
        return self.copy()

    def __call__(self) -> object:
        """
        Get the stored Parameter value.

        Returns
        -------
        value
            The stored parameter value-
        """
        return self.__value

    def __hash__(self) -> int:
        """
        Get a hash value for the Parameter.

        The generated hash key depends on the reference key, type, value,
        default, name, unit and choices of the Parameter.

        Warning: In case of non-hashable values, the Parameter will still
        generate a hash value based on the other items but this value might
        not be representative because it cannot capture changing values.

        Returns
        -------
        int
            The hashed value for the Parameter.
        """
        _hash_vals = []
        _choices = (
            tuple() if self.__meta["choices"] is None else tuple(self.__meta["choices"])
        )
        for _item in [
            self.__refkey,
            self.__type,
            self.__value,
            self.__meta["default"],
            self.__meta["name"],
            self.__meta["unit"],
            _choices,
        ]:
            try:
                _val = hash(_item)
                _hash_vals.append(_val)
            except TypeError:
                warnings.warn(
                    f'Could not hash "{_item}". The hash value for '
                    "the Parameter might not be accurate."
                )
        return hash(tuple(_hash_vals))
