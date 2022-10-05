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
Module with the SetupScanIoBase class which exporters/importers for the
SetupScan should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SetupScanIoBase"]

from ...core.io_registry import GenericIoBase
from ...core.constants import SCAN_GENERIC_PARAM_NAMES
from ...core import UserConfigError
from .setup_scan_io_meta import SetupScanIoMeta
from .setup_scan import SetupScan


SCAN = SetupScan()


class SetupScanIoBase(GenericIoBase, metaclass=SetupScanIoMeta):
    """
    Base class for SetupScan importer/exporters.
    """

    extensions = []
    format_name = "unknown"
    imported_params = {}

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
                "The following SetupScan Parameters are missing:\n - "
                + "\n - ".join(_missing_entries)
            )
            raise UserConfigError(_text)

    @classmethod
    def _write_to_scan_settings(cls):
        """
        Write the loaded (temporary) Parameters to the scanSettings.
        """
        for _key, _item in cls.imported_params.items():
            SCAN.set_param_value(_key, _item)
        cls.imported_params = {}
