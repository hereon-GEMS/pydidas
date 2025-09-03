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
Module with the ScanIoHdf5 class which is used to import and export
ScanContext metadata from a HDF5 file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoHdf5"]


from typing import Union

import h5py

from pydidas.contexts.scan.scan import SCAN_LEGACY_PARAMS, Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import CatchFileErrors
from pydidas.core.utils.hdf5_dataset_utils import (
    export_context_to_hdf5,
    get_hdf5_populated_dataset_keys,
    read_and_decode_hdf5_dataset,
)


SCAN = ScanContext()


class ScanIoHdf5(ScanIoBase):
    """
    HDF5 importer/exporter for Scan objects.
    """

    extensions = HDF5_EXTENSIONS
    format_name = "HDF5"

    @classmethod
    def export_to_file(cls, filename: str, **kwargs: dict):
        """
        Write the ScanTree to a file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        _scan = kwargs.get("scan", SCAN)
        cls.check_for_existing_file(filename, **kwargs)
        export_context_to_hdf5(filename, _scan, "entry/pydidas_config/scan")

    @classmethod
    def import_from_file(cls, filename: str, scan: Union[Scan, None] = None):
        """
        Restore the ScanContext from a HDF5 file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        scan : Union[None, pydidas.contexts.scan.Scan], optional
            The Scan instance to be updated. If None, the ScanContext instance is used.
            The default is None.
        """

        _scan = SCAN if scan is None else scan
        with (
            CatchFileErrors(filename, KeyError, raise_file_read_error=False) as catcher,
            h5py.File(filename, "r") as file,
        ):
            _present_keys = [
                _key.removeprefix("/entry/pydidas_config/scan/")
                for _key in get_hdf5_populated_dataset_keys(
                    file["entry/pydidas_config/scan"], min_dim=0, min_size=0
                )
            ]
            cls.imported_params = {}
            for _key in list(_scan.params) + list(SCAN_LEGACY_PARAMS):
                if _key not in _present_keys:
                    continue
                cls.imported_params[_key] = read_and_decode_hdf5_dataset(
                    file[f"entry/pydidas_config/scan/{_key}"]
                )
        if catcher.raised_exception:
            raise UserConfigError(
                f"Cannot interpret the selected file {filename} as a saved instance of "
                "ScanContext. Please check the file format and "
                "content."
            )
        cls.update_scan_from_import(scan)
