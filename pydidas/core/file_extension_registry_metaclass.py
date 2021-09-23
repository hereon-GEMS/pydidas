# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.
"""
Module with the RegistryMetaclass which is used for creating
a registry of classes for a specific application.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['FileExtensionRegistryMetaclass']


class FileExtensionRegistryMetaclass(type):
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
        _new_class = super(FileExtensionRegistryMetaclass, cls).__new__(
            cls, clsname, bases, attrs)
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
                raise KeyError('A class has already been registered for the '
                               f'extension "{_ext}."')
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
            raise KeyError(f'The extension "{ext}" is not registered with '
                           'the MetaClass.')

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
