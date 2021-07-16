# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
The parameter module includes the Parameter class which is used to store
processing parameters.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Parameter']

import numbers
from pathlib import Path

from pydidas.core.hdf_key import HdfKey


def _get_base_class(cls):
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
    Only the value and choices properties can be edited at runtime, all other
    properties are fixed at instanciation.

    +------------+-----------+-------------------------------------------+
    | property   | editable  | description                               |
    +============+===========+===========================================+
    | name       | False     | A readable name as description.           |
    +------------+-----------+-------------------------------------------+
    | value      | True      | The current value.                        |
    +------------+-----------+-------------------------------------------+
    | refkey     | False     | A reference key for the Parameter.        |
    |            |           | This key is used for accessing the        |
    |            |           | Parameter in the ParameterCollection      |
    +------------+-----------+-------------------------------------------+
    | choices    | True      | A list with choices if the value of the   |
    |            |           | parameter is limited to specific values.  |
    +------------+-----------+-------------------------------------------+
    | optional   | False     | A flag whether the parameter is required  |
    |            |           | or optional.                              |
    +------------+-----------+-------------------------------------------+
    | tooltip    | False     | A readable tooltip.                       |
    +------------+-----------+-------------------------------------------+
    | default    | False     | The default value                         |
    +------------+-----------+-------------------------------------------+

    """

    def __init__(self, name, param_type, meta=None, **kwargs):
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
        meta : Union[dict, None], optional
            A dictionary with meta data. Any keys specified as meta will
            overwrite the kwargs dictionary. This is added merely as
            convenience to facility copying Parameter instances. If None,
            this entry will be ignored. The default is None.
        refkey : str, optional
            The reference key for the Parameter in the Parameter collection.
            If not specified, this will default to the name.
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
        """
        super().__init__()
        self.__name = name
        self.__type = _get_base_class(param_type)
        if isinstance(meta, dict):
            kwargs.update(meta)

        self.__meta = dict(tooltip = kwargs.get('tooltip', ''),
                           unit = kwargs.get('unit', ''),
                           optional = kwargs.get('optional', False),
                           refkey = kwargs.get('refkey', name))
        self.__process_default_input(kwargs)
        self.__process_choices_input(kwargs)
        self.__value = (self.__meta['default'] if 'value' not in kwargs
                        else kwargs['value'])

    def __process_default_input(self, kwargs):
        """
        Process the default value.

        Parameters
        ----------
        kwargs : dict
            The kwargs passed to init.

        Raises
        ------
        TypeError
            If the default value is not of the demanded data type.
        """
        default = kwargs.get('default', None)
        if not self.__typecheck(default):
            raise TypeError(f'Default value "{default}" does not have data'
                            f'type {self.__type}!')
        self.__meta['default'] = default

    def __process_choices_input(self, kwargs):
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
        _choices = kwargs.get('choices', None)
        if not (isinstance(_choices, (list, tuple, set)) or _choices is None):
            raise TypeError('The type of choices (type: "{type(_choices)}"'
                            'is not supported. Please use list or tuple.')
        self.__meta['choices'] = None if _choices is None else list(_choices)
        _def = self.__meta['default']
        if (self.__meta['choices'] is not None
                and _def not in self.__meta['choices']):
            raise ValueError(f'The default value "{_def}" does not '
                             'correspond to any of the defined choices: '
                             f'{self.__meta["choices"]}.')

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
        val : any
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

    def __convenience_type_conversion(self, value):
        """
        Convert the value to the defined type.

        This method will take the input value and do some type checking and
        conversion.

        The following conversions are supported:

            - str input and Path type
            - str input and HdfKey type

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
            elif self.__type == HdfKey:
                value = HdfKey(value)
        return value

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
            _t += f' (type: {str(self.type)})'
        return _t.replace(') (', ', ')

    @property
    def choices(self):
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
        return self.__meta['choices']

    @choices.setter
    def choices(self, choices):
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
        if not isinstance(choices, (list, tuple, set)):
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
        Get or set the parameter value.

        Parameters
        ----------
        val : type
            The new value for the parameter.

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

        Raises
        ------
        ValueError
            Raised if the type of val does not correspond to the required
            datatype.
        """
        val = self.__convenience_type_conversion(val)
        if self.__meta['choices'] and val not in self.__meta['choices']:
            raise ValueError(f'The selected value "{val}" does not correspond'
                             ' to any of the allowed choices: '
                             f'{self.__meta["choices"]}')
        if not (self.__typecheck(val)
                or self.__meta['optional'] and (val is None)):
            raise ValueError(
                f'Cannot set Parameter (object ID:{id(self)}, name: '
                f'"{self.__name}", reference: "{self.__meta["refkey"]}")'
                ' because it is of the wrong data type.')
        self.__value = val

    def restore_default(self):
        """
        Restore the parameter to its default value.
        """
        self.value = self.__meta['default']

    def get_copy(self):
        """
        A method to get the a copy of the Parameter object.

        Returns
        -------
        Parameter
            A full copy of the object.
        """
        return Parameter(*self.dump())

    def dump(self):
        """
        A method to get the full class information for saving.

        Returns
        -------
        str
            The name of the Parameter
        type
            The data type of the Parameter.
        meta
            A dictionary with all the metadata information about the
            Parameter (value, unit, tooltip, refkey, default, choices)
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
        _s = f'Parameter <{self.__name} (type: {_type}'
        if self.__meta['optional']:
            _s += ', optional'
        _s += f'): {_val} {_unit}(default: {_def})>'
        return _s

    def __copy__(self):
        return self.get_copy()
