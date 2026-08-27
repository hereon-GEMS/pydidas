# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DiffractionExperimentIoYaml"]


from numbers import Integral, Real
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_context import DiffractionExperimentContext
from pydidas.contexts.diff_exp.diff_exp_io_base import DiffractionExperimentIoBase
from pydidas.core import UserConfigError
from pydidas.core.constants import LAMBDA_IN_A_TO_E, YAML_EXTENSIONS
from pydidas.core.utils import verify_is_new_file_or_replace_set


EXP = DiffractionExperimentContext()


class DiffractionExperimentIoYaml(DiffractionExperimentIoBase):
    """
    YAML importer/exporter for ExperimentalSetting files.
    """

    extensions = YAML_EXTENSIONS
    format_name = "YAML"

    @staticmethod
    def export_to_file(filename: Path | str, **kwargs: Any) -> None:
        """
        Write the DiffractionExperiment to a file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        **kwargs : Any
            The following keyword arguments are defined:

            diffraction_exp : DiffractionExperiment, optional
                The DiffractionExperiment instance to be exported.
                The default is the DiffractionExperimentContext.
        """
        _exp = kwargs.get("diffraction_exp", EXP)
        verify_is_new_file_or_replace_set(filename, **kwargs)
        _tmp_params = _exp.get_param_values_as_dict()
        # need to convert all float values to generic python "float" to
        # allow using the yaml.save_dump function
        for _key, _val in _tmp_params.items():
            if isinstance(_val, Real) and not isinstance(_val, Integral):
                _tmp_params[_key] = float(_val)
        _tmp_params["detector_mask_file"] = str(_tmp_params["detector_mask_file"])
        del _tmp_params["xray_energy"]
        with open(filename, "w") as stream:
            yaml.safe_dump(_tmp_params, stream)

    @classmethod
    def import_from_file(  # type: ignore[override]
        cls,
        filename: Path | str,
        diffraction_exp: DiffractionExperiment | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Restore a DiffractionExperiment from a YAML file.

        If a diffraction experiment is given as argument, this instance
        is updated. If none is given, the generic DiffractionExperimentContext
        is updated.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        diffraction_exp : DiffractionExperiment or None, optional
            The DiffractionExperiment instance to be updated.
        """
        with open(filename, "r") as stream:
            try:
                _imported_params = yaml.safe_load(stream)
            except (yaml.YAMLError, UnicodeDecodeError):
                _imported_params = None
        if not isinstance(_imported_params, dict):
            raise UserConfigError(
                f"Cannot interpret the selected file {filename} as a saved instance of "
                "DiffractionExperimentContext."
            )
        _imported_params["xray_energy"] = LAMBDA_IN_A_TO_E / _imported_params.get(
            "xray_wavelength", np.nan
        )
        cls.verify_all_entries_present(_imported_params)
        cls.update_diffraction_exp(_imported_params, diffraction_exp=diffraction_exp)
