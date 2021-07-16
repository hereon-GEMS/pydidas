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

"""Module with the BaseApp from which all apps should inherit.."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PydidasQsettingsMixin']


from numbers import Integral, Real
from PyQt5 import QtCore

from .generic_parameters import get_generic_parameter
from ..config import QSETTINGS_GLOBAL_KEYS


settings = QtCore.QSettings('Hereon', 'pydidas')
for key in QSETTINGS_GLOBAL_KEYS:
    _val = settings.value(f'global/{key}')
    if _val is None:
        _param = get_generic_parameter(key)
        settings.setValue(f'global/{key}', _param.default)
del settings


class copyableQSettings(QtCore.QSettings):
    """
    QtCore.QSettings subclass with an added copy method.
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __copy__(self):
        return copyableQSettings(self.organizationName(),
                                 self.applicationName())


class PydidasQsettingsMixin:
    """

    An object with a ParameterCollection.

    This class can be inherited by any class which requires a
    ParameterCollection and access methods for it.
    """
    def __init__(self, *args, **kwargs):
        """
        Create a Base instance.

        Parameters
        ----------
        *args : list
            Any arguments. Defined by the concrete
            subclass..
        **kwargs : dict
            A dictionary of keyword arguments. Defined by the concrete
            subclass.
        """
        self.q_settings = copyableQSettings('Hereon', 'pydidas')

    def qsetting_get_global_value(self, param_key):
        """
        Get the value from a QSetting.

        Parameters
        ----------
        param_key : str
            The QSetting reference key. A "global/" prefix will be applied
            to it..

        Returns
        -------
        value : object
            The value, converted to the type associated with the Parameter
            referenced by param_key.
        """
        _value = self.q_settings.value(f'global/{param_key}')
        return self._qsettings_convert_value_type(param_key, _value)

    def _qsettings_convert_value_type(self, param_key, value):
        """
        Convert a value to the datatype expected by the Parameter.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.
        value : object
            The value whose type should be converted.

        Returns
        -------
        value : object
            The value in the correct datatype.
        """
        print(param_key, value)
        try:
            _p = self.get_param(param_key)
            if _p.type == Integral:
                return int(value)
            elif _p.type == Real:
                return float(value)
        except KeyError:
            pass
        return value
