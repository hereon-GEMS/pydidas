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
Module with the ExperimentalSetupYamlIo class which is used to import
ExperimentalSetup metadata from a YAML file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSetupIoYaml']

import yaml
import numpy as np
from numbers import Real, Integral

from ...core.constants import YAML_EXTENSIONS, LAMBDA_IN_A_TO_E
from .experimental_setup_io_base import ExperimentalSetupIoBase
from .experimental_setup import ExperimentalSetup


EXP_SETUP = ExperimentalSetup()


class ExperimentalSetupIoYaml(ExperimentalSetupIoBase):
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
        tmp_params = EXP_SETUP.get_param_values_as_dict()
        # need to convert all float values to generic python "float" to
        # allow using the yaml.save_dump function
        for _key, _val in tmp_params.items():
            if isinstance(_val, Real) and not isinstance(_val, Integral):
                tmp_params[_key] = float(_val)
        del tmp_params['xray_energy']
        with open(filename, 'w') as stream:
            yaml.safe_dump(tmp_params, stream)

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the ExperimentalSetup from a YAML file.

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
        assert isinstance(cls.imported_params, dict)
        cls.imported_params['xray_energy'] = (
            LAMBDA_IN_A_TO_E
            / cls.imported_params.get('xray_wavelength', np.nan))
        cls._verify_all_entries_present()
        cls._write_to_exp_settings()
