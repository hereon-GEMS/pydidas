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

    Mix-in class with access functions to pydidas QSettings values.

    This class can be inherited by any class which requires access to the
    global QSettings defined in pydidas.
    """
    def __init__(self):
        """
        Create the q_settings attribute.
        """
        self.q_settings = copyableQSettings('Hereon', 'pydidas')

    def q_settings_get_global_value(self, key):
        """
        Get the value from a QSetting.

        Parameters
        ----------
        key : str
            The QSetting reference key. A "global/" prefix will be applied
            to the selected key.

        Returns
        -------
        value : object
            The value, converted to the type associated with the Parameter
            referenced by param_key.
        """
        _value = self.q_settings.value(f'global/{key}')
        return self._qsettings_convert_value_type(key, _value)

    def _qsettings_convert_value_type(self, key, value):
        """
        Convert a value to the datatype expected by the Parameter.

        Parameters
        ----------
        key : str
            The Parameter reference key.
        value : object
            The value whose type should be converted.

        Returns
        -------
        value : object
            The value in the correct datatype.
        """
        try:
            _p = self.get_param(key)
            if _p.type == Integral:
                return int(value)
            elif _p.type == Real:
                return float(value)
        except (KeyError, AttributeError):
            pass
        return value
