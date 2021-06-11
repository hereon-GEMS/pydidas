# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
The parameter_collection module includes the ParameterCollection class which
is an dict implementation with additional methods to get and set
values of Parameters..
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterCollection']

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
                        '"{item.__class__}" to ParameterCollection.')

    def __add_arg_params(self, *params):
        """
        Add the passed parameters to the ParameterCollection.

        Parameters
        ----------
        *params : Union[Parameter, ParameterCollection]
            Single Parameters or ParameterCollections.
        """
        if isinstance(params, (ParameterCollection)):
            self.update(params)
        else:
            for _param in params:
                if isinstance(_param, Parameter):
                    self.add_param(_param)
                elif isinstance(_param, (ParameterCollection, dict)):
                    self.update(_param)

    def __add_kwarg_params(self, **kwparams):
        """
        Add the passed keyword parameters to the ParameterCollection.

        Parameters
        ----------
        **kwparams : dict
            A dictionary of keyword arguments.
        """
        for _key in kwparams:
            assert _key == kwparams[_key].refkey
            self.__setitem__(_key, kwparams[_key])

    def __check_arg_types(self, *args):
        """
        Check the types of input arguments.

        This method verifies that all passed arguments are either Parameters
        or ParameterCollections.

        This method
        Parameters
        ----------
        *params : any
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

        This method
        Parameters
        ----------
        *kwargs : any
            Any keyword arguments.
        """
        for _key in kwargs:
            if not isinstance(kwargs[_key], Parameter):
                self.__raise_type_error(kwargs[_key])

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
            If an entry with param.name already exists.
        """
        self.__check_arg_types(param)
        if param.name in self.keys():
            raise KeyError(f'A parameter with the name "{param.name}" '
                            'already exists.')
        self.__setitem__(param.refkey, param)

    def add_params(self, *params, **kwparams):
        """
        Add parameters to the ParameterCollection.

        This method adds Parameters to the ParameterCollection
        Parameters can be either supplies individually as arguments or as
        ParameterCollections or dictionaries.

        Parameters
        ----------
        *params : Union[Parameter, dict, ParameterCollection]
            Any Parameter or ParameterCollection
        **kwparams : dict
            A dictionary with Parameter values.
        """
        # perform all type checks before adding any items:
        self.__check_arg_types(*params)
        self.__check_kwarg_types(*kwparams)
        self.__add_arg_params(*params)
        self.__add_kwarg_params(**kwparams)

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


    def get_value(self, param_name):
        """
        Get the value of a stored parameter.

        This method will verify that the entry exists and returns its value
        in its native type.

        Parameters
        ----------
        param_name : str
            The reference key to the parameter in the dictionary.

        Raises
        ------
        KeyError
            If the key <param_name> is not registered.
        TypeError
            If the item referenced by <param_name> is not a Parameter
            instance.

        Returns
        -------
        object
            The value of the Parameter object in its native data type.
        """
        if param_name not in self.keys():
            raise KeyError(f'No parameter with the name "{param_name}" '
                            'has been registered.')
        _item = self.__getitem__(param_name)
        if not isinstance(_item, Parameter):
            raise TypeError(('The stored item referenced by the key '
                             f'"{param_name}" is not a Parameter object.'))
        return _item.value

    def set_value(self, param_name, value):
        """
        Update the value of a stored parameter.

        This method will verify that the entry exists and update the the
        stored value.

        Parameters
        ----------
        param_name : str
            The reference key to the parameter in the dictionary.
        value : object
             The new value for the Parameter. Note that type-checking is
             performed in the Parameter value setter.

        Raises
        ------
        KeyError
            If the key <param_name> is not registered.
        """
        if param_name not in self.keys():
            raise KeyError(f'No parameter with the name "{param_name}" '
                            'has been registered.')
        _item = self.__getitem__(param_name)
        _item.value = value
