# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
The ParameterCollection class is a dictionary with support for pydidas Parameters.

The ParameterCollection extends the standard dictionary with additional methods to
get and set values of Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterCollection"]


import copy as copy_module
from collections.abc import Collection
from typing import Any, NoReturn

from pydidas.core.parameter import Parameter
from pydidas.core.utils.iterable_utils import flatten


class ParameterCollection(dict):
    """
    An ordered collection of parameters, implemented as subclass of dict.

    The ParameterCollection is a dictionary for Parameter instances
    with additional convenience routines to easily get and set Parameter
    values.
    Items can be added at instantiation either as single Parameters,
    ParameterCollections or as keyword arguments. Keywords will be converted
    to keys for the associated Parameters.

    Parameters
    ----------
    *args : Parameter or ParameterCollection
        Any number of Parameter or ParameterCollection instances
    """

    def __init__(self, *args: "Parameter | ParameterCollection") -> None:
        super().__init__()
        self.add_params(*args)  # type: ignore[arg-type]

    # ----------------------------
    # Re-implemented dict methods:
    # ----------------------------

    def __copy__(self) -> "ParameterCollection":
        """
        Get a copy of the ParameterCollection.

        This method will return a copy of the ParameterCollection with
        a copy of each Parameter object. Note that there is no difference between
        a ParameterCollections copy and deepcopy.

        Returns
        -------
        _copy : ParameterCollection
            The copy of ParameterCollection with no shared objects.
        """
        _copy = self.__class__.__new__(self.__class__)
        dict.__init__(_copy)
        for _param in self.values():
            _new_param = Parameter(*_param.dump())
            _copy.add_param(_new_param)
        # Preserve __dict__ references (for shallow copy semantics)
        for _key, _val in self.__dict__.items():
            _copy.__dict__[_key] = copy_module.copy(_val)
        return _copy

    def __deepcopy__(self, memo: dict) -> "ParameterCollection":
        """
        Get a deep copy of the ParameterCollection.

        This method will return a copy of the ParameterCollection with
        a copy of each Parameter object. Note that there is no difference between
        a ParameterCollections copy and deepcopy.

        Parameters
        ----------
        memo : dict
            A dictionary to track already copied objects.

        Returns
        -------
        _copy : ParameterCollection
            The deep copy of ParameterCollection with no shared objects.
        """
        _copy = self.__class__.__new__(self.__class__)
        dict.__init__(_copy)
        for _param in self.values():
            _new_param = Parameter(*_param.dump())
            _copy.add_param(_new_param)
        # Preserve and deep copy __dict__ attributes
        for _key, _val in self.__dict__.items():
            _copy.__dict__[_key] = copy_module.deepcopy(_val, memo)
        return _copy

    def __hash__(self) -> int:  # type: ignore[override]
        """
        Create a hash value for the ParameterCollection.

        This hash value is based on the hashed values of the dictionary keys
        and values.

        Returns
        -------
        int
            The hash value.
        """
        _keys = tuple(hash(_key) for _key in self.keys())
        _values = tuple(hash(_val) for _val in self.values())
        return hash((_keys, _values))

    def __setitem__(self, key: str, param: Parameter) -> None:
        """
        Assign a value to a dictionary key.

        This method overloads the regular dict.__setitem__ method with
        additional type and reference key checks.

        Parameters
        ----------
        key : str
            The dictionary key.
        param : Parameter
            The value / object to be added to the dictionary.

        Raises
        ------
        TypeError
            If the param argument is not a Parameter object.
        KeyError
            If the dictionary key differs from the Parameter reference key.
        """
        if not isinstance(param, Parameter):
            self.__raise_type_error(param)
        if key != param.refkey:
            raise KeyError(
                f"The dictionary key `{key}` for Parameter `{param}` does not "
                "match the Parameter reference key: `{param.refkey}`. The "
                "Parameter cannot be added to the ParameterCollection: Both keys "
                "must be identical."
            )
        self.__check_key_available(param)
        super().__setitem__(key, param)

    def __getitem__(self, key: str) -> Parameter:
        """
        Get the requested Parameter

        Parameters
        ----------
        key : str
            The reference key.

        Returns
        -------
        Parameter
            The requested Parameter.
        """
        return super().__getitem__(key)

    # ----------------------------
    # New public methods:
    # ----------------------------

    @property
    def param_keys(self) -> list[str]:
        """
        Get the Parameter reference keys of the ParameterCollection.

        Returns
        -------
        list[str]
            The Parameter reference keys in a list.
        """
        return list(self.keys())

    def add_param(self, param: Parameter, force_replace: bool = False) -> None:
        """
        Add a parameter to the ParameterCollection.

        Parameters
        ----------
        param : Parameter
            An instance of a Parameter object.
        force_replace : bool, optional
            Flag whether to replace an existing entry with the same reference
            key. This allows to handle generic dict operations (e.g. when
            calling copy) to bypass the key check.

        Raises
        ------
        TypeError
            If the passed param argument is not a Parameter instance.
        KeyError
            If an entry with the param.refkey already exists.
        """
        if not isinstance(param, Parameter):
            self.__raise_type_error(param)
        self.__check_arg_types(param)
        if not force_replace:
            self.__check_key_available(param)
        super().__setitem__(param.refkey, param)

    def add_params(self, *args: "Parameter | ParameterCollection") -> None:
        """
        Add parameters to the ParameterCollection.

        This method adds Parameters to the ParameterCollection.
        Parameters can be either supplied individually as arguments or as
        ParameterCollections.

        Parameters
        ----------
        *args : Parameter or ParameterCollection
            Any Parameter or ParameterCollection
        """
        # perform all type checks before adding any items:
        self.__check_arg_types(*args)  # type: ignore[arg-type]
        self.__check_duplicate_keys(*args)  # type: ignore[arg-type]
        for _item in args:  # type: ignore[arg-type]
            if isinstance(_item, Parameter):
                super().__setitem__(_item.refkey, _item)
            elif isinstance(_item, ParameterCollection):
                self.update(_item)

    def delete_param(self, key: str) -> None:
        """
        Remove a Parameter from the ParameterCollection.

        This method is a wrapper for the intrinsic dict.__delitem__ method.

        Parameters
        ----------
        key : str
            The key of the dictionary entry to be removed.
        """
        self.__delitem__(key)

    def copy(self) -> "ParameterCollection":
        """
        Get a copy of the ParameterCollection.

        This method will return a copy of the ParameterCollection with
        a copy of each Parameter object.

        Returns
        -------
        ParameterCollection
            The copy of ParameterCollection with no shared objects.
        """
        return self.__copy__()

    def deepcopy(self) -> "ParameterCollection":
        """
        Get a deep copy of the ParameterCollection.

        This method will return a copy of the ParameterCollection with
        a copy of each Parameter object. Note that there is no difference between
        a ParameterCollections copy and deepcopy since Parameter objects are
        immutable value objects.

        Returns
        -------
        ParameterCollection
            The deep copy of ParameterCollection with no shared objects.
        """

        return self.__deepcopy__({})

    def get_value(self, param_key: str) -> Any:
        """
        Get the value of a stored parameter.

        This method will verify that the entry exists and returns its value
        in its native type.

        Parameters
        ----------
        param_key : str
            The reference key to the parameter in the dictionary.

        Returns
        -------
        Any
            The value of the Parameter in its native data type.
        """
        return self.__getitem__(param_key).value

    def set_value(self, param_key: str, value: Any) -> None:
        """
        Update the value of a stored parameter.

        This method will verify that the entry exists and update the
        stored value.

        Parameters
        ----------
        param_key : str
            The reference key to the parameter in the dictionary.
        value : Any
             The new value for the Parameter. Note that type-checking is
             performed in the Parameter value setter.

        Raises
        ------
        KeyError
            If the key "param_key" is not registered.
        """
        _item = self.__getitem__(param_key)
        _item.value = value

    def get_param(self, param_key: str) -> Parameter:
        """
        Get a Parameter from the ParameterCollection.

        Parameters
        ----------
        param_key : str
            The Parameter key.

        Returns
        -------
        Parameter
            The Parameter instance.
        """
        return self.__getitem__(param_key)

    def get_params(self, *keys: str) -> list[Parameter]:
        """
        Get a list of Parameters from multiple keys.

        Parameters
        ----------
        keys : str
            The reference keys for all Parameters to be returned.

        Returns
        -------
        list[Parameter]
            A list of the Parameters.
        """
        _items = []
        for _key in keys:
            _items.append(self.__getitem__(_key))
        return _items

    def values_equal(self, *args: str) -> bool:
        """
        Compare all Parameters references by their keys in args and check
        if they have the same value.

        Parameters
        ----------
        *args : str
            Any number of Parameter keys.

        Raises
        ------
        KeyError
            If any of the Parameter reference keys have not been registered
            with the ParameterCollection.

        Returns
        -------
        bool
            Flag whether all Parameters have identical values or not.
        """
        _vals = set()
        for _arg in args:
            if _arg not in self.keys():
                _msg = f"No Parameter with the key {_arg} has been registered."
                raise KeyError(_msg)
            _vals.add(self.get_value(_arg))
        if len(_vals) == 1:
            return True
        return False

    # ----------------------------
    # Private methods:
    # ----------------------------

    @staticmethod
    def __raise_type_error(*items: Any) -> NoReturn:
        """
        Raise a TypeError that item is of the wrong type.

        Parameters
        ----------
        *items : Any
            Any item(s) (which cannot be added to the ParameterCollection).

        Raises
        ------
        TypeError
            Error message that object cannot be added to ParameterCollection.
        """
        _invalids = "\n".join(
            f"- `{item}` of type `{item.__class__}`" for item in items
        )
        raise TypeError(
            "Only Parameter or ParameterCollection instances are supported in the "
            "ParameterCollection. The following items are invalid:\n." + _invalids
        )

    def __check_key_available(
        self, param: Parameter, keys: Collection[str] | None = None
    ) -> None | NoReturn:
        """
        Check if the Parameter refkey is already a registered key.

        Parameters
        ----------
        param : Parameter
            The Parameter to be compared.
        keys : Collection[str] or None, optional
            The keys to be compared against. If None, the comparison will be
            performed against all dictionary keys. The default is None.

        Raises
        ------
        KeyError
            If the key already exists in keys.
        """
        if keys is None:
            keys = self.keys()
        if param.refkey in keys:
            raise KeyError(
                f"A parameter with the reference key '{param.refkey}' already exists."
            )

    def __check_arg_types(self, *args: Any) -> None:
        """
        Check the types of input arguments.

        This method verifies that all passed arguments are either Parameters
        or ParameterCollections.

        Parameters
        ----------
        *args : Any
            Any arguments.
        """
        _are_params = [
            isinstance(arg, (Parameter, ParameterCollection)) for arg in args
        ]
        _valid = all(_are_params)
        if not _valid:
            _invalid = [arg for arg, is_param in zip(args, _are_params) if not is_param]
            self.__raise_type_error(*_invalid)

    def __check_duplicate_keys(self, *args: "Parameter | ParameterCollection") -> None:
        """
        Check for duplicate keys and raise an error if a duplicate key is found.

        This method compares the reference key of all args with the dictionary
        keys.

        Parameters
        ----------
        *args : Parameter or ParameterCollection
            Any number of Parameters or ParameterCollections
            with key: Parameter pairs.

        Raises
        ------
        KeyError
            If the kwargs key of a Parameter differs from the Parameter
            reference key.
        """
        _flattened_params = flatten(  # type: ignore[arg-type]
            [_arg] if isinstance(_arg, Parameter) else list(_arg.values())
            for _arg in args  # type: ignore[arg-type]
        )
        _original_keys = tuple(self.keys())
        for _param in _flattened_params:
            _other_keys = tuple(p.refkey for p in _flattened_params if p is not _param)
            _temp_keys = _original_keys + _other_keys
            self.__check_key_available(_param, keys=_temp_keys)
