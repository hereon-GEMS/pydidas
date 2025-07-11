# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ScanIoBase class which exporters/importers for Scan should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoBase"]


from pathlib import Path
from typing import Any

from pydidas.contexts.scan.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io import ScanIo
from pydidas.core import UserConfigError
from pydidas.core.generic_params import SCAN_GENERIC_PARAM_NAMES
from pydidas.core.io_registry import GenericIoBase


class ScanIoBase(GenericIoBase, metaclass=ScanIo):
    """
    Base class for Scan importer/exporters.
    """

    extensions = []
    format_name = "unknown"
    imported_params = {}
    beamline_format = False
    import_only = False

    @classmethod
    def _verify_all_entries_present(cls) -> None:
        """
        Verify that the tmp_params dictionary holds all keys from the
        scanSettings.
        """
        _missing_entries = []
        for _name in SCAN_GENERIC_PARAM_NAMES:
            if _name not in cls.imported_params:
                _missing_entries.append(_name)
        n_dim = cls.imported_params.get("scan_dim", 0)
        for _dim in range(n_dim):
            for _key in ["label", "n_points", "delta", "unit", "offset"]:
                _item = f"scan_dim{_dim}_{_key}"
                if _item not in cls.imported_params:
                    _missing_entries.append(_item)

        if len(_missing_entries) > 0:
            _text = "The following Scan Parameters are missing:\n - " + "\n - ".join(
                _missing_entries
            )
            raise UserConfigError(_text)

    @classmethod
    def _write_to_scan_settings(cls, scan: Scan | None = None) -> None:
        """
        Write the loaded (temporary) Parameters to the scanSettings.

        Parameters
        ----------
        scan : Scan, optional
            The Scan instance to be updated. If None, the ScanContext instance is used.
            The default is None.
        """
        _scan = ScanContext() if scan is None else scan
        for _key, _item in cls.imported_params.items():
            _scan.set_param_value(_key, _item)
        cls.imported_params = {}

    @classmethod
    def check_file_list(cls, filenames: list[Path | str], **kwargs: Any) -> list[str]:
        """
        Check if the list of filenames is valid.

        Parameters
        ----------
        filenames : list[Path | str]
            List of filenames to be checked.
        **kwargs : Any
            Additional keyword arguments. Must be defined by the subclass.

        Returns
        -------
        list[str]
            A list of coded messages.
        """
        return ["::no_error::"]

    @classmethod
    def update_scan_from_import(cls, scan: Scan) -> None:
        """
        Update the scan with the imported parameters.

        Parameters
        ----------
        scan : Scan
            The Scan instance to be updated.
        """
        cls._convert_legacy_param_names()
        cls._verify_all_entries_present()
        cls._write_to_scan_settings(scan=scan)

    @classmethod
    def _convert_legacy_param_names(cls) -> None:
        """
        Convert legacy parameter names to the new format.

        This method should be overridden by subclasses if they have
        specific legacy import formats to handle.
        """
        if "scan_start_index" in cls.imported_params:
            if "pattern_number_offset" in cls.imported_params:
                raise UserConfigError(
                    "The parameter `scan_start_index` is deprecated and has been "
                    "replaced by `pattern_number_offset`. However, both parameter keys "
                    "are present. Please verify the input file."
                )
            cls.imported_params["pattern_number_offset"] = cls.imported_params.pop(
                "scan_start_index"
            )
            cls.imported_params["pattern_number_delta"] = 1
        if "scan_index_stepping" in cls.imported_params:
            if "frame_indices_per_scan_point" in cls.imported_params:
                raise UserConfigError(
                    "The parameter `scan_index_stepping` is deprecated and has been "
                    "replaced by `frame_indices_per_scan_point`. However, both "
                    "parameter keys are present. Please verify the input file."
                )
            cls.imported_params["frame_indices_per_scan_point"] = (
                cls.imported_params.pop("scan_index_stepping")
            )
        if "scan_multiplicity" in cls.imported_params:
            if "scan_frames_per_scan_point" in cls.imported_params:
                raise UserConfigError(
                    "The parameter `scan_multiplicity` is deprecated and has been "
                    "replaced by `scan_frames_per_scan_point`. However, both "
                    "parameter keys are present. Please verify the input file."
                )
            cls.imported_params["scan_frames_per_scan_point"] = cls.imported_params.pop(
                "scan_multiplicity"
            )
        if "scan_multi_image_handling" in cls.imported_params:
            if "scan_multi_frame_handling" in cls.imported_params:
                raise UserConfigError(
                    "The parameter `scan_multi_image_handling` is deprecated and has "
                    "been replaced by `scan_multi_frame_handling`. However, both "
                    "parameter keys are present. Please verify the input file."
                )
            cls.imported_params["scan_multi_frame_handling"] = cls.imported_params.pop(
                "scan_multi_image_handling"
            )
