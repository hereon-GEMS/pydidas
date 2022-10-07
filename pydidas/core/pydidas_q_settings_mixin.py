# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PydidasQsettingsMixin class which can be used to give classes
access to global QSettings values.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasQsettingsMixin", "CopyableQSettings"]

from numbers import Integral, Real

from qtpy import QtCore

from ..version import VERSION


class CopyableQSettings(QtCore.QSettings):
    """
    QtCore.QSettings subclass with added copy, setstate and getstate methods
    to allow pickling.
    """

    def __copy__(self):
        return CopyableQSettings(self.organizationName(), self.applicationName())

    def __getstate__(self):
        return {"org_name": self.organizationName(), "app_name": self.applicationName()}

    def __setstate__(self, state):
        super().__init__(state["org_name"], state["app_name"])


class PydidasQsettingsMixin:
    """
    Mix-in class with access functions to pydidas QSettings values.

    This class can be inherited by any class which requires access to the
    global QSettings defined in pydidas.
    """

    def __init__(self):
        self.q_settings = CopyableQSettings("Hereon", "pydidas")

    def q_settings_get_value(self, key, dtype=None, default=None):
        """
        Get the value from a QSetting key.

        Parameters
        ----------
        key : str
            The QSetting reference key.
        dtype : Union[type, None], optional
            A return datatype. If not None, the output will be returned as
            dtype(value), otherwise, the generic string/int will be returned. The
            default is None.
        default : type, optional
            The default value which is returned if the key defaults to None. The
            default is None.

        Returns
        -------
        value : object
            The value, converted to the type associated with the Parameter
            referenced by param_key or dtype, if given.
        """
        _value = self.q_settings.value(f"{VERSION}/{key}")
        if _value is None:
            return default
        if dtype is not None:
            if dtype == Integral:
                return int(_value)
            if dtype == Real:
                return float(_value)
            return dtype(_value)
        return _value

    def q_settings_set_key(self, key, value):
        """
        Set the value of a QSettings key.

        Parameters
        ----------
        key : str
            The name of the key.
        value : object
            The value to be stored.
        """
        self.q_settings.setValue(f"{VERSION}/{key}", value)
