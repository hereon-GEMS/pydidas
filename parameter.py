# MIT License
#
# Copyright (c) 2021 Malte Storm, Hereon
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

"""Base class for parameter handling."""

from copy import copy
import numbers



# class ParameterCollection(OrderedDict):
#     def __init__(self, params=None):
#         self._params = []
#         self._param_names = []
#         for p in params:
#             self.add_parameter(p)

#     def add_parameter(self, param):
#         if param.name in self._param_names:
#             raise KeyError(f'A parameter with the name "{param.name}" already exists.')
#         self._params.append(param)
#         self._param_names.append(param.name)

#     def remove_parameter_by_name(self, param_name):
#         if param_name not in self._param_names:
#             raise KeyError(f'No parameter with the name "{param_name}" has been registered.')
#         self._param_names.remove(param_name)

#         for param in self._params:
#             if param.name == param_name:
#                 self._params.remove(param)
#     @property
#     def parameters(self):
#         return self._params


def _get_base_cls(cls):
    """
    Filter numerical and sequence classes and return the corresponding
    abstract base class.

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
    """An object to hold all information needed for parameters."""

    def __init__(self, name=None, param_type=None, default=None,
                 optional=False, desc=None, unit=None):
        """
        Setup method.

        Parameters
        ----------
        name : str, optional
            The name of the parameter. The default is None.
        param_type : type, optional
            The datatype of the parameter. If None, no type-checking will be
            performed. If any integer or float value is used, this will be
            changed to the abstract base class of numbers.Integral or
            numbers.Real. The default is None.
        default : TYPE, optional
            The default value. The default is None.
        optional : bool, optional
            Keyword to toggle optional parameters. The default is False.
        desc : None or str
            A description of the parameter.
        Returns
        -------
        None.

        """
        self.name = name
        self._type = _get_base_cls(param_type)
        if not self.typecheck(default):
            raise TypeError(f'Default value "{default}" does not have data'
                            f'type {param_type}!')
        self.__value = default
        self.optional = optional
        self.description = desc
        self.default = default
        self.unit = unit if unit else ''

    def typecheck(self, val):
        """
        Check type of

        Parameters
        ----------
        val : type
            The value of the parameter to be checked.

        Returns
        -------
        bool
            Returns True if the type of val matches the defined data type
            or if type is None.

        """
        if not self._type:
            return True
        if isinstance(val, self._type):
            return True
        return False

    @property
    def value(self):
        """
        Get the parameter value.

        Returns
        -------
        value
            The value of the parameter.
        """
        return self.__value

    @value.setter
    def value(self, val):
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

        Returns
        -------
        None.

        """
        if self.typecheck(val):
            self.__value = val
        else:
            if self.optional and (val is None):
                return
            else:
                raise ValueError(f'Cannot set parameter "{str(self.name)}" '
                                 'because it is of the wrong data type.')


    def restore_default(self):
        """
        Restore the parameter to its default value.

        Returns
        -------
        None.
        """
        self.value = self.default

    def isOptional(self):
        """
        Check whether the parameter is optional.

        Returns
        -------
        bool
            The boolean flag whether the paramter is optional.
        """
        return self.optional

    def dump(self):
        """
        A function to get the full class information for saving.

        Returns
        -------
        A tuple containing the following data:
        str
            The name of the parameter
        type
            The type value of the parameter.
        value
            The value of the parameter.
        bool
            The parameter is optionalflag value.
        str
            The description of the parameter.
        """
        return (self.name, self._type, self.__value, self.optional,
                self.description, self.unit)

    def __repr__(self):
        _type =( f'{self._type.__name__}' if self._type is not None else
                'no type specified')
        s = f'Parameter {self.name} (type: {_type}'
        if self.optional:
            s += ', optional'
        s += f'): {self.__value} {self.unit} (default: {self.default})'
        return s