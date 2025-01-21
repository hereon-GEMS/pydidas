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
Module with the IoManager metaclass which stores references for all IO classes
and allows to get the importers/exporters based on the file extension.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["IoManager"]


from pathlib import Path
from typing import Literal, Union

import numpy as np

from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import get_extension


class IoManager(type):
    """
    Metaclass to manage imports and exporters for different file types.
    """

    registry_import = {}
    registry_export = {}

    def __new__(cls, clsname: str, bases: list[type], attrs: dict):
        """
        Call the class' (i.e. the WorkflowTree exporter) __new__ method
        and register the class with the registry.

        Parameters
        ----------
        clsname : str
            The name of the new class
        bases : list[type]
            The list of class bases.
        attrs : dict
            The class attributes.

        Returns
        -------
        type
            The new class.
        """
        _new_class = super(IoManager, cls).__new__(cls, clsname, bases, attrs)
        cls.register_class(_new_class)
        return _new_class

    @classmethod
    def register_class(cls, new_class: type, update_registry: bool = False):
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
        for _ext in new_class.extensions_export:
            if _ext in cls.registry_export and not update_registry:
                raise KeyError(
                    "An export class has already been registered "
                    f'for the extension "{_ext}."'
                )
            cls.registry_export[_ext] = new_class
        for _ext in new_class.extensions_import:
            if _ext in cls.registry_import and not update_registry:
                raise KeyError(
                    "An import class has already been registered "
                    f'for the extension "{_ext}."'
                )
            cls.registry_import[_ext] = new_class

    @classmethod
    def clear_registry(cls):
        """
        Clear the registry and remove all items.
        """
        cls.registry_import = {}
        cls.registry_export = {}

    @classmethod
    def verify_extension_is_registered(
        cls,
        ext: str,
        mode: Literal["import", "export"] = "import",
        filename: Union[str, None] = None,
    ):
        """
        Verify the extension is registered with the MetaClass.

        Parameters
        ----------
        ext : str
            The file extension
        mode : str[import, export], optional
            The mode to use: Choose between import and export. The default is
            import.
        filename : Union[None, str]
            The filename of the file to be checked.

        Raises
        ------
        UserConfigError
            If the extension is not registered.
        """
        if not cls.is_extension_registered(ext, mode=mode):
            if ext == "":
                raise UserConfigError(
                    f"No extension has been selected for data {mode}. Please set an "
                    "extension to choose a fileformat."
                    + ("" if filename is None else f" (filename: {filename})")
                )
            raise UserConfigError(
                f'The extension "{ext}" is not registered for data input/output.'
            )

    @classmethod
    def is_extension_registered(
        cls, extension: str, mode: Literal["import", "export"] = "import"
    ):
        """
        Check if the extension of filename corresponds to a registered class.

        The extension is stored without the leading dot. If the given extension
        includes a leading dot, it is stripped before checking the extension.
        This behaviour allows to use pathlib.Path instances' suffix property to
        be used directly.

        Parameters
        ----------
        extension : str
            The extension to be checked. If the extension includes a leading
            dot, it is stripped.
        mode : Literal["import", "export"]
            The mode to use: Choose between import and export. The default is
            import.
        Returns
        -------
        bool
            Flag whether the extension is registered or not.
        """
        if extension.startswith("."):
            extension = extension[1:]
        if extension in cls._get_registry(mode):
            return True
        return False

    @classmethod
    def _get_registry(cls, mode: Literal["import", "export"]):
        """
        Get the registry for the selected mode.

        Parameters
        ----------
        mode : Literal["import", "export"]
            The mode. Must be one of import or export.

        Raises
        ------
        ValueError
            If the mode is not import or export.

        Returns
        -------
        _reg : dict
            The selected registry, based on the mode.
        """
        if mode == "import":
            _reg = cls.registry_import
        elif mode == "export":
            _reg = cls.registry_export
        else:
            raise ValueError('The "mode" must be either import or export.')
        return _reg

    @classmethod
    def get_string_of_formats(cls, mode: Literal["import", "export"] = "import"):
        """
        Get a list of strings with the different formats and extensions.

        This class method is designed to have an easy way of creating the
        required lists for QFileDialog windows.

        Parameters
        ----------
        mode : Literal["import", "export"]
            The mode to use: Choose between import and export. The default is
            import.

        Returns
        -------
        str
            The string entries for each format and one entry for all formats,
            each separated by a ";;".
        """
        _formats = cls.get_registered_formats(mode=mode)
        _extensions = [f"*.{_key}" for _key in cls._get_registry(mode)]
        _all = [f"All supported files ({' '.join(_extensions)})"] + [
            f"{_name} files (*.{' *.'.join(_ext)})" for _name, _ext in _formats.items()
        ]
        return ";;".join(_all)

    @classmethod
    def get_registered_formats(cls, mode: Literal["import", "export"] = "import"):
        """
        Get the names and file extensins of all registered formats.

        Parameters
        ----------
        mode : Literal["import", "export"]
            The mode to use: Choose between import and export. The default is
            import.

        Returns
        -------
        dict
            A dictionary with <format name> : <extensions> entries.
        """
        if mode == "import":
            _reg = cls.registry_import
            _formats = {
                _class.format_name: _class.extensions_import for _class in _reg.values()
            }
        elif mode == "export":
            _reg = cls.registry_export
            _formats = {
                _class.format_name: _class.extensions_export for _class in _reg.values()
            }
        else:
            raise ValueError('The "mode" must be either import or export.')
        return _formats

    @classmethod
    def export_to_file(
        cls, filename: Union[Path, str], data: np.ndarray, **kwargs: dict
    ):
        """
        Export the data to file using the exporter based on the extension.

        Parameters
        ----------
        filename : str
            The full filename and path.
        data : np.ndarray
            The data to be exported.
        **kwargs : dict
            Any kwargs which should be passed to the underlying exporter.
        """
        _extension = get_extension(filename)
        cls.verify_extension_is_registered(_extension, mode="export")
        _io_class = cls.registry_export[_extension]
        _io_class.export_to_file(filename, data, **kwargs)

    @classmethod
    def import_from_file(cls, filename: Union[Path, str], **kwargs: dict) -> Dataset:
        """
        Import data from a file, using the importer based on the extension.

        Parameters
        ----------
        filename : Union[Path, str]
            The full filename and path.
        **kwargs : dict
            Keyword arguments for the concrete importer implementation call.

        Returns
        -------
        pydidas.core.Dataset
            The imported Dataset.
        """
        _extension = get_extension(filename)
        cls.verify_extension_is_registered(_extension, mode="import", filename=filename)
        _io_class = cls.registry_import[_extension]
        _data = _io_class.import_from_file(filename, **kwargs)
        _forced_dim = kwargs.get("forced_dimension", None)
        if _forced_dim is not None and _forced_dim != _data.ndim:
            raise UserConfigError(
                f"The imported data has {_data.ndim} dimensions, but an input of "
                f"dimensionality {kwargs.get('forced_dimension')} is required. Please "
                "control the given input and configuration."
            )
        return _data
