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
Module with the ExperimentalSettingsYamlIo class which is used to import
ExperimentalSettings metadata from a YAML file.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSettingsIoYaml']


import yaml

from pydidas.constants import YAML_EXTENSIONS, LAMBDA_TO_E
from .experimental_settings_io_base import ExperimentalSettingsIoBase
from .experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()


class ExperimentalSettingsIoYaml(ExperimentalSettingsIoBase):
    """
    YAML importer/exporter for ExperimentalSetting files.
    """
    extensions = YAML_EXTENSIONS
    format_name = 'YAML'

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Write the ExperimentalTree to a file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        cls.check_for_existing_file(filename, **kwargs)
        tmp_params = EXP_SETTINGS.get_param_values_as_dict()
        del tmp_params['xray_energy']
        with open(filename, 'w') as stream:
            yaml.safe_dump(tmp_params, stream)

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the ExperimentalSettings from a YAML file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        with open(filename, 'r') as stream:
            try:
                cls.imported_params = yaml.safe_load(stream)
            except yaml.YAMLError as yerr:
                cls.imported_params = {}
                raise yaml.YAMLError from yerr
        cls.imported_params['xray_energy'] = (
            LAMBDA_TO_E / cls.imported_params['xray_wavelength'])
        cls._verify_all_entries_present()
        cls._write_to_exp_settings()
