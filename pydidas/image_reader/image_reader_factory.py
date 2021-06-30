# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with the ImageReaderFactory which returns always the same instance
of the ImageReader.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ImageReaderFactory']

import os
from ..core import SingletonFactory


class _ImageReaderFactory:
    """
    Factory to manage readers for different file types.
    """

    def __init__(self):
        self._readers = {}
        self._extensions = {}

    def register_format(self, filetype, ext, reader):
        """
        Register a new file type.

        This method registers new file types to the image reader and also
        maps the specified extensions to the file type and image reader.

        Note that file extensions will not be handled case-sensitive.

        Parameters
        ----------
        filetype : str
            The reference name of the filetype to register
        ext : list
            A list of string entries for the different extensions associated
            with this specific file type.
        reader : object
            The reader implementation class (not its instance! - The instance
            will be managed by the Builder).
        """
        self._readers[filetype] = SingletonFactory(reader)
        for ex in ext:
            self._extensions[ex] = filetype

    def get_reader(self, filename, **kwargs):
        """
        Get the reader associated with the filetype of filename.

        This method finds the ImageReader registered to the file extension
        of the input filename and returns the instance for reading the image.

        Parameters
        ----------
        filename : str
            The filename including the extension and the full path.

        Returns
        -------
        reader : ImageReader
            The instance of the ImageReader implementation.
        """
        _ext = os.path.splitext(filename)[1].lower()
        if not _ext in self._extensions.keys():
            raise ValueError(f'Extension "{_ext}" not supported.')
        reader = self._readers.get(self._extensions[_ext])
        if not reader:
            raise ValueError(f'Extension "{_ext}" not supported.')
        return reader(**kwargs)


class ImageReaderFactoryBuilder:
    """
    Builder class to prevent multiple instances of the _ImageReaderFactory to
    be created.
    """
    def __init__(self):
        """
        Initialization
        """
        self._instance = None

    def __call__(self, **kwargs):
        """
        Get the _ImageReaderFactory instance.

        If an instance of ImageReaderFactory exists, it is returned.
        If no instance exists yet, one is created and returned.

        Returns
        -------
        _ImageReaderFactory
            The class instance.
        """
        if not self._instance:
            self._instance = _ImageReaderFactory()
        return self._instance


ImageReaderFactory = ImageReaderFactoryBuilder()
