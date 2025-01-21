# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasQsettingsMixin"]


from numbers import Integral, Real
from typing import Optional, Self, Union

from qtpy import QtCore

from pydidas.version import VERSION
from pydidas_qtcore import PydidasQApplication


class _CopyablePydidasQSettings(QtCore.QSettings):
    """
    A pydidas-specific QSettings instance which allows pickling.

    CopyableQSettings is a QtCore.QSettings subclass with added copy, setstate and
    getstate methods to allow pickling. Note that the organization and application
    are hard-coded to "Hereon" and "pydidas", respectively.
    """

    def __init__(self):
        QtCore.QSettings.__init__(self, "Hereon", "pydidas")

    def __copy__(self) -> Self:
        return _CopyablePydidasQSettings()

    def __getstate__(self) -> dict:
        return {"org_name": "Hereon", "app_name": "pydidas"}

    def __setstate__(self, state: dict):
        return


class PydidasQsettingsMixin:
    """
    Mix-in class with access functions to pydidas QSettings values.

    This class can be inherited by any class which requires access to the
    global QSettings defined in pydidas.

    Parameters
    ----------
    version : Optional[str]
        An optional version string. The default is the pydidas version number.
    """

    def __init__(self, version: Optional[str] = None):
        self.q_settings = _CopyablePydidasQSettings()
        self.q_settings_version = version if version is not None else VERSION

    def q_settings_get(
        self,
        key: str,
        dtype: Union[type, None] = None,
        default: Union[object, None] = None,
    ) -> object:
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
        _value = self.q_settings.value(f"{self.q_settings_version}/{key}")
        if _value is None:
            return default
        if dtype is not None:
            if dtype == Integral:
                if _value in ["true", "True", True]:
                    return 1
                if _value in ["false", "False", False]:
                    return 0
                return int(_value)
            if dtype == Real:
                return float(_value)
            if dtype is bool:
                return _value in ["true", "True", True]
            return dtype(_value)
        return _value

    def q_settings_set(self, key: str, value: object):
        """
        Set the value of a QSettings key.

        Parameters
        ----------
        key : str
            The name of the key.
        value : object
            The value to be stored.
        """
        _current = self.q_settings_get(key)
        if value == _current:
            return
        self.q_settings.setValue(f"{self.q_settings_version}/{key}", value)
        if key.startswith("user/"):
            _stripped_key = key.replace("user/", "")
            _qtapp = PydidasQApplication.instance()
            _qtapp.updated_user_config(_stripped_key, str(value))
