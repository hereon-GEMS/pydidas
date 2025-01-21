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
Module with the ScanIoYaml class which is used to import and export
ScanContext metadata from a YAML file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIoYaml"]


from typing import Union

import yaml

from pydidas.contexts.scan.scan import Scan
from pydidas.contexts.scan.scan_context import ScanContext
from pydidas.contexts.scan.scan_io_base import ScanIoBase
from pydidas.core.constants import YAML_EXTENSIONS


SCAN = ScanContext()


class ScanIoYaml(ScanIoBase):
    """
    YAML importer/exporter for Scan objects.
    """

    extensions = YAML_EXTENSIONS
    format_name = "YAML"

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
        tmp_params = _scan.get_param_values_as_dict(filter_types_for_export=True)
        with open(filename, "w") as stream:
            yaml.safe_dump(tmp_params, stream)

    @classmethod
    def import_from_file(cls, filename: str, scan: Union[Scan, None] = None):
        """
        Restore the ScanContext from a YAML file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        scan : Union[None, pydidas.contexts.scan.Scan], optional
            The Scan instance to be updated. If None, the ScanContext instance is used.
            The default is None.
        """
        _scan = SCAN if scan is None else scan
        with open(filename, "r") as stream:
            try:
                cls.imported_params = yaml.safe_load(stream)
            except yaml.YAMLError as yerr:
                cls.imported_params = {}
                raise yaml.YAMLError from yerr
        assert isinstance(cls.imported_params, dict)
        cls._verify_all_entries_present()
        cls._write_to_scan_settings(scan=_scan)
