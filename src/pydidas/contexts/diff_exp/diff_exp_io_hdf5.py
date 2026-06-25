# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DiffractionExperimentIoHdf5"]


from pathlib import Path
from typing import Any

import h5py
import numpy as np

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_context import DiffractionExperimentContext
from pydidas.contexts.diff_exp.diff_exp_io_base import DiffractionExperimentIoBase
from pydidas.core import UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS, LAMBDA_IN_A_TO_E
from pydidas.core.utils import (
    CatchFileErrors,
    verify_is_new_file_or_replace_set,
)
from pydidas.core.utils.hdf5 import nxs_export_context, read_and_decode_hdf5_dataset


class DiffractionExperimentIoHdf5(DiffractionExperimentIoBase):
    """
    Importer / Exporter for DiffractionExperiment metadata from HDF5 files
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"

    @staticmethod
    def export_to_file(  # type: ignore[override]
        filename: Path | str, **kwargs: Any
    ) -> None:
        """
        Write the ExperimentalTree to a HDF5 file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        **kwargs : Any
            Keyword arguments. Supported kwargs are:

            diffraction_exp : DiffractionExperiment, optional
                The DiffractionExperiment instance to be exported. The
                default is the DiffractionExperimentContext.
        """
        _EXP = kwargs.get("diffraction_exp", DiffractionExperimentContext())
        verify_is_new_file_or_replace_set(filename, **kwargs)
        with h5py.File(filename, "a") as h5file:
            nxs_export_context(h5file, _EXP, "entry/pydidas_diffraction_exp")

    @classmethod
    def import_from_file(  # type: ignore[override]
        cls,
        filename: Path | str,
        diffraction_exp: DiffractionExperiment | None = None,
    ) -> None:
        """
        Restore the DiffractionExperimentContext from a HDF5 file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be read.
        diffraction_exp : DiffractionExperiment or None, optional
            The DiffractionExperiment instance to be updated. The default is
            None.
        """
        diffraction_exp = diffraction_exp or DiffractionExperimentContext()
        _imported_params = {}
        with (
            CatchFileErrors(filename, KeyError, raise_file_read_error=False) as catcher,
            h5py.File(filename, "r") as _h5file,
        ):
            _root_key = cls._find_root_key(_h5file)
            for _key in diffraction_exp.params.keys():
                _imported_params[_key] = read_and_decode_hdf5_dataset(
                    _h5file[f"{_root_key}{_key}"]
                )
        if catcher.raised_exception:
            raise UserConfigError(
                f"Cannot interpret the selected file {filename} as a "
                "saved instance of DiffractionExperimentContext. Please "
                "check the file format and content."
            )
        _imported_params["xray_energy"] = LAMBDA_IN_A_TO_E / _imported_params.get(
            "xray_wavelength", np.nan
        )
        cls.verify_all_entries_present(_imported_params)
        cls.update_diffraction_exp(_imported_params, diffraction_exp=diffraction_exp)

    @staticmethod
    def _find_root_key(h5file: h5py.File) -> str:
        """
        Find the root key for diffraction experiment exported settings.

        This method checks for legacy key locations and returns
        the appropriate root key for the diffraction experiment settings
        in the HDF5 file.

        Parameters
        ----------
        h5file : h5py.File
            The HDF5 file object to search for the root key.

        Returns
        -------
        str
            The root key for the diffraction experiment settings
            in the HDF5 file.
        """
        for _key in [
            "/entry/pydidas_diffraction_exp/",
            "/entry/pydidas_config/diffraction_exp/",
        ]:
            if _key in h5file:
                return _key
        raise KeyError("No valid key location found")
