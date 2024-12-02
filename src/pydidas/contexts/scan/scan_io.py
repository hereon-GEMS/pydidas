# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with the ScanIo class which is used for creating
exporter/importer classes for the ScanContext singleton and registering them.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIo"]


from typing import Optional, TypeVar

from ...core.io_registry import GenericIoMeta
from ...core.utils.file_utils import get_extension


Scan = TypeVar("Scan")


class ScanIo(GenericIoMeta):
    """
    Metaclass for ScanContext exporters and importers.

    The ScanIo holds the registry with all associated file extensions
    for importing / exporting Scan (and ScanContexts).
    """

    # need to redefine the registry to have a unique registry for ScanIo
    registry = {}

    @classmethod
    def import_from_file(cls, filename: str, scan: Optional[Scan] = None):
        """
        Import a Scan from file and update the given Scan object.

        Call the concrete import_from_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : str
            The full filename and path.
        scan : Optional[Scan]
            The Scan object to be updated. If None, the generic ScanContext is used.
            The default is None.
        """
        _extension = get_extension(filename)
        cls.verify_extension_is_registered(_extension)
        _io_class = cls.registry[_extension]
        _io_class.import_from_file(filename, scan=scan)
