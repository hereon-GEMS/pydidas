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
Module with the ScanIoHdf5 class which is used to import and export
ScanContext metadata from a HDF5 file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoHdf5"]

from pathlib import Path
from typing import Any

import h5py

from pydidas.contexts.scan.scan import SCAN_LEGACY_PARAMS, Scan  # type: ignore[import]
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import CatchFileErrors, verify_is_new_file_or_replace_set
from pydidas.core.utils.hdf5 import (
    get_hdf5_populated_dataset_keys,
    nxs_create_recursive_groups,
    nxs_export_context,
    nxs_write_dataset,
    read_and_decode_hdf5_dataset,
)


SCAN = ScanContext()


class ScanIoHdf5(ScanIoBase):
    """
    HDF5 importer/exporter for Scan objects.
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"

    @staticmethod
    def export_to_file(filename: str | Path, **kwargs: Any) -> None:
        """
        Write the ScanTree to a file.

        Parameters
        ----------
        filename : str or Path
            The filename of the file to be written.
        **kwargs : Any
            Keyword arguments. Supported kwargs are:

            scan : Scan, optional
                The Scan instance to be exported. The default is the
                ScanContext instance.
        """
        _scan = kwargs.get("scan", SCAN)
        verify_is_new_file_or_replace_set(filename, **kwargs)
        with h5py.File(filename, "a") as h5file:
            nxs_export_context(h5file, _scan, "entry/pydidas_scan")
            nxs_create_recursive_groups(h5file, "entry/instrument", "NXinstrument")
            _det_group = nxs_create_recursive_groups(
                h5file, "entry/instrument/detector", "NXdetector"
            )
            nxs_write_dataset(
                _det_group,
                "frame_start_number",
                _scan.get_param_value("pattern_number_offset"),
            )

    @classmethod
    def import_from_file(cls, filename: Path | str, scan: Scan | None = None) -> None:
        """
        Restore the ScanContext from a HDF5 file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be read.
        scan : Scan or None, optional
            The Scan instance to be updated. If None, the ScanContext
            instance is used. The default is None.
        """

        _scan = SCAN if scan is None else scan
        with (
            CatchFileErrors(filename, KeyError, raise_file_read_error=False) as catcher,
            h5py.File(filename, "r") as _h5file,
        ):
            _root_key = cls._find_root_key(_h5file)
            _present_keys = [
                _key.removeprefix(_root_key)
                for _key in get_hdf5_populated_dataset_keys(
                    _h5file[_root_key], min_dim=0, min_size=0
                )
            ]
            _imported_params = {}
            for _key in list(_scan.params) + list(SCAN_LEGACY_PARAMS):
                if _key not in _present_keys:
                    continue
                _imported_params[_key] = read_and_decode_hdf5_dataset(
                    _h5file[f"{_root_key}{_key}"]
                )
        if catcher.raised_exception:
            raise UserConfigError(
                f"Cannot interpret the selected file {filename} as a "
                "saved instance of ScanContext. Please check the file "
                "format and content."
            )
        cls.update_scan_from_import(_imported_params, scan)  # type: ignore[type]

    @staticmethod
    def _find_root_key(h5file: h5py.File) -> str:
        """
        Find the root key for scan exported Scan settings.

        This method checks for legacy key locations and returns
        the appropriate root key for the scan settings in the HDF5 file.

        Parameters
        ----------
        h5file : h5py.File
            The HDF5 file object to search for the root key.

        Returns
        -------
        str
            The root key for the scan settings in the HDF5 file.
        """
        for _key in [
            "/entry/pydidas_scan/",
            "/entry/pydidas_config/scan/",
        ]:
            if _key in h5file:
                return _key
        raise KeyError("No valid key location found")
