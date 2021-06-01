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
is an OrderedDict implementation with additional methods to get and set
values of Parameters..
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ParameterCollection']

import collections

from .parameter import Parameter


class ParameterCollection(collections.OrderedDict):
    """
    Ordered collection of parameters.

    The ParameterCollection is an ordered dictionary for Parameter instances
    with additional convenience rountines to easily get and set Parameter
    values.
    Items can be added at instantiation either as a dictionary or as keyword
    arguments. Keywords will be converted to keys for the

    Parameters
    ----------
    """
    def __init__(self, *args, **kwargs):
        """Setup method."""
        super().__init__()
        for param in args:
            self.add_parameter(param)
        for _key in kwargs:
            if not isinstance(kwargs[_key], Parameter):
                raise TypeError(('ParameterCollection only supports '
                                 'Parameter objects as values.'))
            self.__setitem__(_key, kwargs[_key])

    def add_parameter(self, param):
        """Method to add a parameter.

        Parameters
        ----------
        param : Parameter object
            An instance of a Parameter object.

        Raises
        ------
        TypeError
            If the passed param argument is not a Parameter instance.
        KeyError
            If an entry with param.name already exists.

        Returns
        -------
        None.
        """
        if not isinstance(param, Parameter):
            raise TypeError(('ParameterCollection only supports '
                             'Parameter objects as values.'))
        if param.name in self.keys():
            raise KeyError(f'A parameter with the name "{param.name}" '
                            'already exists.')
        self.__setitem__(param.refkey, param)

    def remove_parameter_by_refkey(self, param_refkey):
        """
        Removoe a parameter from the collection.

        Parameters
        ----------
        param_refkey : str
            The reference key name of the parameter.

        Raises
        ------
        KeyError
            If no parameter with param_name has been registered.

        Returns
        -------
        None.
        """
        if param_refkey not in self.keys():
            raise KeyError(f'No parameter with the name "{param_name}" '
                            'has been registered.')
        self.__delitem__(param_refkey)

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
                             '"{param_name}" is not a Parameter object.'))
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

        Returns
        -------
        None
        """
        if param_name not in self.keys():
            raise KeyError(f'No parameter with the name "{param_name}" '
                            'has been registered.')
        _item = self.__getitem__(param_name)
        _item.value = value
