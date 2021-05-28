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
The parameter module includes the Parameter class which is used to store
processing parameters.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Parameter']

import numbers
from PyQt5 import QtCore

# class ParameterCollection(OrderedDict):
#     """Collection of parameters for plugins.
#     """
#     def __init__(self, params=None):
#         """Setup method."""
#         super().__init__()
#         for _p in params:
#             self._eter(_p)

#     def add_parameter(self, param):
#         """Method to add a parameter.

#         Parameters
#         ----------
#         param : Parameter object
#             An instance of a Parameter object.

#         Raises
#         ------
#         KeyError
#             If an entry with param.name already exists.

#         Returns
#         -------
#         None.
#         """
#         if param.name in self.keys():
#             raise KeyError(f'A parameter with the name "{param.name}" '
#                            'already exists.')
#         self.__setitem__(param.name, param)

#     def remove_parameter_by_name(self, param_name):
#         """
#         Removoe a parameter from the collection.

#         Parameters
#         ----------
#         param_name : str
#             The key name of the parameter.

#         Raises
#         ------
#         KeyError
#             If no parameter with param_name has been registered.

#         Returns
#         -------
#         None.
#         """
#         if param_name not in self.keys():
#             raise KeyError(f'No parameter with the name "{param_name}" '
#                            'has been registered.')
#         self.__delitem__(param_name)



