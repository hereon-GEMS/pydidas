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
Module with the ScanIoBase class which exporters/importers for the
ScanContext should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoBase"]

from pathlib import Path
from typing import Optional, Union

from pydidas.contexts.scan.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io import ScanIo
from pydidas.core import UserConfigError
from pydidas.core.generic_params import SCAN_GENERIC_PARAM_NAMES
from pydidas.core.io_registry import GenericIoBase


SCAN = ScanContext()


class ScanIoBase(GenericIoBase, metaclass=ScanIo):
    """
    Base class for ScanContext importer/exporters.
    """

    extensions = []
    format_name = "unknown"
    imported_params = {}
    beamline_format = False
    import_only = False

    @classmethod
    def _verify_all_entries_present(cls):
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
            _text = (
                "The following ScanContext Parameters are missing:\n - "
                + "\n - ".join(_missing_entries)
            )
            raise UserConfigError(_text)

    @classmethod
    def _write_to_scan_settings(cls, scan: Optional[Scan] = None):
        """
        Write the loaded (temporary) Parameters to the scanSettings.

        Parameters
        ----------
        scan : Optional[Scan], optional
            The Scan instance to be updated. If None, the ScanContext instance is used.
            The default is None.
        """
        _scan = SCAN if scan is None else scan
        for _key, _item in cls.imported_params.items():
            _scan.set_param_value(_key, _item)
        cls.imported_params = {}

    @classmethod
    def check_file_list(
        cls, filenames: list[Union[Path, str]], **kwargs: dict
    ) -> list[str]:
        """
        Check if the list of filenames is valid.

        Parameters
        ----------
        filenames : List[Path]
            List of filenames to be checked.
        **kwargs : dict
            Additional keyword arguments. Must be defined by the subclass.

        Returns
        -------
        List[str]
            A list of coded messages.
        """
        return ["::no_error::"]
