# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the DiffractionExperimentIoHdf5 class which is used to import
DiffractionExperimentContext metadata from HDF5 files (written by pydidas).
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DiffractionExperimentIoHdf5"]

from pathlib import Path
from typing import Union

import h5py
import numpy as np

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_context import DiffractionExperimentContext
from pydidas.contexts.diff_exp.diff_exp_io_base import DiffractionExperimentIoBase
from pydidas.core import UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS, LAMBDA_IN_A_TO_E
from pydidas.core.utils import (
    CatchFileErrors,
)
from pydidas.core.utils.hdf5_dataset_utils import (
    export_context_to_hdf5,
    read_and_decode_hdf5_dataset,
)


EXP = DiffractionExperimentContext()


class DiffractionExperimentIoHdf5(DiffractionExperimentIoBase):
    """
    Importer / Exporter for DiffractionExperiment metadata from HDF5 files
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"

    @classmethod
    def export_to_file(cls, filename: Path | str, **kwargs: dict):
        """
        Write the ExperimentalTree to a HDF5 file.

        Parameters
        ----------
        filename : Path | str
            The filename of the file to be written.
        diffraction_exp : DiffractionExperiment, optional
            The DiffractionExperiment instance to be exported. The default is the
            DiffractionExperimentContext.
        """
        _EXP = kwargs.get("diffraction_exp", EXP)
        cls.check_for_existing_file(filename, **kwargs)
        export_context_to_hdf5(filename, _EXP, "entry/pydidas_config/diffraction_exp")

    @classmethod
    def import_from_file(
        cls,
        filename: Path | str,
        diffraction_exp: Union[DiffractionExperiment, None] = None,
    ):
        """
        Restore the DiffractionExperimentContext from a HDF5 file.

        Parameters
        ----------
        filename : Path | str
            The filename of the file to be written.
        diffraction_exp : Union[DiffractionExperiment, None], optional
            The DiffractionExperiment instance to be updated.
        """
        if diffraction_exp is None:
            diffraction_exp = EXP
        with (
            CatchFileErrors(filename, KeyError, raise_file_read_error=False) as catcher,
            h5py.File(filename, "r") as file,
        ):
            cls.imported_params = {}
            for _key in diffraction_exp.params.keys():
                cls.imported_params[_key] = read_and_decode_hdf5_dataset(
                    file[f"entry/pydidas_config/diffraction_exp/{_key}"]
                )
        if catcher.raised_exception:
            raise UserConfigError(
                f"Cannot interpret the selected file {filename} as a saved instance of "
                "DiffractionExperimentContext. Please check the file format and "
                "content."
            )
        cls.imported_params["xray_energy"] = LAMBDA_IN_A_TO_E / cls.imported_params.get(
            "xray_wavelength", np.nan
        )
        cls._verify_all_entries_present()
        cls._write_to_exp_settings(diffraction_exp=diffraction_exp)
