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
Module with the PydidasQsettings class which can be used to query and
modify the globally stored QSettings for pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasQsettings"]


from typing import Optional, Union

from pydidas.core.pydidas_q_settings_mixin import PydidasQsettingsMixin


class PydidasQsettings(PydidasQsettingsMixin):
    """
    A modified version of the QSettings with some additional convenience methods.

    Parameters
    ----------
    version : Optional[str]
        An optional version string. If None, the pydidas version will be used.
        The default is None.
    """

    def __init__(self, version: Optional[str] = None):
        PydidasQsettingsMixin.__init__(self, version=version)

    def show_all_stored_q_settings(self):
        """
        Print all stored QSettings to the standard output.
        """
        _sets = self.get_all_stored_q_settings()
        for _key, _val in _sets.items():
            print(f"{_key}: {_val}")

    def get_all_stored_q_settings(self) -> dict:
        """
        Get all stored QSettings values as a dictionary.

        Returns
        -------
        dict
            The dict with (key: stored_value) pairs.
        """
        _keys = self.q_settings.allKeys()
        _prefix = f"{self.q_settings_version}/"
        return {
            _key.removeprefix(_prefix): self.q_settings.value(_key)
            for _key in _keys
            if (
                (_key.startswith(_prefix) or _key.startswith("font/"))
                and not (_key.startswith(f"{_prefix}dialogues"))
            )
        }

    def set_value(self, key: str, val: object):
        """
        Set the value of a QSettings key.

        Parameters
        ----------
        key : str
            The name of the key.
        val : object
            The new value stored for the key.
        """
        self.q_settings.setValue(f"{self.q_settings_version}/{key}", val)

    def value(self, key: str, dtype: Union[None, type] = None) -> object:
        """
        Get the value from a QSetting key.

        This method is a wrapper for the PydidasQsettingsMixin.q_settings_get_value
        method.

        Parameters
        ----------
        key : str
            The QSetting reference key.
        dtype : Union[type, None], optional
            A return datatype. If not None, the output will be returned as
            dtype(value).

        Returns
        -------
        value : object
            The value, converted to the type associated with the Parameter
            referenced by param_key or dtype, if given.
        """
        return self.q_settings_get(key, dtype)
