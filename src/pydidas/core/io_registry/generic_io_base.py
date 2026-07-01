# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GenericIoBase"]


from pathlib import Path
from typing import Any, ClassVar, Sequence

from pydidas.core.io_registry.generic_io_meta import GenericIoMeta


class GenericIoBase(metaclass=GenericIoMeta):
    """
    Base class for Metaclass-based importer/exporters.
    """

    extensions: ClassVar[list[str]] = []
    format_name: ClassVar[str] = ""

    @staticmethod
    def export_to_file(filename: Path | str, **kwargs: Any) -> None:
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        **kwargs : Any
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @classmethod
    def import_from_file(cls, filename: str | Path, **kwargs: Any) -> None:
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str or Path
            The filename of the file to be imported.
        **kwargs : Any
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @classmethod
    def import_from_file_sequence(
        cls, filenames: Sequence[Path | str], **kwargs: Any
    ) -> None:
        """
        Restore the content from a sequence of files.

        Parameters
        ----------
        filenames : Sequence[Path or str]
            The filenames of the files to be imported.
        **kwargs : Any
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError
