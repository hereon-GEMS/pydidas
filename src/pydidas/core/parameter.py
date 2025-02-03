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
The parameter module includes the Parameter class which is used to have a
consistent interface for various data types.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Parameter"]


import copy
import warnings
from collections.abc import Iterable
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Self, Type, Union

from numpy import asarray, ndarray

from pydidas.core.exceptions import UserConfigError
from pydidas.core.hdf5_key import Hdf5key


_ITERATORS = (list, set, tuple)
_NUMBERS = [Integral, Real]


def _get_base_class(cls: Any) -> Union[type, Real, Integral, None]:
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
        The base class of the input class if the input.
    """
    if cls is None:
        return None
    if issubclass(cls, Integral):
        return Integral
    if issubclass(cls, Real):
        return Real
    return cls


def _outside_range_string(val: object, parameter: object) -> str:
    if parameter.dtype == Integral:
        _range = (int(parameter.range[0]), int(parameter.range[1]))
    else:
        _range = parameter.range
    return (
        f"The new value `{val}` is outside of the specified range for the "
        f"Parameter `{parameter.refkey}`. The valid range is: {_range}."
    )


def _invalid_choice_str(val: object, choices: list) -> str:
    return (
        f"The selected value '{val}' does not correspond to any of the allowed "
        f"choices: {choices}"
    )


def _value_set_valueerror_str(parameter: object, val: object) -> str:
    _subtype = (
        f"[{parameter._Parameter__meta['subtype'].__name__}]"
        if parameter._Parameter__meta["subtype"]
        else ""
    )
    return (
        f"Cannot set Parameter (object ID:{id(parameter)}, refkey: '{parameter.refkey}', "
        f"name: '{parameter.name}) because it is of the wrong data type. "
        f"(expected: {parameter.dtype}({_subtype}), input type: {type(val)})"
    )


class Parameter:
    """
    A class used for storing a value and associated metadata.

    The Parameter has the following properties which can be accessed.
    Only the value and choices properties can be edited at runtime, all other
    properties are fixed at instantiation.

    +------------+-----------+-------------------------------------------+
    | property   | editable  | description                               |
    +============+===========+===========================================+
    | refkey     | False     | A reference key for the Parameter.        |
    |            |           | This key is used for accessing the        |
    |            |           | Parameter in the ParameterCollection      |
    +------------+-----------+-------------------------------------------+
    | dtype      | False     | The datatype of the Parameter value.      |
    |            |           | This must be a base class or None.        |
    |            |           | If None, no type-checking is performed.   |
    +------------+-----------+-------------------------------------------+
    | value      | True      | The current value.                        |
    +------------+-----------+-------------------------------------------+
    | choices    | True      | A list with choices if the value of the   |
    |            |           | parameter is limited to specific values.  |
    +------------+-----------+-------------------------------------------+
    | range      | True      | The range of allowed values. The range    |
    |            |           | is only supported for numerical datatypes.|
    |            |           | The range must be given as a 2-tuple with |
    |            |           | the lower and upper bound.                |
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
    | subtype    | False     | For Iterable datatypes, a subtype can be  |
    |            |           | defined to determine the data type inside |
    |            |           | the iterating object, e.g. a list of int. |
    +------------+-----------+-------------------------------------------+

    Parameters can be passed either as a complete meta_dict or as individual
    keyword arguments. The meta_dict will take precedence.

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
        A dictionary with metadata. Any keys specified as meta will
        overwrite the kwargs dictionary. This is added merely as
        convenience to facility copying Parameter instances. If None,
        this entry will be ignored. The default is None.
    **kwargs : dict
        Additional keyword arguments. Supported argument

        name : str, optional
            The name of the parameter. The default is None.
        subtype : Optional[type]
            For Iterable datatypes, a subtype can be defined to determine the
            data type inside the iterating object, e.g. a list of int. None does
            not enforce type checking. The default is None.
        optional : bool, optional
            Keyword to toggle optional parameters. The default is False.
        tooltip : str, optional
            A description of the parameter. It will be automatically extended
            to include certain type and unit information. The default is ''.
        unit : str, optional
            The unit of the parameter. The default is ''.
        choices : Union[list, tuple, None]
            A list of allowed choices. If None, no checking will be enforced.
            The default is None.
        value : object
            The value of the parameter. This parameter should only be used
            to restore saved parameters.
        allow_None : bool, optional
            Keyword to allow None instead of the usual datatype. The default
            is False.
    """

    def __init__(
        self,
        refkey: str,
        param_type: Union[None, Type],
        default: object,
        meta: Union[None, dict] = None,
        **kwargs: dict,
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
            range=None,
            subtype=_get_base_class(kwargs.get("subtype", None)),
        )
        self.__process_default_input(default)
        self.__process_choices_input(kwargs)
        self.value = kwargs.get("value", self.__meta["default"])
        if kwargs.get("range", None):
            self.range = kwargs["range"]

    def __process_default_input(self, default: object):
        """
        Process the default value.

        Parameters
        ----------
        default : object
            The default attribute passed to init.

        Raises
        ------
        TypeError
            If the default value is not of the demanded data type.
        """
        default = self.__convenience_type_conversion(default)
        if not self.__typecheck(default):
            raise TypeError(
                f"Default value `{default}` does not have data type `{self.__type}`!"
            )
        self.__meta["default"] = default

    def __process_choices_input(self, kwargs: dict):
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
            If the default has been set, and it is not in choices.
        """
        _choices = kwargs.get("choices", None)
        if not (isinstance(_choices, (list, tuple, set)) or _choices is None):
            raise TypeError(
                f"The type of choices (type: `{type(_choices)}`"
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
        Check the type of new input.

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
        if isinstance(val, _ITERATORS) and self.__meta["subtype"] in _NUMBERS:
            return all(isinstance(item, self.__meta["subtype"]) for item in val)
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
            - str input of list/tuple of numbers to list/tuple of numbers
            - list to tuple
            - tuple to list
            - "None" and "" to None

        Parameters
        ----------
        value : object
            The input value. This can be any datatype entered by the user.

        Returns
        -------
        value : object
            The value with the above-mentioned type conversions applied.
        """
        if self.__meta["allow_None"] and value in ["None", "", None]:
            return None
        if isinstance(value, str):
            if self.__type == Path:
                value = Path(value)
            elif self.__type == Hdf5key:
                value = Hdf5key(value)
            elif self.__type in _ITERATORS and self.__meta["subtype"] in _NUMBERS:
                value = self.__get_as_numbers(value)
        if self.__type in _NUMBERS and not self.__meta["allow_None"]:
            try:
                value = float(value) if self.__type == Real else int(value)
            except ValueError:
                pass
            finally:
                return value
        if (
            isinstance(value, Iterable)
            and self.__type in _ITERATORS
            and not isinstance(value, str)
        ):
            if self.__meta["subtype"] in _NUMBERS:
                value = self.__get_as_numbers(value)
            return self.__type(value)
        if isinstance(value, Iterable) and self.__type == ndarray:
            return asarray(value)
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
        Return the parameter reference key.

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
        if self.dtype == Integral:
            _t += " (type: integer)"
        elif self.dtype == Real:
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
    def choices(self) -> Union[None, list]:
        """
        Get or set the allowed choices for the Parameter value.

        Returns
        -------
        Union[list, None]
            The allowed choices for the Parameter.
        """
        return self.__meta["choices"]

    @choices.setter
    def choices(self, choices: Union[None, list, tuple, set]):
        """
        Update the allowed choices of a Parameter.

        Parameters
        ----------
        choices : Union[None, list, tuple, set]
            A list or tuple of allowed choices. A check will be performed that
            all entries correspond to the defined data type and that the
            current parameter value is one of the allowed choices.

        Raises
        ------
        TypeError
            If the supplied choices are not of datatype list or tuple.
        ValueError
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
        set a new value for the parameter.

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

        if (
            self.__type in _NUMBERS
            and self.__meta["range"] is not None
            and val is not None
        ):
            if not self.__meta["range"][0] <= val <= self.__meta["range"][1]:
                raise UserConfigError(_outside_range_string(val, self))
        if self.__meta["choices"] and val not in self.__meta["choices"]:
            raise ValueError(_invalid_choice_str(val, self.__meta["choices"]))
        if not (self.__typecheck(val) or (self.__meta["optional"] and val is None)):
            raise ValueError(_value_set_valueerror_str(self, val))
        self.__value = val

    @property
    def value_for_export(self) -> object:
        """
        Get the value in a pickleable format for exporting.

        Note that this method does not work with Parameters without a defined
        data type.

        Returns
        -------
        object
            The Parameter value in a pickleable format.
        """
        if self.value is None:
            return None
        if self.__type in (str, Hdf5key, Path):
            return str(self.value)
        if self.__type == Integral:
            return int(self.value)
        if self.__type == Real:
            return float(self.value)
        if self.__type in (tuple, list, dict):
            return self.value
        if self.__type == ndarray:
            return self.value.tolist()
        raise TypeError(f"No export format for type {self.__type} has been defined.")

    @property
    def range(self) -> Union[None, tuple[Real, Real]]:
        """
        Get the range of the Parameter.

        Returns
        -------
        tuple[Real, Real]
            The range of the Parameter.
        """
        return self.__meta["range"]

    @range.setter
    def range(self, new_range: Union[None, tuple[Real, Real]]):
        """
        Set a new range for the Parameter.

        Parameters
        ----------
        new_range : Union[None, tuple[Real, Real]]
            The new range for the Parameter.

        Raises
        ------
        ValueError
            If the new range is not a tuple of two numbers.
        """
        if self.__type not in _NUMBERS:
            raise UserConfigError(
                "The range attribute is only supported for numerical data types."
            )
        if self.__meta["choices"] and new_range is not None:
            raise UserConfigError(
                "Parameter range can only be set for numerical data types which do "
                "not have a defined set of choices."
            )
        if new_range is None:
            self.__meta["range"] = None
            return
        if len(new_range) != 2:
            raise UserConfigError("The new range must be a tuple of two numbers.")
        new_range = (float(new_range[0]), float(new_range[1]))
        self.__meta["range"] = new_range

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
        if self.__meta["range"] is not None:
            raise UserConfigError(
                "Choices are only valid if the Parameter does not have a range."
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
        A method to get a copy of the Parameter object.

        Returns
        -------
        Parameter
            A full copy of the object.
        """
        return Parameter(*self.dump())

    deepcopy = copy

    def dump(self) -> tuple:
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
        _meta.update({"value": copy.copy(self.__value)})
        del _meta["default"]
        _default = self.__meta["default"]
        if self.choices is not None and self.__meta["default"] not in self.choices:
            _default = self.value
        return self.__refkey, self.__type, _default, _meta

    def export_refkey_and_value(self) -> tuple:
        """
        Export the refkey and value (in a pickleable format) for saving
        in YAML files.

        Returns
        -------
        tuple
            The tuple of (refkey, value as pickleable format)
        """
        return self.__refkey, self.value_for_export

    def get_type_and_default_str(self, check_optional: bool = False) -> str:
        """
        Get a string representation of the type and default value.

        Parameters
        ----------
        check_optional : bool, optional
            A flag to print whether the Parameter is optional. The default is False.

        Returns
        -------
        str
            The string representation.
        """
        _type = f"{self.__type.__name__}" if self.__type is not None else "None"
        _unit = "" if self.__meta["unit"] == "" else f" {self.__meta['unit']}"
        _default_val = str(self.default) if len(str(self.default)) >= 0 else '""'
        _repr = f"(type: {_type}, "
        if check_optional and self.__meta["optional"]:
            _repr += "optional, "
        return _repr + f"default: {_default_val}{_unit})"

    def __str__(self) -> str:
        """
        Get a short string representation of the parameter.

        This method will return a short description of the Parameter in the
        format
        <Name>: <value> (type: <type>, default: <default> <unit>).

        Returns
        -------
        str
            The string of the short description.
        """
        return self.__get_string_repr()

    def __repr__(self) -> str:
        """
        Get the representation of the Parameter instance.

        Returns
        -------
        str
            The representation.
        """
        _repr = self.__get_string_repr(check_optional=True)
        return f"Parameter <{_repr}>"

    def __get_string_repr(self, check_optional: bool = False) -> str:
        """
        Get a short string representation of the Parameter.

        Parameters
        ----------
        check_optional : bool, optional
            A flag to print whether the Parameter is optional. The default is False.

        Returns
        -------
        str
            The string representation.
        """
        _unit = "" if self.__meta["unit"] == "" else f" {self.__meta['unit']}"
        _val = str(self.value) if len(str(self.value)) > 0 else '""'
        return f"{self.__refkey}: {_val}{_unit} " + self.get_type_and_default_str(
            check_optional
        )

    def __get_as_numbers(
        self, value: Union[str, Iterable]
    ) -> Union[list[Real, Integral], tuple[Real, Integral], set[Real, Integral]]:
        """
        Get the input as an iterable of numbers of the specified type.
        Parameters
        ----------
        value : Union[str, Iterable]
            The input object.

        Returns
        -------
        Union[list[Real, Integral], tuple[Real, Integral], set[Real, Integral]]
            The input as an iterable of numbers.
        """
        if self.__meta["subtype"] not in _NUMBERS:
            raise TypeError("The subtype must be either Real or Integral.")
        __converter = float if self.__meta["subtype"] == Real else int
        if isinstance(value, str):
            value = [
                item
                for item in value.strip("{[(}])").split(",")
                if len(item.strip()) > 0
            ]
        try:
            value = [__converter(item) for item in value]
        except ValueError:
            pass
        return self.__type(value)

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
                if isinstance(_item, ndarray):
                    _val = hash(_item.tobytes())
                else:
                    _val = hash(_item)
                _hash_vals.append(_val)
            except TypeError:
                warnings.warn(
                    f'Could not hash "{_item}". The hash value for '
                    "the Parameter might not be accurate."
                )
        return hash(tuple(_hash_vals))
