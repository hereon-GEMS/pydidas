# MIT License
#
# Copyright (c) 2021 Malte Storm, HZG
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


class ParameterCollection:
    def __init__(self):
        self._params = []
        self._param_names = []

    def add_parameter(self, param):
        if param.name in self._param_names:
            raise KeyError(f'A parameter with the name "{param.name}" already exists.')
        self._params.append(param)
        self._param_names.append(param.name)

    def remove_parameter_by_name(self, param_name):
        if param_name not in self._param_names:
            raise KeyError(f'No parameter with the name "{param_name}" has been registered.')
        self._param_names.remove(param_name)

        for param in self._params:
            if param.name == param_name:
                self._params.remove(param)

    @property
    def parameters(self):
        return self._params


class Parameter:
    """An object to hold all information needed for parameters."""

    def __init__(self, name=None, param_type=None, default=None,
                 optional=False, desc=None):
        """
        Setup method.

        Parameters
        ----------
        name : str, optional
            The name of the parameter. The default is None.
        param_type : type, optional
            The type of the parameter. If None, no type-checking will be
            performed. The default is None.
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
        self._type = param_type
        if not self.typecheck(default):
            raise TypeError(f'Default value "{default}" does not have data'
                            f'type {param_type}!')
        self.value = copy(default)
        self.optional = optional
        self.description = desc
        self.default = default

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
        if (type(val) is self._type) or not self._type:
            return True
        else:
            return False

    def set(self, val):
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
            self.value = val
        else:
            if self.optional and (val is None):
                return
            else:
                raise ValueError(f'Cannot set parameter "{str(self.name)}" '
                                 'because it is of the wrong data type.')

    def get(self):
        """
        Get the parameter value.

        Returns
        -------
        value
            The value of the parameter.
        """
        return self.value

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
        return (self.name, self._type, self.value, self.optional,
                self.description)

    def __repr__(self):
        _type =( f'{self._type.__name__}' if self._type is not None else
                'no type specified')
        s = f'Parameter {self.name} (type: {_type}'
        if self.optional:
            s += ', optional'
        s += f'): {self.value} (default: {self.default})'
        return s