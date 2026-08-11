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
Module with the ScanIoYaml class which is used to import and export
ScanContext metadata from a YAML file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoYaml"]


from pathlib import Path
from typing import Any

import yaml

from pydidas.contexts.scan.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core import UserConfigError
from pydidas.core.constants import YAML_EXTENSIONS
from pydidas.core.utils.file_checks import verify_is_new_file_or_replace_set


SCAN = ScanContext()


class ScanIoYaml(ScanIoBase):
    """
    YAML importer/exporter for Scan objects.
    """

    extensions = YAML_EXTENSIONS
    format_name = "YAML"

    @staticmethod
    def export_to_file(filename: Path | str, **kwargs: Any) -> None:
        """
        Write the ScanTree to a file.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        **kwargs : Any
            Optional keyword arguments. Supported keywords:

            scan : Scan, optional
                The Scan instance to export. If not provided, uses
                ScanContext.
        """
        _scan = kwargs.get("scan", SCAN)
        verify_is_new_file_or_replace_set(filename, **kwargs)
        _tmp_params = _scan.get_param_values_as_dict(filter_types_for_export=True)
        with open(filename, "w") as stream:
            yaml.safe_dump(_tmp_params, stream)

    @classmethod
    def import_from_file(
        cls,
        filename: str | Path,
        scan: Scan | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Restore the ScanContext from a YAML file.

        Parameters
        ----------
        filename : str or Path
            The filename of the file to be imported.
        scan : Scan or None, optional
            The Scan instance to be updated. If None, the ScanContext
            instance is used. The default is None.
        **kwargs : Any
            Optional keyword arguments. Not used in this implementation
            but supported for consistency.
        """
        _scan = SCAN if scan is None else scan
        with open(filename, "r") as stream:
            try:
                _imported_params = yaml.safe_load(stream)
            except (yaml.YAMLError, UnicodeError) as _yaml_error:
                _imported_params = {}
                raise yaml.YAMLError from _yaml_error
        if not isinstance(_imported_params, dict):
            raise UserConfigError(
                "The imported YAML file for the Scan does not contain a valid "
                "dictionary."
            )
        cls.update_scan_from_import(_imported_params, _scan)
