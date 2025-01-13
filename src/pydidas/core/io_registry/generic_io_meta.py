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
Module with the GenericIoMeta Metaclass which is used for creating
a registry of classes for a specific application.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GenericIoMeta"]


from pydidas.core.exceptions import UserConfigError
from pydidas.core.utils.file_utils import get_extension


class GenericIoMeta(type):
    """
    Metaclass for a class registry which holds associated classes for
    different file extension.
    """

    registry = {}

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
        _new_class = super(GenericIoMeta, cls).__new__(cls, clsname, bases, attrs)
        cls.register_class(_new_class)
        return _new_class

    @classmethod
    def clear_registry(cls):
        """
        Clear the registry and remove all items.
        """
        cls.registry = {}

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
        for _ext in new_class.extensions:
            if _ext in cls.registry and not update_registry:
                raise KeyError(
                    f"A class has already been registered for the extension {_ext}."
                )
            cls.registry[_ext] = new_class

    @classmethod
    def verify_extension_is_registered(cls, ext):
        """
        Verify the extension is registered with the MetaClass.

        Parameters
        ----------
        ext : str
            The file extension

        Raises
        ------
        TypeError
            If the extension is not registered.
        """
        if not cls.is_extension_registered(ext):
            _name = cls.__name__.removesuffix("Meta").removesuffix("Io")
            raise UserConfigError(
                f"The extension `{ext}` is not a registered extension for {_name}."
            )

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
        if extension in cls.registry:
            return True
        return False

    @classmethod
    def get_string_of_formats(cls):
        """
        Get a list of strings with the different formats and extensions.

        This class method is designed to have an easy way of creating the
        required lists for QFileDialog windows.

        Returns
        -------
        str
            The string entries for each format and one entry for all formats,
            each separated by a ";;".
        """
        _formats = cls.get_registered_formats()
        _extensions = [f"*.{_key}" for _key in cls.registry.keys()]
        _all = [f"All supported files ({' '.join(_extensions)})"] + [
            f"{name} (*.{' *.'.join(formats)})" for name, formats in _formats.items()
        ]
        return ";;".join(_all)

    @classmethod
    def get_registered_formats(cls):
        """
        Get the names of all registered formats and the corresponding
        file extensions.

        Returns
        -------
        dict
            A dictionary with <format name> : <extensions> entries.
        """
        _formats = {_cls.format_name: _cls.extensions for _cls in cls.registry.values()}
        return _formats

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
        _io_class = cls.registry[_extension]
        _io_class.export_to_file(filename, **kwargs)

    @classmethod
    def import_from_file(cls, filename):
        """
        Call the concrete import_from_file method in the subclass registered
        to the extension of the filename.

        Parameters
        ----------
        filename : str
            The full filename and path.
        """
        _extension = get_extension(filename, lowercase=False)
        cls.verify_extension_is_registered(_extension)
        _io_class = cls.registry[_extension]
        _io_class.import_from_file(filename)
