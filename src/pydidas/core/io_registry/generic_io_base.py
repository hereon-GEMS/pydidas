# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the GenericIoBase class which exporters/importers using the pydidas
metaclass-based registry should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GenericIoBase"]


import os

from pydidas.core.io_registry.generic_io_meta import GenericIoMeta


class GenericIoBase(metaclass=GenericIoMeta):
    """
    Base class for Metaclass-based importer/exporters.
    """

    extensions = []
    format_name = ""
    imported_params = {}

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        **kwargs : dict
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be imported.
        """
        raise NotImplementedError

    @classmethod
    def check_for_existing_file(cls, filename, **kwargs):
        """
        Check if the file exists and if the overwrite flag has been set.

        Parameters
        ----------
        filename : str
            The full filename and path.
        **kwargs : dict
            Any keyword arguments. Supported are:
        **overwrite : bool, optional
            Flag to allow overwriting of existing files.

        Raises
        ------
        FileExistsError
            If a file with filename exists and the overwrite flag is not True.
        """
        _overwrite = kwargs.get("overwrite", False)
        if os.path.exists(filename) and not _overwrite:
            raise FileExistsError(
                f"The file `{filename}` exists and overwriting has not been confirmed."
            )
