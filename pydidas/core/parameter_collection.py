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

"""
The parameter_collection module includes the ParameterCollection class which
is an dict implementation with additional methods to get and set
values of Parameters..
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterCollection']

from itertools import chain

from .parameter import Parameter

class ParameterCollection(dict):
    """
    Ordered collection of parameters, implemented as subclass of dict.

    The ParameterCollection is a dictionary for Parameter instances
    with additional convenience rountines to easily get and set Parameter
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
    def __init__(self, *args, **kwargs):
        """Setup method."""
        super().__init__()
        self.add_params(*args, **kwargs)

    def __copy__(self):
        return self.get_copy()

    def __setitem__(self, key, param):
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
            raise TypeError('Only Parameter objects are supported in a '
                            'ParameterCollection. Cannot add object '
                            f'"{param}".')
        if key != param.refkey:
            raise KeyError(f'The dictionary key "{key}" for Parameter '
                    f'"{param}" does not match the Parameter '
                    'reference key: "{param.refkey}". Cannot add item.')
        self.__check_key(param)
        super().__setitem__(key, param)

    @staticmethod
    def __raise_type_error(item):
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
        raise TypeError(f'Cannot add object "{item}" of type '
                        f'"{item.__class__}" to ParameterCollection.')

    def __add_arg_params(self, *args):
        """
        Add the passed parameters to the ParameterCollection.

        Parameters
        ----------
        *args : Union[Parameter, ParameterCollection]
            Single Parameters or ParameterCollections.

        Raises
        ------
        KeyError
            If the key for the Parameter is already in use.
        """
        if isinstance(args, ParameterCollection):
            self.update(args)
        else:
            for _param in args:
                if isinstance(_param, Parameter):
                    self.add_param(_param)
                elif isinstance(_param, (ParameterCollection)):
                    self.update(_param)

    def __add_kwarg_params(self, **kwargs):
        """
        Add the passed keyword parameters to the ParameterCollection.

        Parameters
        ----------
        **kwargs : dict
            A dictionary of keyword arguments.
        """
        for _key in kwargs:
            self.__setitem__(_key, kwargs[_key])

    def __check_arg_types(self, *args):
        """
        Check the types of input arguments.

        This method verifies that all passed arguments are either Parameters
        or ParameterCollections.

        This method
        Parameters
        ----------
        *args : any
            Any arguments.
        """
        for _param in args:
            if not isinstance(_param, (Parameter, ParameterCollection)):
                self.__raise_type_error(_param)

    def __check_kwarg_types(self, **kwargs):
        """
        Check the types of input keyword arguments.

        This method verifies that all passed arguments are either Parameters
        or ParameterCollections.

        Parameters
        ----------
        *kwargs : any
            Any keyword arguments.
        """
        for _key in kwargs:
            if not isinstance(kwargs[_key], Parameter):
                self.__raise_type_error(kwargs[_key])

    def __check_duplicate_keys(self, *args, **kwargs):
        """
        Check for duplicate keys and raise an error if a duplicate key is
        found.

        This method compares the reference key of all args with the dictionary
        keys. Then, it compares the keys of all keyword args with the
        dictionary and arg keys.

        Parameters
        ----------
        *args : Parameters
            Any number of Parameters.
        **kwargs : dict
            A dictionary with Parameter values.

        Raises
        ------
        KeyError
            If the kwargs key of a Parameter differs from the Parameter
            reference key.
        """
        # flatten ParameterCollection arguments and add them to a list
        _new_args = chain.from_iterable(
            [p] if isinstance(p, Parameter) else list(p.values())
            for p in args)
        for _param in _new_args:
            _newkeys = (tuple(self.keys())
                        + tuple(p.refkey for p in _new_args
                                if p is not _param))
            self.__check_key(_param, keys=_newkeys)
        _newkeys = tuple(self.keys()) + tuple(p.refkey for p in _new_args)
        for _key in kwargs:
            self.__check_key(kwargs[_key], keys=_newkeys)

    def __check_key(self, param, keys=None):
        """
        Check if the Parameter refkey is already a registed key.

        Parameters
        ----------
        param : Parameter
            The Parameter to be compared.
        keys : Union[tuple, list], optional
            The keys to be compared against. If None, the comparison will be
            performed against the dictionary keys. The default is None.

        Raises
        ------
        KeyError
            If the key already exists in keys.
        """
        if keys is None:
            keys = self.keys()
        if param.refkey in keys:
            raise KeyError('A parameter with the reference key '
                           f'"{param.refkey}" already exists.')

    def add_param(self, param):
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
        self.__check_arg_types(param)
        self.__check_key(param)
        self.__setitem__(param.refkey, param)

    def add_params(self, *args, **kwargs):
        """
        Add parameters to the ParameterCollection.

        This method adds Parameters to the ParameterCollection
        Parameters can be either supplies individually as arguments or as
        ParameterCollections or dictionaries.

        Parameters
        ----------
        *args : Union[Parameter, dict, ParameterCollection]
            Any Parameter or ParameterCollection
        **kwargs : dict
            A dictionary with Parameter values.
        """
        # perform all type checks before adding any items:
        self.__check_arg_types(*args)
        self.__check_kwarg_types(**kwargs)
        self.__check_duplicate_keys(*args, **kwargs)
        self.__add_arg_params(*args)
        self.__add_kwarg_params(**kwargs)

    def delete_param(self, key):
        """
        Remove a Parameter from the ParameterCollection.

        This method is a wrapper for the intrinsic dict.__delitem__ method.

        Parameters
        ----------
        key : str
            The key of the dictionry entry to be removed.
        """
        self.__delitem__(key)

    def get_copy(self):
        """
        Get a copy of the ParameterCollection.

        This method will return a copy of the ParameterCollection with
        a copy of each Parameter object.

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


    def get_value(self, param_key):
        """
        Get the value of a stored parameter.

        This method will verify that the entry exists and returns its value
        in its native type.

        Parameters
        ----------
        param_key : str
            The reference key to the parameter in the dictionary.

        Raises
        ------
        KeyError
            If the key "param_key" is not registered.

        Returns
        -------
        object
            The value of the Parameter object in its native data type.
        """
        self.__check_key_exists(param_key)
        return self.__getitem__(param_key).value

    def __check_key_exists(self, param_key):
        """
        Check if the Parameter key exists.

        Parameters
        ----------
        param_key : str
            The Parameter key.

        Raises
        ------
        KeyError
            If the "param_key" does not exist.
        """
        if param_key not in self.keys():
            raise KeyError(f'No parameter with the name "{param_key}" '
                            'has been registered.')

    def set_value(self, param_key, value):
        """
        Update the value of a stored parameter.

        This method will verify that the entry exists and update the the
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
        self.__check_key_exists(param_key)
        _item = self.__getitem__(param_key)
        _item.value = value

    def get_param(self, param_key):
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
        self.__check_key_exists(param_key)
        return self.__getitem__(param_key)
