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
Module with the ScanIo class which is used for creating
exporter/importer classes for the ScanContext singleton and registering them.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ScanIo"]


from typing import Optional, TypeVar

from pydidas.core import UserConfigError
from pydidas.core.io_registry import GenericIoMeta
from pydidas.core.utils.file_utils import get_extension


Scan = TypeVar("Scan")


class ScanIo(GenericIoMeta):
    """
    Metaclass for ScanContext exporters and importers.

    The ScanIo holds the registry with all associated file extensions
    for importing / exporting Scan (and ScanContexts).
    """

    # need to redefine the registry to have a unique registry for ScanIo
    registry = {}
    beamline_format_registry = {}

    @classmethod
    def register_class(cls, new_class, update_registry=False):
        """
        Register a class as object for its native extensions.

        Parameters
        ----------
        new_class : type
            The class to be registered.
        update_registry : bool, optional
            Keyword to allow updating / overwriting of registered extensions.
            The default is False.

        Raises
        ------
        KeyError
            If an extension associated with new_class has already been
            registered and update_registry is False.
        """
        _ref_registry = (
            cls.beamline_format_registry
            if getattr(new_class, "beamline_format", False)
            else cls.registry
        )
        for _ext in new_class.extensions:
            if _ext in _ref_registry and not update_registry:
                raise KeyError(
                    f"A class has already been registered for the extension {_ext}."
                )
            _ref_registry[_ext] = new_class

    @classmethod
    def clear_registry(cls):
        """
        Clear the registry and remove all items.
        """
        cls.registry = {}
        cls.beamline_format_registry = {}

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
        _io_class = cls.get_io_class(filename)
        _io_class.import_from_file(filename, scan=scan)

    @classmethod
    def get_io_class(cls, filename: str):
        """
        Get the IO class for a given filename.

        Parameters
        ----------
        filename : str
            The filename with extension.

        Returns
        -------
        type
            The IO class.
        """
        _extension = get_extension(filename)
        cls.verify_extension_is_registered(_extension)
        if _extension in cls.registry:
            return cls.registry[_extension]
        elif _extension in cls.beamline_format_registry:
            return cls.beamline_format_registry[_extension]

    @classmethod
    def import_from_multiple_files(cls, filenames: list[str], **kwargs: dict):
        """
        Import a Scan from multiple files and update the given Scan object.

        Parameters
        ----------
        filenames : list[str]
            The list of full filenames and paths.
        **kwargs : dict
            Any kwargs which should be passed to the underlying importer.
            Supported kwargs are:

            scan : Optional[Scan]
                The Scan object to be updated. If None, the generic ScanContext is used.
                The default is None.
            scan_dim0_motor : Optional[str]
                The motor name for the first dimension. The default is None.
        """
        _extensions = set([get_extension(_filename) for _filename in filenames])
        if len(_extensions) > 1:
            raise UserConfigError(
                "All files must have the same extension for batch import."
            )
        _io_class = cls.get_io_class(filenames[0])
        _io_class.import_from_file(filenames, **kwargs)

    @classmethod
    def check_multiple_files(cls, filenames: list[str], **kwargs: dict) -> list[str]:
        """
        Check whether a selection of multiple files can be imported.

        Parameters
        ----------
        filenames : list[str]
            The list of full filenames and paths.
        **kwargs : dict
            Any kwargs which should be passed to the underlying importer.
            Supported kwargs are:

            scan : Optional[Scan]
                The Scan object to be updated. If None, the generic ScanContext is used.
                The default is None.

        Returns
        -------
        list[str]
            A coded message about whether the files can be imported and additional
            information.
        """
        _extensions = set([get_extension(_filename) for _filename in filenames])
        if len(_extensions) > 1:
            raise UserConfigError(
                "All files must have the same extension for batch import."
            )
        _io_class = cls.get_io_class(filenames[0])
        _result = _io_class.check_file_list(filenames, **kwargs)
        return _result

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Call the concrete export_to_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : str
            The full filename and path.
        tree : pydidas.workflow.WorkflowTree
            The instance of the WorkflowTree
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        _extension = get_extension(filename, lowercase=False)
        cls.verify_extension_is_registered(_extension)
        if _extension in cls.registry:
            _io_class = cls.registry[_extension]
        elif _extension in cls.beamline_format_registry:
            _io_class = cls.beamline_format_registry[_extension]
        if _io_class.import_only:
            raise UserConfigError(
                f"The extension `{_extension}` is only registered for import."
            )
        _io_class.export_to_file(filename, **kwargs)

    @classmethod
    def is_extension_registered(cls, extension):
        """
        Check if the extension of filename corresponds to a registered
        class.

        Parameters
        ----------
        extension : str
            The extension to be checked.

        Returns
        -------
        bool
            Flag whether the extension is registered or not.
        """
        if extension in cls.registry or extension in cls.beamline_format_registry:
            return True
        return False

    @classmethod
    def get_string_of_beamline_formats(cls):
        """
        Get a list of strings with the different beamline formats and extensions.

        This class method is designed to have an easy way of creating the
        required lists for QFileDialog windows.

        Returns
        -------
        str
            The string entries for each format and one entry for all formats,
            each separated by a ";;".
        """
        _formats = {
            _cls.format_name: _cls.extensions
            for _cls in cls.beamline_format_registry.values()
        }
        _extensions = [f"*.{_key}" for _key in cls.beamline_format_registry.keys()]
        _all = [f"All supported files ({' '.join(_extensions)})"] + [
            f"{name} (*.{' *.'.join(formats)})" for name, formats in _formats.items()
        ]
        return ";;".join(_all)
