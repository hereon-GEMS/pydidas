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
Module with the WorkflowTreeIoBase class which exporters/importerss should
inherit from.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSettingsIoBase']

import os

from .experimental_settings_io_meta import ExperimentalSettingsIoMeta
from .experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()


class ExperimentalSettingsIoBase(metaclass=ExperimentalSettingsIoMeta):
    """
    Base class for ExperimentalSettins importer/exporters.
    """
    extensions = []
    format_name = 'unknown'
    imported_params = {}

    @classmethod
    def export_to_file(cls, filename):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        raise NotImplementedError

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        raise NotImplementedError

    @classmethod
    def check_for_existing_file(cls, filename, **kwargs):
        """
        Check if the file exists and if yes if the overwrite flag has been
        set.

        Parameters
        ----------
        filename : str
            The full filename and path.
        **kwargs : dict
            Any keyword arguments

        Raises
        ------
        FileExistsError
            If a file with filename exists and the overwrite flag is not True.
        """
        _overwrite = kwargs.get('overwrite', False)
        if os.path.exists(filename) and not _overwrite:
            raise FileExistsError(f'The file "{filename}" exists and '
                                  'overwriting has not been confirmed.')

    @classmethod
    def _verify_all_entries_present(cls):
        """
        Verify that the tmp_params dictionary holds all keys from the
        ExperimentalSettings.
        """
        for key in EXP_SETTINGS.params:
            if key not in cls.imported_params:
                raise KeyError(f'The setting for "{key}" is missing.')

    @classmethod
    def _write_to_exp_settings(cls):
        """
        Write the loaded (temporary) Parameters to the ExperimentalSettings.
        """
        for key in cls.imported_params:
            EXP_SETTINGS.set_param_value(key, cls.imported_params[key])
        cls.imported_params = {}
