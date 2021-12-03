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

"""
Module with the PydidasQsettings class which can be used to query and
modify the globally stored QSettings for pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PydidasQsettings']

from .pydidas_q_settings_mixin import PydidasQsettingsMixin


class PydidasQsettings(PydidasQsettingsMixin):
    """
    """
    def __init__(self):
        super().__init__()

    def show_all_stored_q_settings(self):
        """
        Print all stored QSettings to the standard output.
        """
        _sets = self.get_all_stored_q_settings()
        for _key, _val in _sets.items():
            print(f'{_key}: {_val}')

    def get_all_stored_q_settings(self):
        """
        Get all stored QSettings values as a dictionary.

        Returns
        -------
        dict
            The dict with (key: stored_value) pairs.
        """
        _keys = self.q_settings.allKeys()
        return {_key: self.q_settings.value(_key) for _key in _keys}

    def set_value(self, key, val):
        """
        Set the value of a QSettings key.

        Parameters
        ----------
        key : str
            The name of the key.
        val : object
            The new value stored for the key.
        """
        self.q_settings.setValue(key, val)
