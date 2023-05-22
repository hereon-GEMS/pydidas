# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the DiffractionExperimentIoYaml class which is used to import or
export DiffractionExperimentContext metadata from a YAML file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DiffractionExperimentIoYaml"]

from numbers import Integral, Real

import numpy as np
import yaml

from ...core import UserConfigError
from ...core.constants import LAMBDA_IN_A_TO_E, YAML_EXTENSIONS
from .diffraction_experiment_context import DiffractionExperimentContext
from .diffraction_experiment_io_base import DiffractionExperimentIoBase


EXP = DiffractionExperimentContext()


class DiffractionExperimentIoYaml(DiffractionExperimentIoBase):
    """
    YAML importer/exporter for ExperimentalSetting files.
    """

    extensions = YAML_EXTENSIONS
    format_name = "YAML"

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Write the ExperimentalTree to a file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        diffraction_exp : DiffractionExperiment, optional
            The DiffractionExperiment instance to be exported. The default is the
            DiffractionExperimentContext.
        """
        _EXP = kwargs.get("diffraction_exp", EXP)
        cls.check_for_existing_file(filename, **kwargs)
        tmp_params = _EXP.get_param_values_as_dict()
        # need to convert all float values to generic python "float" to
        # allow using the yaml.save_dump function
        for _key, _val in tmp_params.items():
            if isinstance(_val, Real) and not isinstance(_val, Integral):
                tmp_params[_key] = float(_val)
        tmp_params["detector_mask_file"] = str(tmp_params["detector_mask_file"])
        del tmp_params["xray_energy"]
        with open(filename, "w") as stream:
            yaml.safe_dump(tmp_params, stream)

    @classmethod
    def import_from_file(cls, filename, diffraction_exp=None):
        """
        Restore the DiffractionExperimentContext from a YAML file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        diffraction_exp : Union[DiffractionExperiment, None], optional
            The DiffractionExperiment instance to be updated.
        """
        with open(filename, "r") as stream:
            try:
                cls.imported_params = yaml.safe_load(stream)
            except yaml.YAMLError as yerr:
                cls.imported_params = {}
                raise yaml.YAMLError from yerr
        if not isinstance(cls.imported_params, dict):
            raise UserConfigError(
                f"Cannot interpret the selected file {filename} as a saved instance of "
                "DiffractionExperimentContext."
            )
        cls.imported_params["xray_energy"] = LAMBDA_IN_A_TO_E / cls.imported_params.get(
            "xray_wavelength", np.nan
        )
        cls._verify_all_entries_present()
        cls._write_to_exp_settings(diffraction_exp=diffraction_exp)