def _get_base_cls(cls):
    """
    Filter numerical classes and return the corresponding
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
    """A class used for storing parameters and associated metadata.

    The parameter has the following properties which can be accessed.
    Only the value property can be edited at runtime, all other properties
    are fixed at instanciation.

    +------------+-----------+-------------------------------------------+
    | property   | editable  | description                               |
    +============+===========+===========================================+
    | name       | False     | A readable name as description.           |
    +------------+-----------+-------------------------------------------+
    | value      | True      | The current value.                        |
    +------------+-----------+-------------------------------------------+
    | choices    | True      | A list with choices if the value of the   |
    |            |           | parameter is limited to specific values.  |
    +------------+-----------+-------------------------------------------+
    | optional   | False     | A flag whether the parameter is required  |
    |            |           |  or optional.                             |
    +------------+-----------+-------------------------------------------+
    | tooltip    | False     | A readable tooltip.                       |
    +------------+-----------+-------------------------------------------+
    | default    | False     | The default value                         |
    +------------+-----------+-------------------------------------------+
    | refkey     | False     | A reference key for the parameter.        |
    |            |           | This key is only used internally.         |
    +------------+-----------+-------------------------------------------+
    """

    def __init__(self, name, param_type, **kwargs):
        """
        Setup method.

        Parameters can be passed either as a complete meta_dict or as
        indicidual keyword arguments. The meta_dict will take precend

        Parameters
        ----------
        name : str, optional
            The name of the parameter. The default is None.
        param_type : type, optional
            The datatype of the parameter. If None, no type-checking will be
            performed. If any integer or float value is used, this will be
            changed to the abstract base class of numbers.Integral or
            numbers.Real. The default is None.
        default : type, optional
            The default value. The data type must be of the same type as
            param_type. The default is None.
        optional : bool
            Keyword to toggle optional parameters. The default is False.
        tooltip : str
            A description of the parameter. It will be automatically extended
            to include certain type and unit information.
        unit : str
            The unit of the parameter.
        choices : Union[list, tuple, None]
            A list of allowed choices. If None, no checking will be enforced.
            The default is None.
        value : object
            The value of the parameter. This parameter should only be used
            to restore saved parameters.
        **kwargs : dict
            All optional parameters can also be passed as a keyword argument
            dictionary.

        Returns
        -------
        None.
        """
        super().__init__()
        self.__name = name
        self.__type = _get_base_cls(param_type)
        self.__meta = dict(default = kwargs.get('default', None),
                           tooltip = kwargs.get('tooltip', ''),
                           unit = kwargs.get('unit', ''),
                           optional = kwargs.get('optional', False),
                           refkey = kwargs.get('refkey', name))

        _choices = kwargs.get('choices', None)
        self.__meta['choices'] = (_choices if (isinstance(_choices, list)
                                               or _choices is None)
                                  else list(_choices))
        _def = self.__meta['default']
        if not self.__typecheck(_def):
            raise TypeError(f'Default value "{_def}" does not have data'
                            f'type {self.__type}!')
        if (self.__meta['choices'] is not None
                and _def not in self.__meta['choices']):
            raise ValueError(f'The default value "{_def}" does not '
                             'correspond to any of the defined choices: '
                             f'{self.__meta["choices"]}.')
        self.__value = _def if not 'value' in kwargs else kwargs['value']

    def __call__(self):
        """
        Calling method to get the value.

        Returns
        -------
        value
            The stored parameter value-

        """
        return self.__value

    def __typecheck(self, val):
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
        if not self.__type:
            return True
        if isinstance(val, self.__type):
            return True
        return False

    @property
    def name(self):
        """
        Return the parameter name.

        Returns
        -------
        str
            The parameter name.
        """
        return self.__name

    @property
    def refkey(self):
        """
        Return the paramter reference key.

        Returns
        -------
        str
            The parameter reference key.
        """
        return self.__meta['refkey']

    @property
    def default(self):
        """
        Return the default value.

        Returns
        -------
        default
            The default value.
        """
        return self.__meta['default']

    @property
    def unit(self):
        """
        Get the Parameter unit.

        Returns
        -------
        str
            The unit of the Parameter.
        """
        return self.__meta['unit']

    @property
    def tooltip(self):
        """
        Get the Parameter tooltip.

        Returns
        -------
        str
            The tooltip for the Parameter.
        """
        _t = self.__meta['tooltip']
        if self.unit:
            _t += f' (unit: {self.unit})'
        if self.type == numbers.Integral:
            _t += ' (type: integer)'
        elif self.type == numbers.Real:
            _t += ' (type: float)'
        elif self.type == str:
            _t += ' (type: str)'
        else:
            _t += f' (type: {str(self.type)}'
        return _t.replace(') (', ', ')

    @property
    def choices(self):
        """
        Get the allowed choices for the Parameter value.

        Returns
        -------
        list or None
            The allowed choices for the Parameter.
        """
        return self.__meta['choices']

    @choices.setter
    def choices(self, choices):
        """
        Update the allowed choices of a Parameter.

        Parameters
        ----------
        choices : Union[list, tuple]
            A list or tuple of allowed choices. A check will be performed that
            all entries correspond to the defined data type and that the
            curent parameter value is one of the allowed choices.

        Raises
        ------
        TypeError
            If the supplied choices are not of datatype list or tuple.
        ValueErrror
            If any choice in choices does not pass the datatype check.
        ValueError
            If the current Parameter value is not included in the list of
            new choices.

        Returns
        -------
        None.
        """
        if not isinstance(choices, (list, tuple)):
            raise TypeError('New choices must be a list or tuple.')
        for _c in choices:
            if not self.__typecheck(_c):
                raise ValueError(f'The new choice "{_c}" does not have the '
                                 'correct data type.')
        if self.__value not in choices:
            raise ValueError('The new choices do not include the current '
                             f'Parameter value ({self.__value})')
        self.__meta['choices'] = list(choices)


    @property
    def optional(self):
        """
        Get the flag whether the parameter is optional or not.

        Returns
        -------
        bool
            The unit of the Parameter.
        """
        return self.__meta['optional']

    @property
    def type(self):
        """
        Get the type of the Parameter value.

        Returns
        -------
        object
            The class of the parameter value type.
        """
        return self.__type

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
        if self.__meta['choices'] and val not in self.__meta['choices']:
            raise ValueError(f'The selected value "{val}" does not correspond'
                             ' to any of the allowed choices: '
                             f'{self.__meta["choices"]}')
        if not (self.__typecheck(val)
                or self.__mexta['optional'] and (val is None)):
            raise ValueError(f'Cannot set parameter "{str(self.__name)}" '
                             'because it is of the wrong data type.')
        self.__value = val

    def restore_default(self):
        """
        Restore the parameter to its default value.

        Returns
        -------
        None.
        """
        self.value = self.__meta['default']

    def is_optional(self):
        """
        Check whether the parameter is optional.

        Returns
        -------
        bool
            The boolean flag whether the paramter is optional.
        """
        return self.__meta['optional']


    def get_type(self):
        """
        A method to get the parameter data type.

        Returns
        -------
        object
            The class of the data type.
        """
        return self.__type

    def dump(self):
        """
        A method to get the full class information for saving.

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
        _meta = self.__meta
        _meta.update({'value': self.__value})
        return (self.__name, self.__type, _meta)

    def __str__(self):
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

        _type =( f'{self.__type.__name__}' if self.__type is not None else
                'None')
        _def = (f'{self.__meta["default"]}'
                if self.__meta['default'] not in (None, '') else 'None')
        _unit = f' {self.unit}' if self.unit else ''
        return (f'{self.name}: {self.value}{_unit} (type: {_type}, '
                f'default: {_def} {self.__meta["unit"]})')

    def __repr__(self):
        _type =( f'{self.__type.__name__}' if self.__type is not None else
                'None')
        _unit= (f'{self.__meta["unit"]} ' if self.__meta['unit'] !=''
                else self.__meta['unit'])
        _val = f'{self.value}' if self.value not in (None, '') else '""'
        _def = (f'{self.__meta["default"]}'
                if self.__meta['default'] not in (None, '') else 'None')
        _s = f'Parameter {self.__name} (type: {_type}'
        if self.__meta['optional']:
            _s += ', optional'
        _s += f'): {_val} {_unit}(default: {_def})'
        return _s
