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
The ParameterCollection class is a dictionary with support for pydidas Parameters.

The ParameterCollection extends the standard dictionary with additional methods to
get and set values of Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ParameterCollection"]


from collections.abc import Iterable
from itertools import chain
from typing import List, Self, Union

from pydidas.core.parameter import Parameter


class ParameterCollection(dict):
    """
    Ordered collection of parameters, implemented as subclass of dict.

    The ParameterCollection is a dictionary for Parameter instances
    with additional convenience routines to easily get and set Parameter
    values.
    Items can be added at instantiation either as single Parameters,
    ParameterCollections or as keyword arguments. Keywords will be converted
    to keys for the associated Parameters.

    Parameters
    ----------
    *args : Union[Parameter, ParameterCollection]
        Any number of Parameter or ParameterCollection instances
    **kwargs : dict
        Any number of Parameters
    """

    def __init__(self, *args: tuple):
        super().__init__()
        self.add_params(*args)

    def __copy__(self) -> Self:
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
        _copy = ParameterCollection()
        for _param in self.values():
            _new_param = Parameter(*_param.dump())
            _copy.add_param(_new_param)
        return _copy

    def __hash__(self) -> int:
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

    def __setitem__(self, key: str, param: Parameter):
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
                f'The dictionary key "{key}" for Parameter "{param}" does not'
                ' match the Parameter reference key: "{param.refkey}". Cannot'
                " add item."
            )
        self.__check_key_available(param)
        super().__setitem__(key, param)

    @staticmethod
    def __raise_type_error(item: object):
        """
        Raise a TypeError that item is of wrong type.

        Parameters
        ----------
        item : object
            Any item.

        Raises
        ------
        TypeError
            Error message that object cannot be added to ParameterCollection.
        """
        raise TypeError(
            f"Cannot add object *{item}* of type {item.__class__} to the "
            "ParameterCollection."
        )

    def __check_key_available(
        self, param: Parameter, keys: Union[Iterable[str, ...], None] = None
    ):
        """
        Check if the Parameter refkey is already a registered key.

        Parameters
        ----------
        param : Parameter
            The Parameter to be compared.
        keys : Union[Iterable[str, ...], None], optional
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

    def add_param(self, param: Parameter):
        """
        Add a parameter to the ParameterCollection.

        Parameters
        ----------
        param : Parameter
            An instance of a Parameter object.

        Raises
        ------
        TypeError
            If the passed param argument is not a Parameter instance.
        KeyError
            If an entry with param.refkey already exists.
        """
        if not isinstance(param, Parameter):
            self.__raise_type_error(param)
        self.__check_arg_types(param)
        self.__check_key_available(param)
        self.__setitem__(param.refkey, param)

    def __check_arg_types(self, *args: tuple):
        """
        Check the types of input arguments.

        This method verifies that all passed arguments are either Parameters
        or ParameterCollections.

        Parameters
        ----------
        *args : tuple
            Any arguments.
        """
        for _param in args:
            if not isinstance(_param, (Parameter, ParameterCollection)):
                self.__raise_type_error(_param)

    def add_params(self, *args: tuple[Parameter, Self, dict]):
        """
        Add parameters to the ParameterCollection.

        This method adds Parameters to the ParameterCollection.
        Parameters can be either supplies individually as arguments or as
        ParameterCollections or dictionaries.

        Parameters
        ----------
        *args : tuple[Parameter, dict, ParameterCollection]
            Any dict, Parameter or ParameterCollection
        """
        # perform all type checks before adding any items:
        self.__check_arg_types(*args)
        self.__check_duplicate_keys(*args)
        self.__add_arg_params(*args)

    def __check_duplicate_keys(self, *args: tuple[Union[dict, Parameter, Self]]):
        """
        Check for duplicate keys and raise an error if a duplicate key is found.

        This method compares the reference key of all args with the dictionary
        keys.

        Parameters
        ----------
        *args : tuple[Union[dict, Parameter, Self]
            Any number of Parameters or ParameterCollections.

        Raises
        ------
        KeyError
            If the kwargs key of a Parameter differs from the Parameter
            reference key.
        """
        # flatten arguments and add them to a list
        _flattened_params = list(
            chain.from_iterable(
                [p] if isinstance(p, Parameter) else list(p.values()) for p in args
            )
        )
        _original_keys = tuple(self.keys())
        for _param in _flattened_params:
            _other_keys = tuple(p.refkey for p in _flattened_params if p is not _param)
            _temp_keys = _original_keys + _other_keys
            self.__check_key_available(_param, keys=_temp_keys)

    def __add_arg_params(self, *args: tuple[Parameter, Self]):
        """
        Add the passed parameters to the ParameterCollection.

        Parameters
        ----------
        *args : tuple[Parameter, Self]
            The single Parameters or ParameterCollections to be added.
        """
        for _item in args:
            if isinstance(_item, Parameter):
                self.add_param(_item)
            elif isinstance(_item, ParameterCollection):
                self.update(_item)

    def delete_param(self, key: str):
        """
        Remove a Parameter from the ParameterCollection.

        This method is a wrapper for the intrinsic dict.__delitem__ method.

        Parameters
        ----------
        key : str
            The key of the dictionary entry to be removed.
        """
        self.__delitem__(key)

    def copy(self) -> Self:
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

    def deepcopy(self) -> Self:
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

    def get_value(self, param_key: str) -> object:
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
        object
            The value of the Parameter object in its native data type.
        """
        return self.__getitem__(param_key).value

    def set_value(self, param_key: str, value: object):
        """
        Update the value of a stored parameter.

        This method will verify that the entry exists and update the
        stored value.

        Parameters
        ----------
        param_key : str
            The reference key to the parameter in the dictionary.
        value : object
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

    def get_params(self, *keys: tuple) -> List[Parameter]:
        """
        Get multiple keys from an iterable.

        Parameters
        ----------
        keys : tuple
            The reference keys for all Parameters to be returned.

        Returns
        -------
        list
            A list of the Parameters.
        """
        _items = []
        for _key in keys:
            _items.append(self.__getitem__(_key))
        return _items

    def values_equal(self, *args: tuple) -> bool:
        """
        Compare all Parameters references by their keys in args and check
        if they have the same value.

        Parameters
        ----------
        *args : tuple
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
                raise KeyError(f"No Parameter with the key {_arg} has been registered.")
            _vals.add(self.get_value(_arg))
        if len(_vals) == 1:
            return True
        return False
