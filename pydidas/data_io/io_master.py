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
Module with the IOmaster metaclass which stores references for all IO classes
and allows to get the importers/exporters based on the file extension.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["IoMaster"]

import os


class IoMaster(type):
    """
    Metaclass to manage imports and exporters for different file types.
    """

    registry_import = {}
    registry_export = {}

    def __new__(cls, clsname, bases, attrs):
        """
        Call the class' (i.e. the WorkflowTree exporter) __new__ method
        and register the class with the registry.

        Parameters
        ----------
        cls : type
            The new class.
        clsname : str
            The name of the new class
        bases : list
            The list of class bases.
        attrs : dict
            The class attributes.

        Returns
        -------
        type
            The new class.
        """
        _new_class = super(IoMaster, cls).__new__(cls, clsname, bases, attrs)
        cls.register_class(_new_class)
        return _new_class

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
    def verify_extension_is_registered(cls, ext, mode="import"):
        """
        Verify the extension is registered with the MetaClass.

        Parameters
        ----------
        ext : str
            The file extension
        mode : str[import, export]
            The mode to use: Choose between import and export. The default is
            import.

        Raises
        ------
        TypeError
            If the extension is not registered.
        """
        if not cls.is_extension_registered(ext, mode=mode):
            raise KeyError(
                f'The extension "{ext}" is not registered with ' "the MetaClass."
            )

    @classmethod
    def is_extension_registered(cls, extension, mode="import"):
        """
        Check if the extension of filename corresponds to a registered
        class.

        Parameters
        ----------
        extension : str
            The extension to be checked.
        mode : str[import, export]
            The mode to use: Choose between import and export. The default is
            import.
        Returns
        -------
        bool
            Flag whether the extension is registered or not.
        """
        if extension in cls._get_registry(mode):
            return True
        return False

    @classmethod
    def _get_registry(cls, mode):
        """
        Get the registry for the selected mode.

        Parameters
        ----------
        mode : str[import, export]
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
    def get_string_of_formats(cls, mode="import"):
        """
        Get a list of strings with the different formats and extensions.

        This class method is designed to have an easy way of creating the
        required lists for QFileDialog windows.

        Parameters
        ----------
        mode : str[import, export]
            The mode to use: Choose between import and export. The default is
            import.

        Returns
        -------
        str
            The string entries for each format and one entry for all formats,
            each separated by a ";;".
        """
        _formats = cls.get_registered_formats(mode=mode)
        _extensions = list(cls._get_registry(mode).keys())
        _all = [f'All supported files (*{" *".join(_extensions)})'] + [
            f'{name} (*{" *".join(formats)})' for name, formats in _formats.items()
        ]
        return ";;".join(_all)

    @classmethod
    def get_registered_formats(cls, mode="import"):
        """
        Get the names of all registered formats and the corresponding
        file extensions.

        Parameters
        ----------
        mode : str[import, export]
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
    def export_to_file(cls, filename, data, **kwargs):
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
        _extension = os.path.splitext(filename)[1]
        cls.verify_extension_is_registered(_extension, mode="export")
        _io_class = cls.registry_export[_extension]
        _io_class.export_to_file(filename, data, **kwargs)

    @classmethod
    def import_from_file(cls, filename, **kwargs):
        """
        Call the concrete import_from_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : str
            The full filename and path.

        Returns
        -------
        pydidas.workflow.WorkflowTree
            The new WorkflowTree instance.
        """
        _extension = os.path.splitext(filename)[1]
        cls.verify_extension_is_registered(_extension, mode="import")
        _io_class = cls.registry_import[_extension]
        return _io_class.import_from_file(filename, **kwargs)
